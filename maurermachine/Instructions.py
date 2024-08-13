from __future__ import annotations
from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING
import copy

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
        MARK0 = "mark0"
        APPLY0 = "apply0"
        UPDATE = "update"
        COPYGLOB = "copyglob"
        NIL = "nil"
        CONS = "cons"

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
        elif self.instruction == Instructions0Params.I.NIL:
            S.SP += 1
            S[S.SP] = H.alloc("LNIL")
        elif self.instruction == Instructions0Params.I.CONS:
            S[S.SP-1] = H.alloc("LCONS", S[S.SP-1], S[S.SP])
            S.SP -= 1
        elif self.instruction == Instructions0Params.I.EVAL:
            h = S[S.SP]
            if H[h].tag == "C":
                Instructions0Params(
                    Instructions0Params.I.MARK0).interpret(state)
                Instructions1Params(
                    Instructions1Params.I.PUSHLOC, 3).interpret(state)
                Instructions0Params(
                    Instructions0Params.I.APPLY0).interpret(state)

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
        elif self.instruction == Instructions0Params.I.MARK0:
            S[S.SP+1] = state.GP
            S[S.SP+2] = state.FP
            S[S.SP+3] = state.PC
            S.SP += 3
            state.FP = S.SP
        elif self.instruction == Instructions0Params.I.APPLY0:
            h = S[S.SP]
            S.SP -= 1
            state.GP = H[h].globPtr
            state.PC = H[h].closurePtr
        elif self.instruction == Instructions0Params.I.UPDATE:
            Instructions0Params(
                Instructions0Params.I.POPENV).interpret(state)
            Instructions1Params(
                Instructions1Params.I.REWRITE, 1).interpret(state)
        elif self.instruction == Instructions0Params.I.COPYGLOB:
            S.SP += 1
            S[S.SP] = state.GP
        else:
            raise Exception("Unknown instruction")

    def description(self):
        if self.instruction == Instructions0Params.I.ADD:
            return "Add the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.SUB:
            return "Subtract the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.MUL:
            return "Multiply the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.DIV:
            return "Divide the two topmost elements of the stack"
        elif self.instruction == Instructions0Params.I.LEQ:
            return "Check if the second element is less than or equal to the topmost element"
        elif self.instruction == Instructions0Params.I.GEQ:
            return "Check if the second element is greater than or equal to the topmost element"
        elif self.instruction == Instructions0Params.I.LT:
            return "Check if the second element is less than the topmost element"
        elif self.instruction == Instructions0Params.I.GT:
            return "Check if the second element is greater than the topmost element"
        elif self.instruction == Instructions0Params.I.EQ:
            return "Check if the two topmost elements are equal"
        elif self.instruction == Instructions0Params.I.NEG:
            return "Make the topmost element negative"
        elif self.instruction == Instructions0Params.I.NOT:
            return "Negate the topmost element"
        elif self.instruction == Instructions0Params.I.PRINT:
            return "Print the topmost element"
        elif self.instruction == Instructions0Params.I.GETBASIC:
            return "Interpret the topmost element as address of a basic value in the heap, and load the value"
        elif self.instruction == Instructions0Params.I.MKBASIC:
            return "Interpret the topmost element as a basic value, and store it in the heap. Returns the address of the stored value"
        elif self.instruction == Instructions0Params.I.EVAL:
            return "Check if the topmost element is a closure, and if so, evaluate it. Otherwise, do nothing"
        elif self.instruction == Instructions0Params.I.HALT:
            return "Stop the program"
        elif self.instruction == Instructions0Params.I.APPLY:
            return "Interpret the topmost element as a Function. Update PC and GP stored in the function. Coppy all arguments from the heap to the stack"
        elif self.instruction == Instructions0Params.I.MKVEC0:
            return "Copies the elements above the frame pointer to a new vector in the heap, returns the address of the vector"
        elif self.instruction == Instructions0Params.I.WRAP:
            return "Creates a new function in the heap. The function has the current PC-1 as code pointer, the topmost element as argument pointer, and the current GP as global pointer"
        elif self.instruction == Instructions0Params.I.POPENV:
            return "Restores the global pointer, program counter and frame pointer from the stack. Save the topmost element and pop the remaining stack frame"
        elif self.instruction == Instructions0Params.I.MARK0:
            return "Save the current global pointer, frame pointer and program counter on top of the stack. (Contrary to MARK, this instructionsaves the PC on the stack)"
        elif self.instruction == Instructions0Params.I.APPLY0:
            return "Interpret the topmost element as a closure. Update GP and PC accordingly and jump to the closure entry point"
        elif self.instruction == Instructions0Params.I.UPDATE:
            return "Restore the global pointer, program counter and frame pointer from the stack. Rewrite the closure pointer in the stack, with the calculated value on top of the stack"
        elif self.instruction == Instructions0Params.I.COPYGLOB:
            return "Place the current global pointer on top of the stack"
        elif self.instruction == Instructions0Params.I.NIL:
            return "Create a new empty list in the heap, and push the address of the list onto the stack"
        elif self.instruction == Instructions0Params.I.CONS:
            return "Create a new cons cell in the heap. Expects Head and Tail on the stack. Returns the address of the new cons cell"
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
        ALLOC = "ALLOC"
        REWRITE = "REWRITE"
        MKCLOS = "MKCLOS"
        GET = "GET"
        GETVEC = "GETVEC"
        TLIST = "TLIST"

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
                H[h][i] = S[S.SP+i]
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
        elif self.instruction == Instructions1Params.I.ALLOC:
            for i in range(1, self.param1+1):
                S[S.SP+i] = H.alloc("C", -1, -1)
            S.SP += self.param1
        elif self.instruction == Instructions1Params.I.REWRITE:
            co = copy.copy(H[S[S.SP]])

            H[S[S.SP - self.param1]] = co

            S.SP -= self.param1
        elif self.instruction == Instructions1Params.I.MKCLOS:
            h = H.alloc("C", self.param1, S[S.SP])
            S[S.SP] = h
        elif self.instruction == Instructions1Params.I.GET:
            if H[S[S.SP]].tag != "V":
                raise Exception("Expected vector")
            vec = H[S[S.SP]]
            if vec.size <= self.param1:
                raise Exception("Out of bounds")
            S[S.SP] = vec[self.param1]
        elif self.instruction == Instructions1Params.I.GETVEC:
            if H[S[S.SP]].tag != "V":
                raise Exception("Expected vector")
            vec = H[S[S.SP]]
            S.SP -= 1
            for i in range(vec.size):
                S.SP += 1
                S[S.SP] = vec[i]
        elif self.instruction == Instructions1Params.I.TLIST:
            h = S[S.SP]
            if H[h].tag != "LCONS" and H[h].tag != "LNIL":
                raise Exception("Expected list")
            if H[h].tag == "LNIL":
                S.SP -= 1
            else:
                S[S.SP+1] = H[S[S.SP]].tail
                S[S.SP] = H[S[S.SP]].head
                S.SP += 1
                state.PC = self.param1
        else:
            raise Exception("Unknown instruction" + str(self.instruction))

    def description(self):
        if self.instruction == Instructions1Params.I.LOADC:
            return f"Load constant {self.param1} onto the stack"
        elif self.instruction == Instructions1Params.I.JUMP:
            return f"Jump to instruction {self.param1}"
        elif self.instruction == Instructions1Params.I.JUMPZ:
            return f"Jump to instruction {self.param1} if the topmost element is zero"
        elif self.instruction == Instructions1Params.I.JUMP_TARGET:
            return f""
        elif self.instruction == Instructions1Params.I.PUSHLOC:
            return f"Copies the {self.param1}th element below the SP to the top of the stack"
        elif self.instruction == Instructions1Params.I.PUSHGLOB:
            return f"Push the {self.param1}th element from the global pointer onto the stack"
        elif self.instruction == Instructions1Params.I.SLIDE:
            return f"Saves the topmost element, and removes the remaining {self.param1}-1 elements from the stack"
        elif self.instruction == Instructions1Params.I.MKVEC:
            return f"Copy the topmost {self.param1} elements to a new vector in the heap, and push the address of the vector onto the stack"
        elif self.instruction == Instructions1Params.I.MKFUNVAL:
            return f"Create a new function in the heap. The function has the parameter {self.param1} as code pointer, an empty vector as argument pointer, and the topmost element of the stack as global pointer"
        elif self.instruction == Instructions1Params.I.TARG:
            return f"Check if there are at least {self.param1} elements above the frame pointer. If not, there is under supply, and a new function with partial arguments is created. Otherwise, do nothing"
        elif self.instruction == Instructions1Params.I.RETURN:
            return f"If all {self.param1} arguments are on the stack are consumed, pop the stack frame. Otherwise, the another function (the return of the expression) must be applied"
        elif self.instruction == Instructions1Params.I.MARK:
            return f"Save the current global pointer, frame pointer and return address {self.param1} on top of the stack"
        elif self.instruction == Instructions1Params.I.ALLOC:
            return f"Allocate {self.param1} new dummy objects on the heap. Copy the addresses of the new objects to the stack"
        elif self.instruction == Instructions1Params.I.REWRITE:
            return f"Rewrite the adress {self.param1} elements below the top of the stack with the topmost element"
        elif self.instruction == Instructions1Params.I.MKCLOS:
            return f"Create a new closure in the heap. The closure has the topmost element as global pointer, and {self.param1} as code pointer"
        elif self.instruction == Instructions1Params.I.GET:
            return f"Interpret the topmost element as a vector in the heap, and copy the {self.param1}th element of the vector onto the stack"
        elif self.instruction == Instructions1Params.I.GETVEC:
            return f"Interpret the topmost element as a vector in the heap, and copy all elements of the vector onto the stack"
        elif self.instruction == Instructions1Params.I.TLIST:
            return f"Interpret the topmost element as a list in the heap. If the list is empty, pop the stack frame. Otherwise, copy the head and tail of the list to the stack. Afterwards jump to instruction {self.param1}"
        else:
            raise Exception("Unknown instruction")
