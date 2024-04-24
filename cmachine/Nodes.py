import random
import string
from typing import Any
from ASTNode import ASTNode
from Instructions import Instructions0Params as I0P
from enum import Enum
from Instructions import Instructions1Params as I1P

NEWLINE = "\n"


class Number(ASTNode):
    def __init__(self, value):
        self.value = value

    def codeR(self, addressSpace: dict[str, int], n):
        return [I1P(I1P.I.LOADC, self.value)]

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of a number")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.value}"


# Shouldnt be global
SIZEOF: dict[str, (int, int)] = {}


class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

    def codeR(self, addressSpace: dict[str, int], n):
        (_, arraySize) = SIZEOF[self.name]
        if arraySize > 1:
            return self.codeL(addressSpace, n)
        else:
            return [*self.codeL(addressSpace, n), I0P(I0P.I.LOAD)]

    def codeL(self, addressSpace: dict[str, int], n):
        return [I1P(I1P.I.LOADC, addressSpace[self.name])]

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.name}"


class UnaryOperator(ASTNode):

    def __init__(self, operator: I0P.I, node: ASTNode):
        self.operator = operator
        self.node = node

    def codeR(self, addressSpace: dict[str, int], n):
        return [*self.node.codeR(addressSpace, n), I0P(self.operator)]

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of a unary operator")

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}({self.operator.value} {self.node})"


class BinaryOperation(ASTNode):

    def __init__(self, left: ASTNode, operator: I0P.I, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right

    def codeR(self, addressSpace: dict[str, int], n):
        return [*self.left.codeR(addressSpace, n), *self.right.codeR(addressSpace, n), I0P(self.operator)]

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of a binary operator")

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}({self.left} {self.operator.value} {self.right})"


class Assignment(ASTNode):

    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right

    def codeR(self, addressSpace: dict[str, int], n):
        return [*self.right.codeR(addressSpace, n), *self.left.codeL(addressSpace, n), I0P(I0P.I.STORE)]

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of an assignment")

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}{self.left} = {self.right}"


class Print(ASTNode):
    def __init__(self, node: ASTNode):
        self.node = node

    def codeR(self, addressSpace: dict[str, int], n):
        return [*self.node.codeR(addressSpace, n), I0P(I0P.I.PRINT)]

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of a print")

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}print({self.node});"


class Comma(ASTNode):
    def __init__(self, *nodes: ASTNode):
        self.nodes = nodes

    def codeR(self, addressSpace: dict[str, int], n):
        instructions = []
        for node in self.nodes[:-1]:
            instructions += node.codeR(addressSpace, n)
            instructions += [I0P(
                I0P.I.POP)]
        instructions += self.nodes[-1].codeR(addressSpace, n)

        return instructions

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of a comma")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{', '.join([f'{node}' for node in self.nodes])}"


class StatementSequence(ASTNode):
    def __init__(self, *nodes: ASTNode):
        self.nodes = nodes

    def code(self, addressSpace: dict[str, int], n):
        instructions = []
        for node in self.nodes:
            instructions += node.code(addressSpace, n)
        return instructions

    def codeR(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load R-value of a statement sequence")

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of a statement sequence")

    def pretty_print(self, indent):
        return f"{NEWLINE.join([f'{node.pretty_print(indent)}' for node in self.nodes])}"


LABEL_COUNTER = 0


def label_generator():
    global LABEL_COUNTER
    LABEL_COUNTER += 1
    return f"LABEL_{LABEL_COUNTER}"


class If(ASTNode):
    def __init__(self, condition: ASTNode, then: ASTNode):
        self.condition = condition
        self.then = then

    def code(self, addressSpace: dict[str, int], n):
        A = label_generator()
        return [*self.condition.codeR(addressSpace, n), I1P(I1P.I.JUMPZ, A), *self.then.code(addressSpace, n), I1P(I1P.I.JUMP_TARGET, A)]

    def codeR(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load R-value of an if statement")

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of an if statement")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}if ({self.condition}){NEWLINE}{self.then.pretty_print(indent+1)}"


class IfElse(ASTNode):
    def __init__(self, condition: ASTNode, then: ASTNode, else_: ASTNode):
        self.condition = condition
        self.then = then
        self.else_ = else_

    def code(self, addressSpace: dict[str, int], n):
        A = label_generator()
        B = label_generator()
        return [*self.condition.codeR(addressSpace, n), I1P(I1P.I.JUMPZ, A), *self.then.code(addressSpace, n), I1P(I1P.I.JUMP, B), I1P(I1P.I.JUMP_TARGET, A), *self.else_.code(addressSpace, n), I1P(I1P.I.JUMP_TARGET, B)]

    def codeR(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load R-value of an if statement")

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of an if statement")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}if ({self.condition}){NEWLINE}{self.then.pretty_print(indent+1)}{NEWLINE}{space}else{NEWLINE}{self.else_.pretty_print(indent+1)}"


class While(ASTNode):
    def __init__(self, condition: ASTNode, body: ASTNode):
        self.condition = condition
        self.body = body

    def code(self, addressSpace: dict[str, int], n):
        A = label_generator()
        B = label_generator()
        return [I1P(I1P.I.JUMP_TARGET, A), *self.condition.codeR(addressSpace, n), I1P(I1P.I.JUMPZ, B), *self.body.code(addressSpace, n), I1P(I1P.I.JUMP, A), I1P(I1P.I.JUMP_TARGET, B)]

    def codeR(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load R-value of a while statement")

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of a while statement")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}while ({self.condition}){NEWLINE}{self.body.pretty_print(indent+1)}"


class For(ASTNode):
    def __init__(self, initialization: ASTNode, condition: ASTNode, increment: ASTNode, body: ASTNode):
        self.initialization = initialization
        self.condition = condition
        self.increment = increment
        self.body = body

    def code(self, addressSpace: dict[str, int], n):
        A = label_generator()
        B = label_generator()

        return [*self.initialization.codeR(addressSpace, n), I0P(I0P.I.POP), I1P(I1P.I.JUMP_TARGET, A), *self.condition.codeR(addressSpace, n), I1P(I1P.I.JUMPZ, B), *self.body.code(addressSpace, n), *self.increment.codeR(addressSpace, n), I0P(I0P.I.POP), I1P(I1P.I.JUMP, A), I1P(I1P.I.JUMP_TARGET, B)]

    def codeR(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load R-value of a for statement")

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of a for statement")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}for ({self.initialization}; {self.condition}; {self.increment}){NEWLINE}{self.body.pretty_print(indent+1)}"


class DeclareVariable(ASTNode):
    def __init__(self, typeName: str, typeSize: int, arraySize: int, name: str, ss: ASTNode):
        self.typeName = typeName
        self.typeSize = typeSize
        self.arraySize = arraySize
        self.name = name
        self.ss = ss

    def code(self, addressSpace: dict[str, int], n):
        newAdressSpace = addressSpace.copy()
        totalSize = self.typeSize * self.arraySize
        newAdressSpace[self.name] = n
        SIZEOF[self.name] = (self.typeSize, self.arraySize)
        return [I1P(I1P.I.ALLOC, totalSize), *self.ss.code(newAdressSpace, n + totalSize)]

    def codeR(self, addressSpace: dict[str, int], n):
        return [*self.codeL(addressSpace, n), I0P(I0P.I.LOAD)]

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of a declaration")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.typeName}{f'[{self.arraySize}]' if self.arraySize !=1 else ''} {self.name};{NEWLINE}{self.ss.pretty_print(indent)}"


# Shouldnt be global
STRUCT_ADRESS_SPACES: dict[str, dict[str, int]] = {}


class DeclareStruct(ASTNode):
    def __init__(self, type: str, body: list[DeclareVariable], name: str, ss: ASTNode):
        self.type = type
        self.name = name
        self.body = body
        self.ss = ss

    def code(self, addressSpace: dict[str, int], n):
        newAdressSpace = addressSpace.copy()
        structAdressSpace = {}
        currentOffset = 0
        for variable in self.body:
            structAdressSpace[variable.name] = currentOffset
            currentOffset += variable.typeSize * variable.arraySize
        STRUCT_ADRESS_SPACES[self.name] = structAdressSpace
        newAdressSpace[self.name] = n
        return [I1P(I1P.I.ALLOC, currentOffset), *self.ss.code(newAdressSpace, n + currentOffset)]

    def codeR(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load R-value of a struct")

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of a struct")

    def pretty_print(self, indent):
        space = "  " * indent
        bracket_open = "{"
        bracket_close = "}"
        children = "".join([variable.pretty_print(indent+1)
                           for variable in self.body])
        return f"{space}struct {self.type} {bracket_open}{NEWLINE}{children}{bracket_close} {self.name}{NEWLINE}{self.ss.pretty_print(indent)}"


class ArrayAccess(ASTNode):
    def __init__(self, e1: ASTNode, e2: ASTNode):
        self.e1 = e1
        self.e2 = e2

    def codeL(self, addressSpace: dict[str, int], n):
        typeSize = SIZEOF[self.e1.name][0]
        return [*self.e1.codeR(addressSpace, n), *self.e2.codeR(addressSpace, n), I1P(I1P.I.LOADC, typeSize), I0P(I0P.I.MUL), I0P(I0P.I.ADD)]

    def codeR(self, addressSpace: dict[str, int], n):
        return [*self.codeL(addressSpace, n), I0P(I0P.I.LOAD)]

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.e1}[{self.e2}]"


class StructAccess(ASTNode):
    def __init__(self, struct_name: ASTNode, member_name: str):
        self.struct_name = struct_name
        self.member_name = member_name

    def codeL(self, addressSpace: dict[str, int], n):
        structAdressSpace = STRUCT_ADRESS_SPACES.get(self.struct_name.name)
        offset = structAdressSpace[self.member_name]
        return [*self.struct_name.codeL(addressSpace, n), I1P(I1P.I.LOADC, offset), I0P(I0P.I.ADD)]

    def codeR(self, addressSpace: dict[str, int], n):
        return [*self.codeL(addressSpace, n), I0P(I0P.I.LOAD)]

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.struct_name}.{self.member_name}"


class Malloc(ASTNode):
    def __init__(self, size: ASTNode):
        self.size = size

    def codeR(self, addressSpace: dict[str, int], n):
        return [*self.size.codeR(addressSpace, n), I0P(I0P.I.NEW)]

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of a malloc")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}malloc({self.size})"


class Dereference(ASTNode):
    def __init__(self, a: ASTNode):
        self.a = a

    def codeR(self, addressSpace: dict[str, int], n):
        return [*self.a.codeR(addressSpace, n), I0P(I0P.I.LOAD)]

    def codeL(self, addressSpace: dict[str, int], n):
        return [*self.a.codeR(addressSpace, n)]

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}*{self.a}"


class AddressOf(ASTNode):
    def __init__(self, a: ASTNode):
        self.a = a

    def codeR(self, addressSpace: dict[str, int], n):
        return [*self.a.codeL(addressSpace, n)]

    def codeL(self, addressSpace: dict[str, int], n):
        raise Exception("Cannot load L-value of an address of")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}&{self.a}"
