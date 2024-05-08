from __future__ import annotations
from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Interpreter import Interpreter


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    OKYELLOW = '\033[93m'
    OKRED = '\033[91m'
    OKMAGENTA = '\033[95m'
    OKORANGE = '\033[33m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Instructions:

    def __init__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def interpret(self, state: Interpreter):
        pass


class Instructions0Params(Instructions):

    class I(Enum):
        ADD = "+"
        SUB = "-"
        MUL = "*"
        DIV = "/"
        LEQ = "<="
        GEQ = ">="
        LT = "<"
        GT = ">"
        EQ = "=="
        NEG = "-"
        NOT = "!"
        GETBASIC = "getbasic"
        MKBASIC = "mkbasic"
        EVAL = "eval"
        PRINT = "print"
        HALT = "halt"

    def __init__(self, instruction: I):
        self.instruction = instruction

    def __repr__(self):
        return f"{bcolors.WARNING+self.instruction.value+bcolors.ENDC}"

    def interpret(self, state: Interpreter):
        S = state.stack
        H = state.heap
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
            print(">>", S[S.SP])
        elif self.instruction == Instructions0Params.I.GETBASIC:
            if (H[S[S.SP]].tag != "B"):
                raise Exception("Expected basic value")
            else:
                S[S.SP] = H[S[S.SP]].value
        elif self.instruction == Instructions0Params.I.MKBASIC:
            S[S.SP] = H.alloc("B", S[S.SP])
        elif self.instruction == Instructions0Params.I.EVAL:
            pass
        else:
            raise Exception("Unknown instruction")


class Instructions1Params(Instructions):

    class I(Enum):
        LOADC = "LOADC"
        LOADRC = "LOADRC"
        JUMP = "JUMP"
        JUMPZ = "JUMPZ"
        JUMP_TARGET = "JUMP_TARGET"
        SLIDE = "SLIDE"
        PUSHLOC = "PUSHLOC"
        PUSHGLOB = "PUSHGLOB"

    def __init__(self, instruction: I, param1):
        self.instruction = instruction
        self.param1 = param1

    def __repr__(self):
        return f"{bcolors.OKCYAN+self.instruction.value+bcolors.ENDC} {bcolors.OKGREEN+str(self.param1)+bcolors.ENDC}"

    def interpret(self, state: Interpreter):
        S = state.stack
        H = state.heap

        if (type(self.param1) == str):
            self.param1 = state.jumpLabels[self.param1]

        if self.instruction == Instructions1Params.I.LOADC:
            S.SP += 1
            S[S.SP] = self.param1
        elif self.instruction == Instructions1Params.I.LOADRC:
            S.SP += 1
            S[S.SP] = S.FP + self.param1
        elif self.instruction == Instructions1Params.I.JUMP:
            state.PC = self.param1
        elif self.instruction == Instructions1Params.I.JUMPZ:
            if S[S.SP] == 0:
                state.PC = self.param1
            S.SP -= 1
        elif self.instruction == Instructions1Params.I.JUMP_TARGET:
            pass
        elif self.instruction == Instructions1Params.I.PUSHLOC:
            S[S.SP+1] = S[S.SP - self.param1]
            S.SP += 1
        elif self.instruction == Instructions1Params.I.PUSHGLOB:
            S.SP += 1
            S[S.SP] = H[state.GP][self.param1]
        elif self.instruction == Instructions1Params.I.SLIDE:
            tmp = S[S.SP]
            S.SP -= self.param1
            S[S.SP] = tmp
        else:
            raise Exception("Unknown instruction")
