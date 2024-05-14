from __future__ import annotations
from pyparsing import *
import string
from abc import abstractmethod
from typing import TYPE_CHECKING, Union
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
    def get_references(self):
        pass


class BaseHeapElement(HeapElement):
    def __init__(self, heap, value: int):
        super().__init__(heap, "B")
        self.value = value

    def __repr__(self):
        return f"{bcolors.OKRED+ str(self.tag)+bcolors.ENDC} V:{self.value}"

    def get_references(self):
        return []


class ClosureHeapElement(HeapElement):
    def __init__(self, heap, closurePtr: int, globPtr: int):
        super().__init__(heap, "C")
        self.closurePtr = closurePtr
        self.globPtr = globPtr

    def __repr__(self):
        return f"{bcolors.OKRED+ str(self.tag)+bcolors.ENDC} CLSRPTR:{bcolors.OKYELLOW+ str(self.closurePtr)+bcolors.ENDC} GLBPTR:{bcolors.OKYELLOW+str(self.globPtr)+bcolors.ENDC}"

    def get_references(self):
        return [self.closurePtr, self.globPtr]


class FunctionHeapElement(HeapElement):
    def __init__(self, heap, codePtr: int, argPtr: int, globPtr: int):
        super().__init__(heap, "F")
        self.codePtr = codePtr
        self.argPtr = argPtr
        self.globPtr = globPtr

    def __repr__(self):
        return f"{bcolors.OKRED+ str(self.tag)+bcolors.ENDC} CP:{self.codePtr} ARGP:{bcolors.OKYELLOW+ str(self.argPtr)+bcolors.ENDC} GLBPTR:{bcolors.OKYELLOW+str(self.globPtr)+bcolors.ENDC}"

    def get_references(self):
        return [self.argPtr, self.globPtr]


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

    def get_references(self):
        return self.elements


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
        else:
            raise Exception("Unknown type")

        addr = self.currentAddress
        self.heap[addr] = element
        self.currentAddress += 1
        return addr

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

            # self.heap.collect_garbage()

            if debug:
                # sleep(0.001)
                real_ir_length = len(uncolor(str(IR)))
                registers = f"IR: {str(IR)+' ' * (18 - real_ir_length)} PC: {self.PC: > 5}, SP: {self.stack.SP: > 5}, FP: {self.FP: > 5}, GP: {self.GP: > 5}"
                if pretty:
                    clear = '\33[2K'
                    print(f"\r{clear}", end="")
                    print(registers)
                    print(f"\r{clear}", end="")
                    print(f"\tStack:\t{self.stack}")
                    print(f"\r{clear}", end="")
                    print(f"\tHeap:\t{self.heap}", end="\r")
                    print("\033[2A", end="")
                else:
                    # sleep(1)

                    print(registers)
                    print(f"\tStack:\t{self.stack}")
                    print(f"\tHeap:\t{self.heap}")

            step += 1

        print(f"\n\nExecution finished in {step} steps")
        print(f"Heap Size: {len(self.heap.heap)}")
