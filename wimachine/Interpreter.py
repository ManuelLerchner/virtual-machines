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

    @abstractmethod
    def pretty_print(self, adress):
        pass


class AtomHeapElement(HeapElement):
    def __init__(self, heap, a: int):
        super().__init__(heap, "A")
        self.a = a

    def __repr__(self):
        return f"{bcolors.OKRED+ str(self.tag)+bcolors.ENDC} V:{self.a}"

    def get_references_rec(self, seen):
        return set()

    def pretty_print(self, adress):
        return f"{self.a}"


class RefHeapElement(HeapElement):
    def __init__(self, heap, value: int):
        super().__init__(heap, "R")
        self.value = value

    def __repr__(self):
        return f"{bcolors.OKRED+ str(self.tag)+bcolors.ENDC} V:{self.value}"

    def get_references_rec(self, seen):
        return set()

    def pretty_print(self, adress):
        if self.value == adress:
            return f"_"
        else:
            return self.heap[self.value].pretty_print(self.value)


class StructHeapElement(HeapElement):
    def __init__(self, heap, f: int, n: int):
        super().__init__(heap, "S")
        self.f = f
        self.n = n

    def __repr__(self):
        return f"{bcolors.OKRED+ str(self.tag)+bcolors.ENDC} F:{self.f} N:{self.n}"

    def get_references_rec(self, seen):
        return set()

    def pretty_print(self, adress):
        name = f"{self.f}"
        children = []
        for i in range(self.n):
            child_address = self.heap[adress+i+1]
            children.append(
                self.heap[child_address].pretty_print(child_address))

        if name == "NIL":
            return f"{bcolors.OKYELLOW}[]{bcolors.ENDC}"
        if name == "CONS":
            return f"{bcolors.OKYELLOW}[{bcolors.ENDC}{children[0]}{bcolors.OKYELLOW}|{bcolors.ENDC}{children[1]}{bcolors.OKYELLOW}]{bcolors.ENDC}"

        return f"{name}({', '.join(children)})"


class Heap:

    def __init__(self):
        self.stack: dict[int, HeapElement] = defaultdict(lambda: "_")
        self.HP = 0

    def __getitem__(self, key: int) -> int:
        return self.stack[key]

    def __setitem__(self, key: int, element: HeapElement):
        self.stack[key] = element

    def makeElement(self, type: str, *args):

        element = None
        if type == "A":
            element = AtomHeapElement(self, args[0])
        elif type == "R":
            element = RefHeapElement(self, args[0])
        elif type == "S":
            name = args[0]
            [f, n] = name.split("/")
            n = int(n)
            element = StructHeapElement(self, f, n)
        else:
            raise Exception("Unknown type " + type)

        return element

    def __repr__(self):
        return " ".join([f'[{bcolors.OKWHITE+ str(add)+bcolors.ENDC}: {e}]' for (add, e) in self.stack.items()])

    def pretty_print(self, startAddress: int):
        return self[startAddress].pretty_print(startAddress)


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
        self.trail: Stack = Stack()
        self.code = code
        self.jumpLabels = get_label_positions(code)
        self.PC: int = 0
        self.FP: int = -1
        self.BP: int = -1

    def run(self, debug=False, pretty=False):
        print("Running...\n\n")

        step = 0
        while True:
            if self.PC >= len(self.code):
                break
            IR = self.code[self.PC]

            if debug:
                # sleep(0.001)
                real_ir_length = len(uncolor(str(IR)))
                registers = f"IR: {str(IR)+' ' * (18 - real_ir_length)} PC: {self.PC: > 5}, SP: {self.stack.SP: > 5}, FP: {self.FP: > 5}, BP: {self.BP: > 5}"
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

                    print(f"Stack:\t{self.stack}")
                    print(f"Heap:\t{self.heap}")
                    print(registers)
                    print()

            self.PC += 1
            IR.interpret(self)

            step += 1

        print(f"\n\nExecution finished in {step} steps")
