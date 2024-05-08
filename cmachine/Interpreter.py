from __future__ import annotations
from typing import TYPE_CHECKING
from collections import defaultdict

from Instructions import Instructions1Params

if TYPE_CHECKING:
    from Instructions import Instructions

from time import sleep


class Stack:
    def __init__(self):
        self.stack: dict[int, int] = defaultdict(lambda: "_")
        self.SP: int = -1
        self.NP = 10000
        self.EP = -1
        self.FP = -1

    def __getitem__(self, key: int) -> int:
        return self.stack[key]

    def __setitem__(self, key: int, value: int):
        self.stack[key] = value

    def to_list(self) -> list[int]:
        return [self.stack[i] for i in range(self.SP+1)]

    def __repr__(self):
        return str(self.to_list())


def get_label_positions(code):
    jump_targets = {}
    for i, instruction in enumerate(code):
        if instruction.instruction == Instructions1Params.I.JUMP_TARGET:
            jump_targets[instruction.param1] = i
    return jump_targets


class Interpreter:
    def __init__(self, code: list[Instructions]):
        self.stack: Stack = Stack()
        self.code = code
        self.jumpLabels = get_label_positions(code)
        self.PC: int = 0

    def run(self, debug=False):
        step = 0
        while True:
            if self.PC >= len(self.code):
                break
            IR = self.code[self.PC]

            self.PC += 1
            IR.interpret(self)

            if debug:
                sleep(0.1)
                clear = '\33[2K'
                print(f"\r{clear}", end="")
                print(
                    f"IR: {str(IR):>15} PC: {self.PC:>5}, SP: {self.stack.SP:>5}, EP: {self.stack.EP:>5}, FP: {self.stack.FP:>5} Stack: {self.stack}", end="", flush=True)

            step += 1

        print(f"\nExecution finished in {step} steps")
