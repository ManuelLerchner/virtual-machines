from __future__ import annotations
from typing import TYPE_CHECKING
from collections import defaultdict

from Instructions import Instructions1Params

if TYPE_CHECKING:
    from Instructions import Instructions


class Stack:
    def __init__(self):
        self.stack: dict[int, int] = defaultdict(lambda: "_")
        self.SP: int = -1
        self.NP = 10000
        self.EP = 5000

    def __getitem__(self, key: int) -> int:
        return self.stack[key]

    def __setitem__(self, key: int, value: int):
        self.stack[key] = value

    def to_list(self) -> list[int]:
        return [self.stack[i] for i in range(self.SP+1)]

    def __repr__(self):
        return str(self.to_list())

    def initVariables(self, variable_adress: dict[str, int], variable_values: dict[str, int]):
        for [name, adress] in variable_adress.items():
            self[adress] = variable_values[name]


def get_label_positions(code):
    jump_targets = {}
    for i, instruction in enumerate(code):
        if instruction.instruction == Instructions1Params.I.JUMP_TARGET:
            jump_targets[instruction.param1] = i
    return jump_targets


class State:
    def __init__(self, code: list[Instructions]):
        self.stack: Stack = Stack()
        self.code = code
        self.jumpLabels = get_label_positions(code)
        self.PC: int = 0

    def run(self, debug=False):
        if debug:
            print(f"Code: {self.code}\n")

        step = 0
        while True:
            if self.PC >= len(self.code):
                break
            IR = self.code[self.PC]
            if debug:
                print(
                    f"About to interpret: PC: {self.PC}, IR: {IR}, SP: {self.stack.SP}")

            self.PC += 1
            IR.interpret(self)

            if debug:
                print(f"Resulting stack:\n{self.stack}\n")
            step += 1

        if debug:
            print(f"Execution finished in {step} steps")
