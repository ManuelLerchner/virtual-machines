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
    OKWHITE = '\033[97m'
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
        PRINT = "print"
        GETBASIC = "getbasic"
        MKBASIC = "mkbasic"
        EVAL = "eval"
        HALT = "halt"
        APPLY = "apply"
        MKVEC0 = "mkvec0"
        WRAP = "wrap"
        POPENV = "popenv"

    def __init__(self, instruction: I):
        self.instruction = instruction

    def __repr__(self):
        return f"{bcolors.OKYELLOW+self.instruction.value+bcolors.ENDC}"

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
        elif self.instruction == Instructions0Params.I.HALT:
            state.PC = -1
        elif self.instruction == Instructions0Params.I.APPLY:
            h = S[S.SP]
            if H[h].tag != "F":
                raise Exception("Expected function")
            state.GP = H[h].globPtr
            state.PC = H[h].codePtr
            for i in range(H[H[h].argPtr].size):
                S[S.SP+i] = H[H[h].argPtr][i]
            S.SP += H[H[h].argPtr].size - 1
        elif self.instruction == Instructions0Params.I.MKVEC0:
            g = S.SP - state.FP
            h = H.alloc("V", g)
            S.SP = state.FP + 1
            for i in range(g):
                H[h][i] = S[S.SP+i]
            S[S.SP] = h
        elif self.instruction == Instructions0Params.I.WRAP:
            S[S.SP] = H.alloc("F", state.PC-1, S[S.SP], state.GP)
        elif self.instruction == Instructions0Params.I.POPENV:
            state.GP = S[state.FP-2]
            S[state.FP-2] = S[S.SP]
            state.PC = S[state.FP]
            S.SP = state.FP - 2
            state.FP = S[state.FP-1]
        else:
            raise Exception("Unknown instruction")


class Instructions1Params(Instructions):

    class I(Enum):
        LOADC = "LOADC"
        JUMP = "JUMP"
        JUMPZ = "JUMPZ"
        JUMP_TARGET = "JUMP_TARGET"
        SLIDE = "SLIDE"
        PUSHLOC = "PUSHLOC"
        PUSHGLOB = "PUSHGLOB"
        MKVEC = "MKVEC"
        MKFUNVAL = "MKFUNVAL"
        TARG = "TARG"
        RETURN = "RETURN"
        MARK = "MARK"

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
            S[S.SP-self.param1] = S[S.SP]
            S.SP -= self.param1
        elif self.instruction == Instructions1Params.I.MKVEC:
            h = H.alloc("V", self.param1)
            S.SP = S.SP-self.param1+1
            for i in range(self.param1):
                H[h][i] = S[S.SP]
            S[S.SP] = h
        elif self.instruction == Instructions1Params.I.MKFUNVAL:
            a = H.alloc("V", 0)
            S[S.SP] = H.alloc("F", self.param1, a, S[S.SP])
        elif self.instruction == Instructions1Params.I.TARG:
            if (S.SP - state.FP < self.param1):
                Instructions0Params(
                    Instructions0Params.I.MKVEC0).interpret(state)
                Instructions0Params(
                    Instructions0Params.I.WRAP).interpret(state)
                Instructions0Params(
                    Instructions0Params.I.POPENV).interpret(state)
        elif self.instruction == Instructions1Params.I.RETURN:
            if (S.SP - state.FP == self.param1+1):
                Instructions0Params(
                    Instructions0Params.I.POPENV).interpret(state)
            else:
                Instructions1Params(
                    Instructions1Params.I.SLIDE, self.param1).interpret(state)
                Instructions0Params(
                    Instructions0Params.I.APPLY).interpret(state)
        elif self.instruction == Instructions1Params.I.MARK:
            S[S.SP+1] = state.GP
            S[S.SP+2] = state.FP
            S[S.SP+3] = self.param1
            S.SP += 3
            state.FP = S.SP
        else:
            raise Exception("Unknown instruction" + str(self.instruction))
