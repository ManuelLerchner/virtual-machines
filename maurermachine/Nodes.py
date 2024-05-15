import random
import string
from typing import Any, List
from ASTNode import ASTNode, label_generator, getvar
from Instructions import Instructions0Params as I0P
from enum import Enum
from Instructions import Instructions1Params as I1P, bcolors

NEWLINE = "\n"

AdressSpace = dict[str, (chr, int)]

# CALL_TYPE = "CBV"
CALL_TYPE = "CBN"


class BaseType(ASTNode):
    def __init__(self, value):
        self.value = value

    def codeB(self, addressSpace: AdressSpace, sd):
        return [I1P(I1P.I.LOADC, self.value)]

    def codeV(self, addressSpace: AdressSpace, sd):
        return [I1P(I1P.I.LOADC, self.value), I0P(I0P.I.MKBASIC)]

    def codeC(self, addressSpace: AdressSpace, sd):
        return self.codeV(addressSpace, sd)

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.value}"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        return set()


class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

    def codeV(self, addressSpace: AdressSpace, sd):
        return [*getvar(self.name, addressSpace, sd), I0P(I0P.I.EVAL)]

    def codeC(self, addressSpace: AdressSpace, sd):
        return getvar(self.name, addressSpace, sd)

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.name}"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        if self.name in boundVars:
            return set()
        else:
            return set([self.name])


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

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        return self.node.getFreeVariables(boundVars)


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

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        return self.left.getFreeVariables(boundVars).union(self.right.getFreeVariables(boundVars))


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

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        return self.condition.getFreeVariables(boundVars).union(self.then.getFreeVariables(boundVars)).union(self.else_.getFreeVariables(boundVars))


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
        string = ""
        for i, (var, expr) in enumerate(self.variables):
            vstring = space+var.pretty_print(indent+i)
            first_chr = 0
            for i, c in enumerate(vstring):
                if c != ' ':
                    first_chr = i
                    break
            letstr = "\n" + vstring[:first_chr]+"let (" + vstring[first_chr:]
            string += f"{letstr} = {expr.pretty_print(indent+1).strip()} in"
        string += f"\n{self.body.pretty_print(indent+len(self.variables))})"
        return string

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        s1 = set()
        new_bound_vars = set().union(boundVars)

        for (var, expr) in self.variables:
            new_bound_vars.add(var.name)
        for (var, expr) in self.variables:
            s1.union(expr.getFreeVariables(boundVars))

        s2 = self.body.getFreeVariables(new_bound_vars)

        return s1.union(s2)


class Fun(ASTNode):

    def __init__(self, variables: List[Variable], body: ASTNode):
        self.variables = variables
        self.body = body

    def codeV(self, addressSpace: AdressSpace, sd):

        z = self.getFreeVariables(set())

        newaddressSpace = {}

        code = []
        for i, var in enumerate(z):
            code += getvar(var, addressSpace, sd+i)
            newaddressSpace[var] = ('G', i)

        for i, var in enumerate(self.variables):
            newaddressSpace[var.name] = ('L', -i)

        A = label_generator()
        B = label_generator()

        k = len(self.variables)

        return [*code, I1P(I1P.I.MKVEC, len(z)), I1P(I1P.I.MKFUNVAL, A), I1P(I1P.I.JUMP, B), I1P(I1P.I.JUMP_TARGET, A), I1P(I1P.I.TARG, k),  *self.body.codeV(newaddressSpace, 0), I1P(I1P.I.RETURN, k), I1P(I1P.I.JUMP_TARGET, B)]

    def codeC(self, addressSpace: AdressSpace, sd):
        return self.codeV(addressSpace, sd)

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}fun {', '.join([var.pretty_print(0) for var in self.variables])} -> {self.body}"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        new_bound_vars = set().union(boundVars)
        for var in self.variables:
            new_bound_vars.add(var.name)

        return self.body.getFreeVariables(new_bound_vars)


class Apply(ASTNode):

    def __init__(self, func: ASTNode, params: List[ASTNode]):
        self.func = func
        self.params = params

    def codeV(self, addressSpace: AdressSpace, sd):

        code = []
        for i, p in enumerate(reversed(self.params)):
            if (CALL_TYPE == "CBV"):
                code += p.codeV(addressSpace, sd+3+i)
            elif (CALL_TYPE == "CBN"):
                code += p.codeC(addressSpace, sd+3+i)

        code += self.func.codeV(addressSpace, sd+len(self.params) + 3)

        A = label_generator()

        return [I1P(I1P.I.MARK, A), *code, I0P(I0P.I.APPLY), I1P(I1P.I.JUMP_TARGET, A)]

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}{self.func.pretty_print(0)} {' '.join([var.pretty_print(0) for var in self.params])}"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        s = self.func.getFreeVariables(boundVars)

        for p in self.params:
            s.union(p.getFreeVariables(boundVars))

        return s


class LetRecIn(ASTNode):

    def __init__(self, variables: List[tuple[Variable, ASTNode]], body: ASTNode):
        self.variables = variables
        self.body = body

    def codeV(self, addressSpace: AdressSpace, sd):
        newaddressSpace = addressSpace.copy()

        for i, (var, expr) in enumerate(self.variables):
            newaddressSpace[var.name] = ('L', sd+i+1)

        code = []
        for i, (var, expr) in enumerate(self.variables):
            if (CALL_TYPE == "CBV"):
                code += expr.codeV(newaddressSpace, sd+len(self.variables))
            elif (CALL_TYPE == "CBN"):
                code += expr.codeC(newaddressSpace, sd+len(self.variables))
            code += [I1P(I1P.I.REWRITE, len(self.variables)-i)]

        code += [*self.body.codeV(newaddressSpace, sd+len(self.variables))]

        return [I1P(I1P.I.ALLOC, len(self.variables)), *code, I1P(I1P.I.SLIDE, len(self.variables))]

    def pretty_print(self, indent=0):
        space = "  " * indent
        string = ""
        for i, (var, expr) in enumerate(self.variables):
            vstring = f"{space}{'let rec ' if i == 0 else ''}{var.pretty_print(indent+i)}"

            string += f"\n{vstring} = ({expr.pretty_print(indent+1).strip()}"
            if i != len(self.variables)-1:
                string += " and"
            else:
                string += " in"

        string += f"\n{self.body.pretty_print(indent+len(self.variables))})"
        return string

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        s1 = set()
        new_bound_vars = set().union(boundVars)
        for (var, expr) in self.variables:
            s1.union(expr.getFreeVariables(boundVars))
            new_bound_vars.add(var)

        s2 = self.body.getFreeVariables(new_bound_vars)

        return s1.union(s2)
