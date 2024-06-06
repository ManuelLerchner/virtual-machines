import random
import string
from typing import Any
from ASTNode import ASTNode, makeCompilationResult
from Instructions import Instructions0Params as I0P
from enum import Enum
from Instructions import Instructions1Params as I1P, bcolors

NEWLINE = "\n"

AdressSpace = dict[str, (chr, int)]


class Number(ASTNode):
    def __init__(self, value):
        self.value = value

    def codeR(self, addressSpace: AdressSpace, n):
        code = [I1P(I1P.I.LOADC, self.value)]
        return makeCompilationResult(code, f"CodeR for {self.value}", self)

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a number")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.value}"

    def getType(self):
        return "int"


SIZEOF: dict[str, (int, int)] = {
    "int": (1, 1),
}
# Shouldnt be global


class Variable(ASTNode):
    def __init__(self, type: str, name: str):
        self.type = type
        self.name = name

    def codeR(self, addressSpace: AdressSpace, n):
        # is function
        if "(" in self.type:
            code = [I1P(I1P.I.LOADC, addressSpace[self.name][1])]
            return makeCompilationResult(code, f"CodeR for {self.name}", self)

        (_, arraySize) = SIZEOF[self.name]
        if arraySize > 1:
            code = self.codeL(addressSpace, n)
        else:
            code = [self.codeL(addressSpace, n), I0P(I0P.I.LOAD)]

        return makeCompilationResult(code, f"CodeR for {self.name}", self)

    def codeL(self, addressSpace: AdressSpace, n):
        if addressSpace[self.name][0] == 'G':
            code = [I1P(I1P.I.LOADC, addressSpace[self.name][1])]
        else:
            code = [I1P(I1P.I.LOADRC, addressSpace[self.name][1])]

        return makeCompilationResult(code, f"CodeL for {self.name}", self)

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{bcolors.OKCYAN+self.name+bcolors.ENDC}"

    def getType(self):
        return self.type


class UnaryOperator(ASTNode):

    def __init__(self, operator: I0P.I, node: ASTNode):
        self.operator = operator
        self.node = node

    def codeR(self, addressSpace: AdressSpace, n):
        code = [self.node.codeR(addressSpace, n), I0P(self.operator)]

        makeCompilationResult(code, f"CodeR for {self.operator}", self)

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a unary operator")

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}({self.operator.value} {self.node})"

    def getType(self):
        raise Exception("Cannot get type of a unary operator")


class BinaryOperation(ASTNode):

    def __init__(self, left: ASTNode, operator: I0P.I, right: ASTNode):
        self.left = left
        self.operator = operator
        self.right = right

    def codeR(self, addressSpace: AdressSpace, n):
        code = [self.left.codeR(addressSpace, n),
                self.right.codeR(addressSpace, n), I0P(self.operator)]
        return makeCompilationResult(code, f"CodeR for {self.operator}", self)

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a binary operator")

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}({self.left} {self.operator.value} {self.right})"

    def getType(self):
        return self.left.getType()


class Assignment(ASTNode):

    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right

    def codeR(self, addressSpace: AdressSpace, n):
        code = [self.right.codeR(addressSpace, n),
                self.left.codeL(addressSpace, n), I0P(I0P.I.STORE)]
        return makeCompilationResult(code, f"CodeR for assignment", self)

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of an assignment")

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}{self.left} = {self.right}"

    def getType(self):
        return self.left.getType()


class Print(ASTNode):
    def __init__(self, node: ASTNode):
        self.node = node

    def codeR(self, addressSpace: AdressSpace, n):
        code = [self.node.codeR(addressSpace, n), I0P(I0P.I.PRINT)]
        return makeCompilationResult(code, f"CodeR for print", self)

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a print")

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}print({self.node});"

    def getType(self):
        return "void"


class Comma(ASTNode):
    def __init__(self, *nodes: ASTNode):
        self.nodes = nodes

    def codeR(self, addressSpace: AdressSpace, n):
        instructions = []
        for node in self.nodes[:-1]:
            instructions += node.codeR(addressSpace, n)
            instructions += [I0P(
                I0P.I.POP)]
        instructions += self.nodes[-1].codeR(addressSpace, n)

        return makeCompilationResult(instructions, f"CodeR for comma", self)

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a comma")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{', '.join([f'{node}' for node in self.nodes])}"

    def getType(self):
        return self.nodes[-1].getType()


class StatementSequence(ASTNode):
    def __init__(self, *nodes: ASTNode):
        self.nodes = nodes

    def code(self, addressSpace: AdressSpace, n):
        instructions = []
        for node in self.nodes:
            instructions.append(node.code(addressSpace, n))
        return makeCompilationResult(instructions, f"Code for statement sequence", self)

    def codeR(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load R-value of a statement sequence")

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a statement sequence")

    def pretty_print(self, indent):
        return f"{NEWLINE.join([f'{node.pretty_print(indent)}' for node in self.nodes])}"

    def getType(self):
        return self.nodes[-1].getType()


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


class If(ASTNode):
    def __init__(self, condition: ASTNode, then: ASTNode):
        self.condition = condition
        self.then = then

    def code(self, addressSpace: AdressSpace, n):
        A = label_generator()
        code = [self.condition.codeR(addressSpace, n), I1P(
            I1P.I.JUMPZ, A), self.then.code(addressSpace, n), I1P(I1P.I.JUMP_TARGET, A)]
        return makeCompilationResult(code, f"Code for if", self)

    def codeR(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load R-value of an if statement")

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of an if statement")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{bcolors.OKORANGE}if{bcolors.ENDC} ({self.condition}):{NEWLINE}{self.then.pretty_print(indent+1)}"

    def getType(self):
        raise Exception("Cannot get type of an if statement")


class IfElse(ASTNode):
    def __init__(self, condition: ASTNode, then: ASTNode, else_: ASTNode):
        self.condition = condition
        self.then = then
        self.else_ = else_

    def code(self, addressSpace: AdressSpace, n):
        A = label_generator()
        B = label_generator()
        code = [self.condition.codeR(addressSpace, n), I1P(I1P.I.JUMPZ, A), self.then.code(addressSpace, n), I1P(
            I1P.I.JUMP, B), I1P(I1P.I.JUMP_TARGET, A), self.else_.code(addressSpace, n), I1P(I1P.I.JUMP_TARGET, B)]
        return makeCompilationResult(code, f"Code for if else", self)

    def codeR(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load R-value of an if statement")

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of an if statement")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{bcolors.OKORANGE}if{bcolors.ENDC} ({self.condition}):{NEWLINE}{self.then.pretty_print(indent+1)}{NEWLINE}{space}{bcolors.OKORANGE}else{bcolors.ENDC}:{NEWLINE}{self.else_.pretty_print(indent+1)}"

    def getType(self):
        raise Exception("Cannot get type of an if statement")


class While(ASTNode):
    def __init__(self, condition: ASTNode, body: ASTNode):
        self.condition = condition
        self.body = body

    def code(self, addressSpace: AdressSpace, n):
        A = label_generator()
        B = label_generator()
        code = [I1P(I1P.I.JUMP_TARGET, A), self.condition.codeR(addressSpace, n), I1P(I1P.I.JUMPZ, B),
                self.body.code(addressSpace, n), I1P(I1P.I.JUMP, A), I1P(I1P.I.JUMP_TARGET, B)]
        return makeCompilationResult(code, f"Code for while", self)

    def codeR(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load R-value of a while statement")

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a while statement")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{bcolors.OKORANGE}while{bcolors.ENDC} ({self.condition}):{NEWLINE}{self.body.pretty_print(indent+1)}"

    def getType(self):
        raise Exception("Cannot get type of a while statement")


class For(ASTNode):
    def __init__(self, initialization: ASTNode, condition: ASTNode, increment: ASTNode, body: ASTNode):
        self.initialization = initialization
        self.condition = condition
        self.increment = increment
        self.body = body

    def code(self, addressSpace: AdressSpace, n):
        A = label_generator()
        B = label_generator()

        code = [self.initialization.codeR(addressSpace, n), I0P(I0P.I.POP), I1P(I1P.I.JUMP_TARGET, A), self.condition.codeR(addressSpace, n), I1P(
            I1P.I.JUMPZ, B), self.body.code(addressSpace, n), self.increment.codeR(addressSpace, n), I0P(I0P.I.POP), I1P(I1P.I.JUMP, A), I1P(I1P.I.JUMP_TARGET, B)]

        return makeCompilationResult(code, f"Code for for", self)

    def codeR(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load R-value of a for statement")

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a for statement")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{bcolors.OKORANGE}for{bcolors.ENDC} ({self.initialization}; {self.condition}; {self.increment}):{NEWLINE}{self.body.pretty_print(indent+1)}"

    def getType(self):
        raise Exception("Cannot get type of a for statement")


class DeclareVariable(ASTNode):
    def __init__(self, type: str, typeSize: int, arraySize: int, name: str, ss: ASTNode):
        self.type = type
        self.typeSize = typeSize
        self.arraySize = arraySize
        self.name = name
        self.ss = ss

    def code(self, addressSpace: AdressSpace, n):
        newAdressSpace = addressSpace.copy()
        totalSize = self.typeSize * self.arraySize
        newAdressSpace[self.name] = ('L', n)
        SIZEOF[self.type] = (self.typeSize, 1)
        SIZEOF[self.name] = (self.typeSize, self.arraySize)
        code = [I1P(I1P.I.ALLOC, totalSize),
                self.ss.code(newAdressSpace, n + totalSize)]
        return makeCompilationResult(code, f"Code for declaration", self)

    def codeR(self, addressSpace: AdressSpace, n):
        return [self.codeL(addressSpace, n), I0P(I0P.I.LOAD)]

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a declaration")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{bcolors.OKMAGENTA}{self.type}{bcolors.ENDC}{f'[{self.arraySize}]' if self.arraySize !=1 else ''} {bcolors.OKCYAN}{self.name}{bcolors.ENDC};{NEWLINE}{self.ss.pretty_print(indent)}"

    def getType(self):
        return self.type


# Shouldnt be global
STRUCT_ADRESS_SPACES: dict[str, dict[str, (str, int)]] = {}


class DeclareStruct(ASTNode):
    def __init__(self, type: str, body: list[DeclareVariable], name: str, ss: ASTNode):
        self.type = type
        self.name = name
        self.body = body
        self.ss = ss

    def code(self, addressSpace: AdressSpace, n):
        newAdressSpace = addressSpace.copy()
        structAdressSpace = {}
        currentOffset = 0
        for variable in self.body:
            structAdressSpace[variable.name] = (variable.type, currentOffset)
            currentOffset += variable.typeSize * variable.arraySize
            SIZEOF[variable.type] = (variable.typeSize, variable.arraySize)
            SIZEOF[variable.name] = (variable.typeSize, variable.arraySize)
        STRUCT_ADRESS_SPACES[self.type] = structAdressSpace
        SIZEOF[self.type] = (currentOffset, 1)
        newAdressSpace[self.name] = ('L', n)
        code = [I1P(I1P.I.ALLOC, currentOffset),
                self.ss.code(newAdressSpace, n + currentOffset)]
        return makeCompilationResult(code, f"Code for struct declaration", self)

    def codeR(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load R-value of a struct")

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a struct")

    def pretty_print(self, indent):
        space = "  " * indent
        bracket_open = "{"
        bracket_close = "}"
        children = "".join([variable.pretty_print(indent+1)
                           for variable in self.body])
        return f"{space}{bcolors.OKORANGE}struct{bcolors.ENDC} {self.type} {bracket_open}{NEWLINE}{children}{bracket_close} {self.name}{NEWLINE}{self.ss.pretty_print(indent)}"

    def getType(self):
        return self.getType


class ArrayAccess(ASTNode):
    def __init__(self, e1: ASTNode, e2: ASTNode):
        self.e1 = e1
        self.e2 = e2

    def codeL(self, addressSpace: AdressSpace, n):
        typeSize = SIZEOF[self.e1.getType()][0]
        code = [self.e1.codeR(addressSpace, n), self.e2.codeR(addressSpace, n),
                I1P(I1P.I.LOADC, typeSize), I0P(I0P.I.MUL), I0P(I0P.I.ADD)]
        return makeCompilationResult(code, f"CodeL for array access", self)

    def codeR(self, addressSpace: AdressSpace, n):
        code = [self.codeL(addressSpace, n), I0P(I0P.I.LOAD)]
        return makeCompilationResult(code, f"CodeR for array access", self)

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.e1}[{self.e2}]"

    def getType(self):
        return self.e1.getType().replace("*", "")


class StructAccess(ASTNode):
    def __init__(self, struct_name: ASTNode, member_name: str):
        self.struct_name = struct_name
        self.member_name = member_name

    def codeL(self, addressSpace: AdressSpace, n):
        structAdressSpace = STRUCT_ADRESS_SPACES.get(self.struct_name.name)
        offset = structAdressSpace[self.member_name][1]
        code = [self.struct_name.codeL(addressSpace, n),
                I1P(I1P.I.LOADC, offset), I0P(I0P.I.ADD)]
        return makeCompilationResult(code, f"CodeL for struct access", self)

    def codeR(self, addressSpace: AdressSpace, n):
        code = [self.codeL(addressSpace, n), I0P(I0P.I.LOAD)]
        return makeCompilationResult(code, f"CodeR for struct access", self)

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.struct_name}.{self.member_name}"

    def getType(self):
        return self.struct_name.getType().replace("*", "")


class Malloc(ASTNode):
    def __init__(self, size: ASTNode):
        self.size = size

    def codeR(self, addressSpace: AdressSpace, n):
        return [self.size.codeR(addressSpace, n), I0P(I0P.I.NEW)]

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a malloc")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{bcolors.OKRED}malloc{bcolors.ENDC}({self.size})"

    def getType(self):
        return "void*"


class Dereference(ASTNode):
    def __init__(self, a: ASTNode):
        self.a = a

    def codeR(self, addressSpace: AdressSpace, n):
        code = [self.a.codeR(addressSpace, n), I0P(I0P.I.LOAD)]
        return makeCompilationResult(code, f"CodeR for dereference", self)

    def codeL(self, addressSpace: AdressSpace, n):
        code = [self.a.codeR(addressSpace, n)]
        return makeCompilationResult(code, f"CodeL for dereference", self)

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}*{self.a}"

    def getType(self):
        return self.a.getType().replace("*", "")


class AddressOf(ASTNode):
    def __init__(self, a: ASTNode):
        self.a = a

    def codeR(self, addressSpace: AdressSpace, n):
        code = [self.a.codeL(addressSpace, n)]
        return makeCompilationResult(code, f"CodeR for address of", self)

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of an address of")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}&{self.a}"

    def getType(self):
        return self.a.getType() + "*"


class Arrow(ASTNode):
    def __init__(self, a: ASTNode, member_name: str):
        self.a = a
        self.member_name = member_name

    def codeR(self, addressSpace: AdressSpace, n):
        (_, arraySize) = SIZEOF[self.member_name]
        if arraySize > 1:
            code = self.codeL(addressSpace, n)
        else:
            code = [self.codeL(addressSpace, n), I0P(I0P.I.LOAD)]
        return makeCompilationResult(code, f"CodeR for arrow", self)

    def codeL(self, addressSpace: AdressSpace, n):
        code = [self.a.codeR(addressSpace, n), I1P(I1P.I.LOADC,
                                                   STRUCT_ADRESS_SPACES[self.a.type.replace("*", "")][self.member_name][1]), I0P(I0P.I.ADD)]
        return makeCompilationResult(code, f"CodeL for arrow", self)

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.a}->{self.member_name}"

    def getType(self):
        return STRUCT_ADRESS_SPACES[self.a.type.replace("*", "")][self.member_name][0]


class FunctionDefinition(ASTNode):
    def __init__(self, type: str, name: str, args: list[ASTNode], body: ASTNode):
        self.type = type
        self.name = name
        self.args = args
        self.body = body

    def code(self, addressSpace: AdressSpace, n):
        _f = label_generator()
        addressSpace[self.name] = ('G', _f)
        newAdressSpace = addressSpace.copy()
        argOffset = 0
        for arg in self.args:
            argOffset += SIZEOF[arg.getType()][0]
            newAdressSpace[arg.name] = ('L', -2 - argOffset)
            SIZEOF[arg.type] = (SIZEOF[arg.getType()][0], 1)
            SIZEOF[arg.name] = (SIZEOF[arg.getType()][0], 1)
        SIZEOF[self.name] = (1, 1)
        code = [I1P(I1P.I.JUMP_TARGET, _f), I1P(I1P.I.ENTER, 500),
                self.body.code(newAdressSpace, 1), I0P(I0P.I.RETURN)]
        return makeCompilationResult(code, f"Code for function definition", self)

    def codeR(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load R-value of a function definition")

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a function definition")

    def pretty_print(self, indent):
        space = "  " * indent
        # return f"{space}{bcolors.OKMAGENTA+self.type+bcolors.ENDC} {bcolors.OKRED+self.name+bcolors.ENDC} ({', '.join([str(arg).replace("\n","") for arg in self.args])}){NEWLINE}{self.body.pretty_print(indent+1)}"

        return f"{space}{bcolors.OKMAGENTA+self.type+bcolors.ENDC} {bcolors.OKRED+self.name+bcolors.ENDC} ({', '.join([str(arg).replace(NEWLINE, '') for arg in self.args])}){NEWLINE}{self.body.pretty_print(indent+1)}"

    def getType(self):
        return self.type


class FunctionCall(ASTNode):
    def __init__(self, function: ASTNode, args: list[ASTNode]):
        self.function = function
        self.args = args

    def codeR(self, addressSpace: AdressSpace, n):
        instructions = []
        parameter_size = 0
        for arg in reversed(self.args):
            instructions.append(arg.codeR(addressSpace, n))
            parameter_size += SIZEOF[arg.getType()][0]
        instructions += [I0P(I0P.I.MARK), self.function.codeR(addressSpace, n),
                         I0P(I0P.I.CALL), I1P(I1P.I.SLIDE, parameter_size-1)]
        code = instructions
        return makeCompilationResult(code, f"CodeR for function call", self)

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a function call")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{bcolors.OKRED+ self.function.name+bcolors.ENDC}({', '.join([f'{arg}' for arg in self.args])})"

    def getType(self):
        return "void"


class Return(ASTNode):
    def __init__(self, value: ASTNode):
        self.value = value

    def code(self, addressSpace: AdressSpace, n):
        code = [self.value.codeR(addressSpace, n), I1P(I1P.I.LOADRC, -3),
                I0P(I0P.I.STORE), I0P(I0P.I.RETURN)]
        return makeCompilationResult(code, f"Code for return", self)

    def codeR(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load R-value of a return")

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a return")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{bcolors.BOLD}return{bcolors.ENDC} {self.value}"

    def getType(self):
        return "void"


class Program(ASTNode):
    def __init__(self, globalVariables: list[DeclareVariable], functions: list[FunctionDefinition]):
        self.globalVariables = globalVariables
        self.functions = functions

    def code(self, addressSpace: AdressSpace, n):
        size_of_globals = 0
        for globalVariable in self.globalVariables:
            size_of_globals += globalVariable.typeSize * globalVariable.arraySize
            addressSpace[globalVariable.name] = ('G', n + size_of_globals)
            SIZEOF[globalVariable.type] = (
                globalVariable.typeSize, globalVariable.arraySize)
            SIZEOF[globalVariable.name] = (
                globalVariable.typeSize, globalVariable.arraySize)

        functionCode = []

        newAdressSpace = addressSpace.copy()
        for function in self.functions:
            newAdressSpace[function.name] = (
                'G', function.name)
            functionCode += [I1P(I1P.I.JUMP_TARGET, function.name),
                             function.code(newAdressSpace, n)]

        instructions = [I1P(I1P.I.ENTER, size_of_globals+4), I1P(I1P.I.ALLOC, size_of_globals+1), I0P(I0P.I.MARK),
                        I1P(I1P.I.LOADC, "main"), I0P(I0P.I.CALL), I1P(I1P.I.SLIDE, size_of_globals), I0P(I0P.I.HALT)]
        instructions += functionCode

        return makeCompilationResult(instructions, f"Code for program", self)

    def codeR(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load R-value of a return")

    def codeL(self, addressSpace: AdressSpace, n):
        raise Exception("Cannot load L-value of a return")

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{NEWLINE.join([f'{globalVariable.pretty_print(indent)}' for globalVariable in self.globalVariables])}{NEWLINE}{(NEWLINE+NEWLINE).join([f'{function.pretty_print(indent)}' for function in self.functions])}"

    def getType(self):
        return "void"
