from __future__ import annotations
from abc import abstractmethod
from enum import Enum
from typing import TYPE_CHECKING
import copy

if TYPE_CHECKING:
    from Interpreter import Interpreter, Heap


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
    ITALIC = '\033[3m'


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
        PUTANON = "PUTANON"
        BIND = "BIND"
        UNIFY = "UNIFY"
        POP = "POP"
        POPENV = "POPENV"
        SETBTP = "SETBTP"
        DELBTP = "DELBTP"
        NO = "NO"

    def __init__(self, instruction: I):
        self.instruction = instruction

    def __repr__(self):
        return f"{bcolors.OKYELLOW+self.instruction.value+bcolors.ENDC}"

    def interpret(self, state: Interpreter):
        S = state.stack
        H = state.heap
        T = state.trail
        if self.instruction == Instructions0Params.I.PUTANON:
            H[H.HP] = H.makeElement("R", H.HP)
            S.SP += 1
            S[S.SP] = H.HP
            H.HP += 1
        elif self.instruction == Instructions0Params.I.BIND:
            H[S[S.SP-1]] = H.makeElement("R", S[S.SP])
            trail(S[S.SP-1], state)
            S.SP -= 2
        elif self.instruction == Instructions0Params.I.UNIFY:
            unify(S[S.SP-1], S[S.SP], state)
            S.SP -= 2
        elif self.instruction == Instructions0Params.I.POP:
            S.SP -= 1
        elif self.instruction == Instructions0Params.I.POPENV:
            if state.FP > state.BP:
                S.SP = state.FP - 6
            state.PC = state.jumpLabels[posCont(S, state.FP)]
            state.FP = FPOld(S, state.FP)
        elif self.instruction == Instructions0Params.I.SETBTP:
            # HPold
            S[state.FP-2] = H.HP
            # TPOld
            S[state.FP-3] = T.SP
            # BPOld
            S[state.FP-4] = state.BP
            state.BP = state.FP
        elif self.instruction == Instructions0Params.I.DELBTP:
            state.BP = BPOld(S, state.FP)
        elif self.instruction == Instructions0Params.I.NO:
            print("No")
            state.PC = len(state.code) + 1
        else:
            raise Exception("Unknown instruction")


class Instructions1Params(Instructions):

    class I(Enum):
        PUTATOM = "PUTATOM"
        PUTREF = "PUTREF"
        PUTVAR = "PUTVAR"
        PUTSTRUCT = "PUTSTRUCT"
        UATOM = "UATOM"
        UVAR = "UVAR"
        UREF = "UREF"
        USTRUCT = "USTRUCT"
        SON = "SON"
        UP = "UP"
        JUMP = "JUMP"
        JUMP_TARGET = "JUMP_TARGET"
        MARK = "MARK"
        CALL = "CALL"
        CHECK = "CHECK"
        PUSHENV = "PUSHENV"
        TRY = "TRY"
        INIT = "INIT"
        HALT = "HALT"

    def __init__(self, instruction: I, param1, param2=None):
        self.instruction = instruction
        self.param1 = param1
        self.param2 = param2

    def __repr__(self):
        return f"{bcolors.OKCYAN+self.instruction.value+bcolors.ENDC} {bcolors.OKGREEN+str(self.param1)+bcolors.ENDC}" + (f" {bcolors.OKGREEN+str(self.param2)+bcolors.ENDC}" if self.param2 is not None else "")

    def interpret(self, state: Interpreter):
        S = state.stack
        H = state.heap

        # if (type(self.param1) == str):
        #     self.param1 = state.jumpLabels[self.param1]

        if self.instruction == Instructions1Params.I.PUTATOM:
            H[H.HP] = H.makeElement("A", self.param1)
            S.SP += 1
            S[S.SP] = H.HP
            H.HP += 1
        elif self.instruction == Instructions1Params.I.PUTREF:
            S.SP += 1
            S[S.SP] = deref(S[state.FP+self.param1], state)
        elif self.instruction == Instructions1Params.I.PUTVAR:
            H[H.HP] = H.makeElement("R", H.HP)
            S.SP += 1
            S[S.SP] = H.HP
            S[state.FP+self.param1] = H.HP
            H.HP += 1
        elif self.instruction == Instructions1Params.I.PUTSTRUCT:
            H[H.HP] = H.makeElement("S", self.param1)
            name = self.param1
            [f, n] = name.split("/")
            n = int(n)
            S.SP = S.SP - n + 1
            for i in range(1, n+1):
                H[H.HP+i] = S[S.SP+i-1]
            S[S.SP] = H.HP
            H.HP += n+1
        elif self.instruction == Instructions1Params.I.UATOM:
            v = S[S.SP]
            S.SP -= 1
            element = H[v]

            if element.tag == "A" and element.a == self.param1:
                return
            elif element.tag == "R":
                a = self.param1
                H[H.HP] = H.makeElement("A", a)
                H[v] = H.makeElement("R", H.HP)
                H.HP += 1
                trail(v, state)
                return
            else:
                backtrack(S, state)
        elif self.instruction == Instructions1Params.I.UVAR:
            S[state.FP+self.param1] = S[S.SP]
            S.SP -= 1
        elif self.instruction == Instructions1Params.I.UREF:
            unify(S[S.SP], deref(S[state.FP+self.param1], state), state)
            S.SP -= 1
        elif self.instruction == Instructions1Params.I.USTRUCT:
            h = H[S[S.SP]]
            [f, n] = self.param1.split("/")
            n = int(n)
            if h.tag == "S" and h.f == f and h.n == n:
                return
            elif h.tag == "R":
                state.PC = state.jumpLabels[self.param2]
                return
            else:
                backtrack(S, state)
        elif self.instruction == Instructions1Params.I.SON:
            S[S.SP+1] = deref(H[S[S.SP] + self.param1], state)
            S.SP += 1
        elif self.instruction == Instructions1Params.I.UP:
            S.SP -= 1
            state.PC = state.jumpLabels[self.param1]
        elif self.instruction == Instructions1Params.I.JUMP:
            state.PC = state.jumpLabels[self.param1]
        elif self.instruction == Instructions1Params.I.JUMP_TARGET:
            pass
        elif self.instruction == Instructions1Params.I.MARK:
            S.SP += 6
            S[S.SP] = self.param1
            S[S.SP-1] = state.FP
        elif self.instruction == Instructions1Params.I.CALL:
            name = self.param1
            # split the name
            [l, n] = name.split("/")
            n = int(n)
            state.FP = S.SP - n
            state.PC = state.jumpLabels[name]
        elif self.instruction == Instructions1Params.I.CHECK:
            if not check(S[S.SP], deref(S[state.FP+self.param1], state), state):
                backtrack(S, state)
        elif self.instruction == Instructions1Params.I.PUSHENV:
            S.SP = state.FP + self.param1
        elif self.instruction == Instructions1Params.I.TRY:
            # negCont
            S[state.FP-5] = state.PC
            state.PC = state.jumpLabels[self.param1]
        elif self.instruction == Instructions1Params.I.INIT:
            state.BP = 5
            state.FP = 5
            S.SP = 5
            S[0] = self.param1
            S[1] = -1
            S[2] = -1
            S[3] = 0
            state.BP = state.FP
        elif self.instruction == Instructions1Params.I.HALT:
            # returns bindings of all self.param1 globals
            for i in range(0, self.param1):
                adress = S[state.FP+i+1]
                print(f">> X{i} = {H.pretty_print(adress)}")
            if self.param1 == 0:
                print(">> Yes")
            # wait for user input
            input("\nPress Enter to continue...\n")
            backtrack(S, state)
        else:
            raise Exception("Unknown instruction" + str(self.instruction))


def deref(v, state):
    H = state.heap
    element = H[v]
    if element.tag == "R" and element.value != v:
        return deref(element.value, state)
    else:
        return v


def trail(u, state):
    S = state.stack
    T = state.trail

    if u < S[state.BP-2]:
        T.SP += 1
        T[T.SP] = u


def unify(u, v, state):
    S = state.stack
    H = state.heap
    if u == v:
        return True

    element_u = H.stack[u]
    element_v = H.stack[v]

    if element_u.tag == "R":
        if element_v.tag == "R":
            if u > v:
                H[u] = H.makeElement("R", v)
                trail(u, state)
                return True
            else:
                H[v] = H.makeElement("R", u)
                trail(v, state)
                return True
        elif check(u, v, state):
            H[u] = H.makeElement("R", v)
            trail(u, state)
            return True
        else:
            backtrack(S, H, state)
            return False

    if element_v.tag == "R":
        if check(v, u, state):
            H[v] = H.makeElement("R", u)
            trail(v, state)
            return True
        else:
            backtrack(S, state)
            return False

    if element_u.tag == "A" and element_v.tag == "A" and element_u.a == element_v.a:
        return True

    if element_u.tag == "S" and element_v.tag == "S":
        if element_u.f == element_v.f and element_u.n == element_v.n:
            for i in range(1, element_u.n+1):
                if not unify(deref(H[u+i], state), deref(H[v+i], state), state):
                    return False
            return True

    backtrack(S,  state)
    return False


def check(u, v, state):
    H = state.heap
    if u == v:
        return False
    if H[u].tag == "S":
        (f, n) = H[u].f

        for i in range(1, n+1):
            if not check(u, deref(H[v+i], H), H):
                return False
    return True


def backtrack(S, state):
    H = state.heap

    state.FP = state.BP
    H.HP = HPold(S, state.FP)
    reset(TPOld(S, state.FP), state.trail.SP, state)
    state.TP = TPOld(S, state.FP)
    neg_cnt = negCont(S, state.FP)
    state.PC = state.jumpLabels[neg_cnt] if type(neg_cnt) == str else neg_cnt


def reset(x, y, state):
    u = y
    H = state.heap
    T = state.trail
    while x < u:
        H[T[u]] = H.makeElement("R", T[u])
        u -= 1


def posCont(S, FP):
    return S[FP]


def FPOld(S, FP):
    return S[FP-1]


def HPold(S, FP):
    return S[FP-2]


def TPOld(S, FP):
    return S[FP-3]


def BPOld(S, FP):
    return S[FP-4]


def negCont(S, FP):
    return S[FP-5]
