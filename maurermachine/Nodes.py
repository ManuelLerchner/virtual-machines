import random
import string
from typing import Any, List
from ASTNode import ASTNode, CompilationResult, label_generator, getvar, makeCompilationResult
from Instructions import Instructions0Params as I0P
from enum import Enum
from Instructions import Instructions1Params as I1P, bcolors

NEWLINE = "\n"

AdressSpace = dict[str, (chr, int)]

CALL_TYPE = "CBV"
# CALL_TYPE = "CBN"


class BaseType(ASTNode):
    def __init__(self, value):
        self.value = value

    def codeB(self, addressSpace: AdressSpace, sd):
        code = [I1P(I1P.I.LOADC, self.value)]

        return makeCompilationResult(code, f"BaseType B({self.value})", self)

    def codeV(self, addressSpace: AdressSpace, sd):
        code = [I1P(I1P.I.LOADC, self.value),
                I0P(I0P.I.MKBASIC)]

        return makeCompilationResult(code,  f"BaseType V({self.value})", self)

    def codeC(self, addressSpace: AdressSpace, sd):
        return makeCompilationResult(self.codeV(addressSpace, sd),  f"BaseType C({self.value})", self)

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.value}"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        return set()


class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

    def codeV(self, addressSpace: AdressSpace, sd):
        code = [*getvar(self.name, addressSpace, sd), I0P(I0P.I.EVAL)]

        return makeCompilationResult(code,  f"Variable V({self.name})", self)

    def codeC(self, addressSpace: AdressSpace, sd):
        code = getvar(self.name, addressSpace, sd)

        return makeCompilationResult(code,  f"Variable C({self.name})", self)

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}{self.name}"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        if self.name in boundVars:
            return set()
        else:
            return set([self.name])


class Nil(ASTNode):
    def __init__(self):
        pass

    def codeV(self, addressSpace: AdressSpace, sd):
        code = [I0P(I0P.I.NIL)]

        return makeCompilationResult(code,  "Nil V", self)

    def codeC(self, addressSpace: AdressSpace, sd):
        code = self.codeV(addressSpace, sd)

        return makeCompilationResult(code,  "Nil C", self)

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}[]"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        return set()


class Cons(ASTNode):
    def __init__(self, head: ASTNode, tail: ASTNode):
        self.head = head
        self.tail = tail

    def codeV(self, addressSpace: AdressSpace, sd):
        if (CALL_TYPE == "CBV"):
            head = self.head.codeV(addressSpace, sd)
            tail = self.tail.codeV(addressSpace, sd+1)
        elif (CALL_TYPE == "CBN"):
            head = self.head.codeC(addressSpace, sd)
            tail = self.tail.codeC(addressSpace, sd+1)
        else:
            raise Exception("CALL_TYPE not set")

        code = [head, tail, I0P(I0P.I.CONS)]
        return makeCompilationResult(code, f"Cons V({self.head} :: {self.tail}) {CALL_TYPE}", self)

    def codeC(self, addressSpace: AdressSpace, sd):
        code = self.codeV(addressSpace, sd)

        return makeCompilationResult(code, f"Cons C({self.head} :: {self.tail})", self)

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space}({self.head} :: {self.tail})"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        return self.head.getFreeVariables(boundVars).union(self.tail.getFreeVariables(boundVars))


class Print(ASTNode):
    def __init__(self, node: ASTNode):
        self.node = node

    def codeV(self, addressSpace: AdressSpace, sd):
        body = self.node.codeB(addressSpace, sd)

        code = [body, I0P(I0P.I.PRINT),
                I1P(I1P.I.SLIDE, 1), I1P(I1P.I.MKVEC, 0)]

        return makeCompilationResult(code, f"Print V({self.node})", self)

    def pretty_print(self, indent):
        space = "  " * indent
        return f"{space} print {self.node}"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        return self.node.getFreeVariables(boundVars)


class UnaryOperator(ASTNode):

    def __init__(self, operator: I0P.I, node: ASTNode):
        self.operator = operator
        self.node = node

    def codeB(self, addressSpace: AdressSpace, sd):
        body = self.node.codeB(addressSpace, sd)

        code = [body, I0P(self.operator)]
        return makeCompilationResult(code, f"UnaryOperator B({self.operator} {self.node})", self)

    def codeV(self, addressSpace: AdressSpace, sd):
        body = self.node.codeB(addressSpace, sd)

        code = [body, I0P(self.operator), I0P(I0P.I.MKBASIC)]
        return makeCompilationResult(code, f"UnaryOperator V({self.operator} {self.node})", self)

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
        left = self.left.codeB(addressSpace, sd)
        right = self.right.codeB(addressSpace, sd+1)

        code = [left, right, I0P(self.operator)]

        return makeCompilationResult(code, f"BinaryOperation B", self)

    def codeV(self, addressSpace: AdressSpace, sd):
        left = self.left.codeB(addressSpace, sd)
        right = self.right.codeB(addressSpace, sd+1)

        code = [left, right, I0P(self.operator), I0P(I0P.I.MKBASIC)]

        return makeCompilationResult(code, f"BinaryOperation V", self)

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

        cond = self.condition.codeB(addressSpace, sd)
        then = self.then.codeB(addressSpace, sd)
        else_ = self.else_.codeB(addressSpace, sd)

        code = [
            cond,
            I1P(I1P.I.JUMPZ, A),
            then,
            I1P(I1P.I.JUMP, B),
            I1P(I1P.I.JUMP_TARGET, A),
            else_,
            I1P(I1P.I.JUMP_TARGET, B)
        ]

        return makeCompilationResult(code, f"IfThenElse B", self)

    def codeV(self, addressSpace: AdressSpace, sd):
        A = label_generator()
        B = label_generator()

        cond = self.condition.codeB(addressSpace, sd)
        then = self.then.codeV(addressSpace, sd)
        else_ = self.else_.codeV(addressSpace, sd)

        code = [
            cond,
            I1P(I1P.I.JUMPZ, A),
            then,
            I1P(I1P.I.JUMP, B),
            I1P(I1P.I.JUMP_TARGET, A),
            else_,
            I1P(I1P.I.JUMP_TARGET, B)
        ]

        return makeCompilationResult(code, f"IfThenElse V", self)

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

        declar_variables = []
        for i, (var, expr) in enumerate(self.variables):
            if (CALL_TYPE == "CBV"):
                var_i = expr.codeV(newaddressSpace, sd+i)
            elif (CALL_TYPE == "CBN"):
                var_i = expr.codeC(newaddressSpace, sd+i)
            else:
                raise Exception("CALL_TYPE not set")

            declar_variables.append(var_i)

            newaddressSpace[var.name] = ("L", sd+i+1)

        body = self.body.codeV(
            newaddressSpace, sd+len(self.variables))

        code = [
            makeCompilationResult(declar_variables, f"Params", None),  body,
            I1P(I1P.I.SLIDE, len(self.variables))]

        return makeCompilationResult(code, f"LetIn V", self)

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
            s1 = s1.union(expr.getFreeVariables(boundVars))

        s2 = self.body.getFreeVariables(new_bound_vars)

        return s1.union(s2)


class Fun(ASTNode):

    def __init__(self, variables: List[Variable], body: ASTNode):
        self.variables = variables
        self.body = body

    def codeV(self, addressSpace: AdressSpace, sd):

        z = self.getFreeVariables(set())

        newaddressSpace = addressSpace.copy()

        declare_variables = []
        for i, var in enumerate(z):
            var_i = getvar(var, addressSpace, sd+i)

            declare_variables.append(*var_i)

            newaddressSpace[var] = ('G', i)

        for i, var in enumerate(self.variables):
            newaddressSpace[var.name] = ('L', -i)

        A = label_generator()
        B = label_generator()

        k = len(self.variables)

        code = [
            makeCompilationResult(declare_variables, f"Globals", None), I1P(I1P.I.MKVEC, len(z)), I1P(I1P.I.MKFUNVAL, A), I1P(I1P.I.JUMP, B), I1P(I1P.I.JUMP_TARGET, A), I1P(
                I1P.I.TARG, k),  self.body.codeV(newaddressSpace, 0), I1P(I1P.I.RETURN, k), I1P(I1P.I.JUMP_TARGET, B)]

        return makeCompilationResult(code, f"Fun V", self)

    def codeC(self, addressSpace: AdressSpace, sd):
        return makeCompilationResult(self.codeV(addressSpace, sd), f"Fun C", self)

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}(fun {', '.join([var.pretty_print(0) for var in self.variables])} -> {self.body})"

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

        paramsCode = []
        for i, p in enumerate(reversed(self.params)):
            if (CALL_TYPE == "CBV"):
                paramsCode.append(p.codeV(addressSpace, sd+3+i))
            elif (CALL_TYPE == "CBN"):
                paramsCode.append(p.codeC(addressSpace, sd+3+i))

        func = self.func.codeV(addressSpace, sd+len(self.params) + 3)

        A = label_generator()

        code = [I1P(I1P.I.MARK, A),
                makeCompilationResult(
                    paramsCode, f"Params", self), func, I0P(I0P.I.APPLY),
                I1P(I1P.I.JUMP_TARGET, A)]

        return makeCompilationResult(code, f"Apply V", self)

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}{self.func.pretty_print(0)} {' '.join([var.pretty_print(0) for var in self.params])}"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        s = self.func.getFreeVariables(boundVars)

        for p in self.params:
            s = s.union(p.getFreeVariables(boundVars))

        return s


class LetRecIn(ASTNode):

    def __init__(self, variables: List[tuple[Variable, ASTNode]], body: ASTNode):
        self.variables = variables
        self.body = body

    def codeV(self, addressSpace: AdressSpace, sd):
        newaddressSpace = addressSpace.copy()

        for i, (var, expr) in enumerate(self.variables):
            newaddressSpace[var.name] = ('L', sd+i+1)

        params = []
        for i, (var, expr) in enumerate(self.variables):
            if (CALL_TYPE == "CBV"):
                params.append(expr.codeV(
                    newaddressSpace, sd+len(self.variables)))
            elif (CALL_TYPE == "CBN"):
                params.append(expr.codeC(
                    newaddressSpace, sd+len(self.variables)))
            params += [I1P(I1P.I.REWRITE, len(self.variables)-i)]

        body = self.body.codeV(newaddressSpace, sd+len(self.variables))

        code = [I1P(I1P.I.ALLOC, len(self.variables)),
                makeCompilationResult(params, f"Params", None),
                body, I1P(I1P.I.SLIDE, len(self.variables))]

        return makeCompilationResult(code, f"LetRecIn V", self)

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
            s1 = s1.union(expr.getFreeVariables(boundVars))
            new_bound_vars.add(var)

        s2 = self.body.getFreeVariables(new_bound_vars)

        return s1.union(s2)


class Tuple(ASTNode):

    def __init__(self, elements: List[ASTNode]):
        self.elements = elements

    def codeV(self, addressSpace: AdressSpace, sd):
        params = []
        for i, e in enumerate(self.elements):
            if (CALL_TYPE == "CBV"):
                params.append(e.codeV(addressSpace, sd+i))
            elif (CALL_TYPE == "CBN"):
                params.append(e.codeC(addressSpace, sd+i))

        code = [
            makeCompilationResult(params, f"Params", None), I1P(I1P.I.MKVEC, len(self.elements))]

        return makeCompilationResult(code, f"Tuple V", self)

    def codeC(self, addressSpace: AdressSpace, sd):
        return makeCompilationResult(self.codeV(addressSpace, sd), f"Tuple C", self)

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}({', '.join([e.pretty_print(0) for e in self.elements])})"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        s = set()
        for e in self.elements:
            s = s.union(e.getFreeVariables(boundVars))

        return s


class TupleAccess(ASTNode):

    def __init__(self, tuple_: ASTNode, index: int, ):
        self.tuple = tuple_
        self.index = index

    def codeV(self, addressSpace: AdressSpace, sd):
        code = [self.tuple.codeV(addressSpace, sd), I1P(
            I1P.I.GET, self.index), I0P(I0P.I.EVAL)]

        return makeCompilationResult(code, f"TupleAccess V",    self)

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}(#{self.index} {self.tuple})"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        return self.tuple.getFreeVariables(boundVars)


class DeconstructTuple(ASTNode):

    def __init__(self,  variables: List[Variable], tuple_: ASTNode, body: ASTNode):
        self.variables = variables
        self.tuple = tuple_
        self.body = body

    def codeV(self, addressSpace: AdressSpace, sd):
        newaddressSpace = addressSpace.copy()

        for i, var in enumerate(self.variables):
            newaddressSpace[var.name] = ('L', sd+i+1)

        code = [self.tuple.codeV(addressSpace, sd), I1P(I1P.I.GETVEC, len(self.variables)), self.body.codeV(
            newaddressSpace, sd+len(self.variables)), I1P(I1P.I.SLIDE, len(self.variables))]

        return makeCompilationResult(code, f"DeconstructTuple V", self)

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}let ({', '.join([var.pretty_print(0) for var in self.variables])} = {self.tuple} in {self.body})"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        s1 = set()
        new_bound_vars = set().union(boundVars)
        for var in self.variables:
            new_bound_vars.add(var.name)
        s1 = s1.union(self.tuple.getFreeVariables(boundVars))
        s2 = self.body.getFreeVariables(new_bound_vars)

        return s1.union(s2)


class MatchList(ASTNode):

    def __init__(self, list_: ASTNode, nil_case: ASTNode, cons_variables: List[Variable],
                 cons_case: ASTNode):
        self.list = list_
        self.nil_case = nil_case
        self.cons_variables = cons_variables
        self.cons_case = cons_case

    def codeV(self, addressSpace: AdressSpace, sd):
        A = label_generator()
        B = label_generator()

        newAddressspace = addressSpace.copy()

        for i, var in enumerate(self.cons_variables):
            newAddressspace[var.name] = ('L', sd+i+1)

        code = [self.list.codeV(addressSpace, sd), I1P(I1P.I.TLIST, A), self.nil_case.codeV(addressSpace, sd), I1P(I1P.I.JUMP, B), I1P(I1P.I.JUMP_TARGET, A),
                self.cons_case.codeV(newAddressspace, sd+2),                I1P(I1P.I.SLIDE, 2), I1P(I1P.I.JUMP_TARGET, B)]

        return makeCompilationResult(code, f"MatchList V", self)

    def pretty_print(self, indent=0):
        space = "  " * indent
        return f"{space}match {self.list} with [] -> {self.nil_case} | {self.cons_variables[0]} :: {self.cons_variables[1]} -> {self.cons_case}"

    def getFreeVariables(self, boundVars: set[str]) -> set[str]:
        s1 = set()
        s1 = s1.union(self.list.getFreeVariables(boundVars))
        s1 = s1.union(self.nil_case.getFreeVariables(boundVars))

        new_bound_vars = set().union(boundVars)
        for var in self.cons_variables:
            new_bound_vars.add(var.name)
        s1 = s1.union(self.cons_case.getFreeVariables(new_bound_vars))

        return s1
