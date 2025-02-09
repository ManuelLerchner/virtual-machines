from __future__ import annotations
from pyparsing import *
import string
from abc import abstractmethod
from typing import TYPE_CHECKING, List, Union
from collections import defaultdict

from Instructions import Instructions1Params, bcolors

if TYPE_CHECKING:
    from Instructions import Instructions

from time import sleep


class Stack:
    def __init__(self):
        self.stack: dict[int, int] = defaultdict(lambda: "_")
        self.SP: int = -1

    def __getitem__(self, key: int) -> int:
        return self.stack[key]

    def __setitem__(self, key: int, value: int):
        self.stack[key] = value

    def to_list(self) -> list[int]:
        return [self.stack[i] for i in range(self.SP+1)]

    def __repr__(self):
        return str(self.to_list())


class HeapElement:
    @abstractmethod
    def __init__(self, heap: Heap, tag: str,):
        self.heap = heap
        self.tag = tag

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def get_references_rec(self, seen):
        pass


class BaseHeapElement(HeapElement):
    def __init__(self, heap, value: int):
        super().__init__(heap, "B")
        self.value = value

    def __repr__(self):
        return f"{bcolors.OKRED+ str(self.tag)+bcolors.ENDC} V:{self.value}"

    def get_references_rec(self, seen):
        return set()


class ClosureHeapElement(HeapElement):
    def __init__(self, heap, closurePtr: int, globPtr: int):
        super().__init__(heap, "C")
        self.closurePtr = closurePtr
        self.globPtr = globPtr

    def __repr__(self):
        return f"{bcolors.OKRED+ str(self.tag)+bcolors.ENDC} CLSRPTR:{bcolors.OKYELLOW+ str(self.closurePtr)+bcolors.ENDC} GLBPTR:{bcolors.OKYELLOW+str(self.globPtr)+bcolors.ENDC}"

    def get_references_rec(self, seen):
        if self.globPtr in seen:
            return set()
        else:
            seen.add(self.globPtr)
            return {self.globPtr}.union(self.heap[self.globPtr].get_references_rec(seen))


class FunctionHeapElement(HeapElement):
    def __init__(self, heap, codePtr: int, argPtr: int, globPtr: int):
        super().__init__(heap, "F")
        self.codePtr = codePtr
        self.argPtr = argPtr
        self.globPtr = globPtr

    def __repr__(self):
        return f"{bcolors.OKRED+ str(self.tag)+bcolors.ENDC} CP:{self.codePtr} ARGP:{bcolors.OKYELLOW+ str(self.argPtr)+bcolors.ENDC} GLBPTR:{bcolors.OKYELLOW+str(self.globPtr)+bcolors.ENDC}"

    def get_references_rec(self, seen):
        if self.globPtr in seen:
            return set()
        else:
            seen.add(self.globPtr)
            return {self.globPtr, self.argPtr}.union(self.heap[self.globPtr].get_references_rec(seen)).union(self.heap[self.argPtr].get_references_rec(seen))


class VectorHeapElement(HeapElement):
    def __init__(self, heap, size: int):
        super().__init__(heap, "V")
        self.size = size
        self.elements = [None]*size

    def __getitem__(self, key: int) -> int:
        return self.elements[key]

    def __setitem__(self, key: int, value: int):
        self.elements[key] = value

    def __repr__(self):
        return f"{bcolors.OKRED+ str(self.tag)+bcolors.ENDC} N:{self.size} ITMS:{self.elements}"

    def get_references_rec(self, seen):
        s = set()
        for i in range(self.size):
            if self.elements[i] in seen:
                return set()
            else:
                seen.add(self.elements[i])
                s.union(self.heap[self.elements[i]].get_references_rec(seen))
        return s


class EmptyListHeapElement(HeapElement):
    def __init__(self, heap):
        super().__init__(heap, "LNIL")

    def __repr__(self):
        return f"{bcolors.OKRED+ str(self.tag)+bcolors.ENDC}"

    def get_references_rec(self, seen):
        return set()


class ConsHeapElement(HeapElement):
    def __init__(self, heap, head: int, tail: int):
        super().__init__(heap, "LCONS")
        self.head = head
        self.tail = tail

    def __repr__(self):
        return f"{bcolors.OKRED+ str(self.tag)+bcolors.ENDC} H:{self.head} T:{self.tail}"

    def get_references_rec(self, seen):
        if not self.head in seen:
            seen.add(self.head)
            self.heap[self.head].get_references_rec(seen)
        if not self.tail in seen:
            seen.add(self.tail)
            self.heap[self.tail].get_references_rec(seen)
        return seen


class Heap:

    def __init__(self):
        self.heap: dict[int, HeapElement] = {}
        self.currentAddress = 100

    def __getitem__(self, key: int) -> int:
        if (key == -1):
            # dummy value
            return BaseHeapElement(self, 0)

        return self.heap[key]

    def __setitem__(self, key: int, element: HeapElement):
        self.heap[key] = element

    def alloc(self, type: str, *args):

        element = None
        if type == "B":
            element = BaseHeapElement(self, *args)
        elif type == "C":
            element = ClosureHeapElement(self, *args)
        elif type == "F":
            element = FunctionHeapElement(self, *args)
        elif type == "V":
            element = VectorHeapElement(self, *args)
        elif type == "LNIL":
            element = EmptyListHeapElement(self)
        elif type == "LCONS":
            element = ConsHeapElement(self, *args)
        else:
            raise Exception("Unknown type")

        addr = self.currentAddress
        self.heap[addr] = element
        self.currentAddress += 1
        return addr

    def collect_garbage(self, stack: Stack):
        reachable = set()
        for i in range(stack.SP+1):
            if stack[i] in self.heap:
                reachable.add(stack[i])
                reachable = reachable.union(
                    self.heap[stack[i]].get_references_rec(reachable))

        for key in list(self.heap.keys()):
            if key not in reachable:
                del self.heap[key]

    def __repr__(self):
        return " ".join([f'[{bcolors.OKWHITE+ str(add)+bcolors.ENDC}: {e}]' for (add, e) in self.heap.items()])


def get_label_positions(code):
    jump_targets = {}
    for i, instruction in enumerate(code):
        if instruction.instruction == Instructions1Params.I.JUMP_TARGET:
            jump_targets[instruction.param1] = i
    return jump_targets


def uncolor(str):
    ESC = Literal('\x1b')
    integer = Word(nums)
    escapeSeq = Combine(ESC + '[' + Optional(delimitedList(integer, ';')) +
                        oneOf(list(alphas)))

    def nonAnsiString(s): return Suppress(escapeSeq).transformString(str)

    return nonAnsiString(str)


class Interpreter:
    def __init__(self, code: list[Instructions]):
        self.stack: Stack = Stack()
        self.heap: Heap = Heap()
        self.code = code
        self.jumpLabels = get_label_positions(code)
        self.PC: int = 0
        self.FP: int = -1
        self.GP: int = -1

    def run(self, debug=False, pretty=False):
        print("Running...\n\n")

        step = 0
        while True:
            if self.PC >= len(self.code):
                break
            IR = self.code[self.PC]

            self.PC += 1
            IR.interpret(self)

            if debug:
                real_ir_length = len(uncolor(str(IR)))

                registers = f"PC: {self.PC: > 5}, SP: {self.stack.SP: > 5}, FP: {self.FP: > 5}, GP: {self.GP: > 5}"
                print(f"Stack:\t{self.stack}")
                print(f"Heap:\t{self.heap}")
                print(
                    f"Instruction: {str(IR)+' ' * (18 - real_ir_length)} {bcolors.OKBLUE +str(IR.description()) + bcolors.ENDC}")
                print(registers)
                print()

            if step % 10 == 0:
                # self.heap.collect_garbage(self.stack)
                pass

            step += 1

        self.heap.collect_garbage(self.stack)

        print(f"\n\nExecution finished in {step} steps")
        print(f"Heap Size: {len(self.heap.heap)}")
