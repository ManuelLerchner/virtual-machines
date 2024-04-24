from __future__ import annotations
from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from State import State


class Instructions:

    def __init__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def interpret(self, state: State):
        pass


class Instructions0Params(Instructions):

    class I(Enum):
        ADD = "add"
        SUB = "sub"
        MUL = "mul"
        DIV = "div"
        LEQ = "leq"
        GEQ = "geq"
        LT = "lt"
        GT = "gt"
        EQ = "eq"
        NEG = "neg"
        NOT = "not"
        LOAD = "load"
        STORE = "store"
        POP = "pop"
        PRINT = "print"

    def __init__(self, instruction: I):
        self.instruction = instruction

    def __repr__(self):
        return f"{self.instruction.value}"

    def interpret(self, state: State):
        S = state.stack
        if self.instruction == Instructions0Params.I.ADD:
            S.SP -= 1
            S[S.SP] = S[S.SP] + S[S.SP + 1]
        elif self.instruction == Instructions0Params.I.SUB:
            S.SP -= 1
            S[S.SP] = S[S.SP] - S[S.SP + 1]
        elif self.instruction == Instructions0Params.I.MUL:
            S.SP -= 1
            S[S.SP] = S[S.SP] * S[S.SP + 1]
        elif self.instruction == Instructions0Params.I.DIV:
            S.SP -= 1
            S[S.SP] = S[S.SP] // S[S.SP + 1]
        elif self.instruction == Instructions0Params.I.LEQ:
            S.SP -= 1
            S[S.SP] = 1 if S[S.SP] <= S[S.SP + 1] else 0
        elif self.instruction == Instructions0Params.I.GEQ:
            S.SP -= 1
            S[S.SP] = 1 if S[S.SP] >= S[S.SP + 1] else 0
        elif self.instruction == Instructions0Params.I.LT:
            S.SP -= 1
            S[S.SP] = 1 if S[S.SP] < S[S.SP + 1] else 0
        elif self.instruction == Instructions0Params.I.GT:
            S.SP -= 1
            S[S.SP] = 1 if S[S.SP] > S[S.SP + 1] else 0
        elif self.instruction == Instructions0Params.I.EQ:
            S.SP -= 1
            S[S.SP] = 1 if S[S.SP] == S[S.SP + 1] else 0
        elif self.instruction == Instructions0Params.I.NEG:
            S[S.SP] = -S[S.SP]
        elif self.instruction == Instructions0Params.I.NOT:
            S[S.SP] = 1 if S[S.SP] == 0 else 0
        elif self.instruction == Instructions0Params.I.PRINT:
            print(S[S.SP])
        elif self.instruction == Instructions0Params.I.LOAD:
            S[S.SP] = S[S[S.SP]]
        elif self.instruction == Instructions0Params.I.STORE:
            S[S[S.SP]] = S[S.SP-1]
            S.SP -= 1
        elif self.instruction == Instructions0Params.I.POP:
            S.SP -= 1
        else:
            raise Exception("Unknown instruction")


class Instructions1Params(Instructions):

    class I(Enum):
        LOADC = "LOADC"
        JUMP = "JUMP"
        JUMPZ = "JUMPZ"
        JUMP_TARGET = "JUMP_TARGET"
        ALLOC = "ALLOC"

    def __init__(self, instruction: I, param1):
        self.instruction = instruction
        self.param1 = param1

    def __repr__(self):
        return f"{self.instruction.value} {self.param1}"

    def interpret(self, state: State):
        S = state.stack
        if self.instruction == Instructions1Params.I.LOADC:
            S.SP += 1
            S[S.SP] = self.param1
        elif self.instruction == Instructions1Params.I.JUMP:
            state.PC = state.jumpLabels[self.param1]
        elif self.instruction == Instructions1Params.I.JUMPZ:
            if S[S.SP] == 0:
                state.PC = state.jumpLabels[self.param1]
            S.SP -= 1
        elif self.instruction == Instructions1Params.I.JUMP_TARGET:
            pass
        elif self.instruction == Instructions1Params.I.ALLOC:
            S.SP += self.param1
        else:
            raise Exception("Unknown instruction")
