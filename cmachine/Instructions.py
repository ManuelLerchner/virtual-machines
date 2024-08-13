from __future__ import annotations
from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cmachine.Interpreter import Interpreter


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
        LOAD = "load"
        STORE = "store"
        POP = "pop"
        PRINT = "print"
        NEW = "new"
        MARK = "mark"
        CALL = "call"
        RETURN = "return"
        HALT = "halt"

    def __init__(self, instruction: I):
        self.instruction = instruction

    def __repr__(self):
        return f"{bcolors.WARNING+self.instruction.value+bcolors.ENDC}"

    def interpret(self, state: Interpreter):
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
            print(">>", S[S.SP])
        elif self.instruction == Instructions0Params.I.LOAD:
            S[S.SP] = S[S[S.SP]]
        elif self.instruction == Instructions0Params.I.STORE:
            S[S[S.SP]] = S[S.SP-1]
            S.SP -= 1
        elif self.instruction == Instructions0Params.I.POP:
            S.SP -= 1
        elif self.instruction == Instructions0Params.I.NEW:
            if (S.NP - S[S.SP] <= S.EP):
                S[S.SP] = 0
            else:
                S.NP -= S[S.SP]
                S[S.SP] = S.NP
        elif self.instruction == Instructions0Params.I.MARK:
            S[S.SP+1] = S.EP
            S[S.SP+2] = S.FP
            S.SP += 2
        elif self.instruction == Instructions0Params.I.CALL:
            tmp = S[S.SP]
            S[S.SP] = state.PC
            S.FP = S.SP
            state.PC = tmp
        elif self.instruction == Instructions0Params.I.RETURN:
            state.PC = S[S.FP]
            S.EP = S[S.FP-2]
            if (S.EP >= S.NP):
                raise Exception("Stack overflow")
            S.SP = S.FP-3
            S.FP = S[S.SP+2]
        elif self.instruction == Instructions0Params.I.HALT:
            state.PC = len(state.code)
        else:
            raise Exception("Unknown instruction")

    def description(self):
        if self.instruction == Instructions0Params.I.ADD:
            return "Adds the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.SUB:
            return "Subtracts the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.MUL:
            return "Multiplies the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.DIV:
            return "Divides the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.LEQ:
            return "Compares the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.GEQ:
            return "Compares the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.LT:
            return "Compares the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.GT:
            return "Compares the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.EQ:
            return "Compares the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.NEG:
            return "Negatives the topmost element of the stack"
        elif self.instruction == Instructions0Params.I.NOT:
            return "Negates the topmost element of the stack"
        elif self.instruction == Instructions0Params.I.LOAD:
            return "Interprets the topmost element of the stack as an address and loads the value at that address"
        elif self.instruction == Instructions0Params.I.STORE:
            return "Stores the second topmost element of the stack at the address given by the topmost element of the stack"
        elif self.instruction == Instructions0Params.I.POP:
            return "Pops the topmost element of the stack"
        elif self.instruction == Instructions0Params.I.PRINT:
            return "Prints the topmost element of the stack"
        elif self.instruction == Instructions0Params.I.NEW:
            return "Allocates a new memory block of the size given by the topmost element of the stack. Returns the address of the block"
        elif self.instruction == Instructions0Params.I.MARK:
            return "Saves FP and EP on the stack. This is used to mark the beginning of a new stack frame"
        elif self.instruction == Instructions0Params.I.CALL:
            return "Exchange the current PC with the topmost element (the address of the function to call). Sets the FP to the start of the current stack frame"
        elif self.instruction == Instructions0Params.I.RETURN:
            return "Pops the stackframe by restoring the [PC_old, FP_old, EP_old] at the base of the current stack frame"
        elif self.instruction == Instructions0Params.I.HALT:
            return "Halts the program"
        else:
            return "Unknown instruction"


class Instructions1Params(Instructions):

    class I(Enum):
        LOADC = "LOADC"
        LOADRC = "LOADRC"
        JUMP = "JUMP"
        JUMPZ = "JUMPZ"
        JUMP_TARGET = "JUMP_TARGET"
        ALLOC = "ALLOC"
        ENTER = "ENTER"
        SLIDE = "SLIDE"

    def __init__(self, instruction: I, param1):
        self.instruction = instruction
        self.param1 = param1

    def __repr__(self):
        return f"{bcolors.OKCYAN+self.instruction.value+bcolors.ENDC} {bcolors.OKGREEN+str(self.param1)+bcolors.ENDC}"

    def interpret(self, state: Interpreter):
        S = state.stack

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
        elif self.instruction == Instructions1Params.I.ALLOC:
            S.SP += self.param1
        elif self.instruction == Instructions1Params.I.ENTER:
            S.EP = S.SP + self.param1
            if S.EP >= S.NP:
                raise Exception("Stack overflow")
        elif self.instruction == Instructions1Params.I.SLIDE:
            tmp = S[S.SP]
            S.SP -= self.param1
            S[S.SP] = tmp
        else:
            raise Exception("Unknown instruction")

    def description(self):
        if self.instruction == Instructions1Params.I.LOADC:
            return "Loads the value given by the parameter onto the stack"
        elif self.instruction == Instructions1Params.I.LOADRC:
            return "Loads the relative address FP + param1 onto the stack"
        elif self.instruction == Instructions1Params.I.JUMP:
            return "Sets the PC to the value given by the parameter"
        elif self.instruction == Instructions1Params.I.JUMPZ:
            return "Sets the PC to the value given by the parameter if the topmost element of the stack is 0. Pops the stack"
        elif self.instruction == Instructions1Params.I.JUMP_TARGET:
            return "-"
        elif self.instruction == Instructions1Params.I.ALLOC:
            return "Allocates param1 memory cells on the stack. Returns the address of the first cell"
        elif self.instruction == Instructions1Params.I.ENTER:
            return "Sets the EXTREME POINTER to SP + param1. Limting the stack to param1 elements"
        elif self.instruction == Instructions1Params.I.SLIDE:
            return "Copies the topmost element (the return value) down param1 elements on the stack. This eliminiates formal parameters"
        else:
            return "Unknown instruction"
