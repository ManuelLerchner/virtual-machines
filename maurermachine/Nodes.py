import random
import string
from typing import Any, List
from ASTNode import ASTNode
from Instructions import Instructions0Params as I0P
from enum import Enum
from Instructions import Instructions1Params as I1P, bcolors

NEWLINE = "\n"

AdressSpace = dict[str, (chr, int)]

# CALL_TYPE = "CBV"
CALL_TYPE = "CBV"


class BaseType(ASTNode):
    def __init__(self, value):
        self.value = value

    def codeB(self, addressSpace: AdressSpace, sd):
        return [I1P(I1P.I.LOADC, self.value)]

    def codeV(self, addressSpace: AdressSpace, sd):
        return [I1P(I1P.I.LOADC, self.value), I0P(I0P.I.MKBASIC)]

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.value}"


class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

    def codeV(self, addressSpace: AdressSpace, sd):
        def getvar(x, addressSpace, sd):
            t, v = addressSpace[x]
            if t == "L":
                return [I1P(I1P.I.PUSHLOC, sd-v)]
            elif t == "G":
                return [I1P(I1P.I.PUSHGLOB, v)]

        return [*getvar(self.name, addressSpace, sd), I0P(I0P.I.EVAL)]

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.name}"


class UnaryOperator(ASTNode):

    def __init__(self, operator: I0P.I, node: ASTNode):
        self.operator = operator
        self.node = node

    def codeB(self, addressSpace: AdressSpace, sd):
        return [*self.node.codeB(addressSpace, sd), I0P(self.operator)]

    def codeV(self, addressSpace: AdressSpace, sd):
        return [*self.node.codeB(addressSpace, sd), I0P(self.operator), I0P(I0P.I.MKBASIC)]

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}({self.operator.value} {self.node})"


class BinaryOperation(ASTNode):

    def __init__(self, left: ASTNode, operator: I0P.I, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right

    def codeB(self, addressSpace: AdressSpace, sd):
        return [*self.left.codeB(addressSpace, sd), *self.right.codeB(addressSpace, sd+1), I0P(self.operator)]

    def codeV(self, addressSpace: AdressSpace, sd):
        return [*self.left.codeB(addressSpace, sd), *self.right.codeB(addressSpace, sd+1), I0P(self.operator), I0P(I0P.I.MKBASIC)]

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}({self.left} {self.operator.value} {self.right})"


LABEL_COUNTER = 0


def base10ToBase26Letter_A_is_ONE(num):  # 1-based
    ''' Converts any positive integer to Base26(letters only) with no 0th 
    case. Useful for applications such as spreadsheet columns to determine which 
    Letterset goes with a positive integer.
    '''
    if num <= 0:
        return ""
    s = ""
    while (num > 0):
        s += (chr(97+(num-1) % 26))
        num -= 1
        num //= 26
    return s[::-1]


def label_generator():
    global LABEL_COUNTER
    LABEL_COUNTER += 1
    return f"{base10ToBase26Letter_A_is_ONE(LABEL_COUNTER)}"


class IfThenElse(ASTNode):

    def __init__(self, condition: ASTNode, then: ASTNode, else_: ASTNode):
        self.condition = condition
        self.then = then
        self.else_ = else_

    def codeB(self, addressSpace: AdressSpace, sd):
        A = label_generator()
        B = label_generator()
        return [
            *self.condition.codeB(addressSpace, sd),
            I1P(I1P.I.JUMPZ, A),
            *self.then.codeB(addressSpace, sd),
            I1P(I1P.I.JUMP, B),
            I1P(I1P.I.JUMP_TARGET, A),
            *self.else_.codeB(addressSpace, sd),
            I1P(I1P.I.JUMP_TARGET, B)
        ]

    def codeV(self, addressSpace: AdressSpace, sd):
        A = label_generator()
        B = label_generator()
        return [
            *self.condition.codeB(addressSpace, sd),
            I1P(I1P.I.JUMPZ, A),
            *self.then.codeV(addressSpace, sd),
            I1P(I1P.I.JUMP, B),
            I1P(I1P.I.JUMP_TARGET, A),
            *self.else_.codeV(addressSpace, sd),
            I1P(I1P.I.JUMP_TARGET, B)
        ]

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}if {self.condition} then {self.then} else {self.else_}"


class LetIn(ASTNode):

    def __init__(self, variables: List[tuple[Variable, ASTNode]], body: ASTNode):
        self.variables = variables
        self.body = body

    def codeV(self, addressSpace: AdressSpace, sd):
        newaddressSpace = addressSpace.copy()

        code = []
        for i, (var, expr) in enumerate(self.variables):
            if (CALL_TYPE == "CBV"):
                code += expr.codeV(newaddressSpace, sd+i)
            elif (CALL_TYPE == "CBN"):
                code += expr.codeC(newaddressSpace, sd+i)
            newaddressSpace[var.name] = ("L", sd+i+1)

        return [*code,  *self.body.codeV(newaddressSpace, sd+len(self.variables)), I1P(I1P.I.SLIDE, len(self.variables))]

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}let {' in let '.join([f'{var} = {expr}' for var, expr in self.variables])} in {self.body}"
