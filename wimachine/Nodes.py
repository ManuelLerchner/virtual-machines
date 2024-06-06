
from typing import Any, List
from ASTNode import ASTNode, CompilationResult, label_generator, makeCompilationResult
from Instructions import Instructions0Params as I0P
from enum import Enum
from Instructions import Instructions1Params as I1P, bcolors

NEWLINE = "\n"

AdressSpace = dict[str, (chr, int)]


def check(ivars: set[str], addressSpace: dict[str, int]) -> I1P:
    code = []
    for ivar in ivars:
        code.append(I1P(I1P.I.CHECK, addressSpace[ivar]))

    return CompilationResult(code, "Check ivars", None)


class Atom(ASTNode):
    def __init__(self, a):
        self.a = a

    def codeA(self, addressSpace: dict[str, int]) -> CompilationResult:
        code = [I1P(I1P.I.PUTATOM, self.a)]
        return makeCompilationResult(code, f"Atom {self.a}", self)

    def codeU(self, addressSpace: dict[str, int]) -> CompilationResult:
        code = [I1P(I1P.I.UATOM, self.a)]
        return makeCompilationResult(code, f"CodeU Atom {self.a}", self)

    def ivars(self) -> set[str]:
        return set()

    def locals(self) -> set[str]:
        return set()

    def pretty_print(self, indent: int) -> str:
        return f"{bcolors.OKWHITE+bcolors.BOLD}{self.a}{bcolors.ENDC}"


class Variable(ASTNode):
    def __init__(self, X):
        self.X = X

    def codeA(self, addressSpace: dict[str, int]) -> CompilationResult:
        code = [I1P(I1P.I.PUTVAR, addressSpace[self.X])]
        return makeCompilationResult(code, f"Variable {self.X}", self)

    def codeU(self, addressSpace: dict[str, int]) -> CompilationResult:
        code = [I1P(I1P.I.UVAR, addressSpace[self.X])]
        return makeCompilationResult(code, f"CodeU Variable {self.X}", self)

    def ivars(self) -> set[str]:
        return set()

    def locals(self) -> set[str]:
        return set([self.X])

    def pretty_print(self, indent: int) -> str:
        return f"{bcolors.ITALIC+bcolors.BOLD+bcolors.OKBLUE}{self.X}{bcolors.ENDC}"


class InitializedVariable(ASTNode):
    def __init__(self, X):
        self.X = X

    def codeA(self, addressSpace: dict[str, int]) -> CompilationResult:
        code = [I1P(I1P.I.PUTREF, addressSpace[self.X])]
        return makeCompilationResult(code, f"InitializedVariable {self.X}", self)

    def codeU(self, addressSpace: dict[str, int]) -> CompilationResult:
        code = [I1P(I1P.I.UREF, addressSpace[self.X])]
        return makeCompilationResult(code, f"CodeU InitializedVariable {self.X}", self)

    def ivars(self) -> set[str]:
        return set([self.X])

    def locals(self) -> set[str]:
        return set([self.X])

    def pretty_print(self, indent: int) -> str:
        return f"{bcolors.ITALIC+bcolors.OKBLUE}{self.X}{bcolors.ENDC}"


class AnonymousVariable(ASTNode):
    def __init__(self):
        pass

    def codeA(self, addressSpace: dict[str, int]) -> CompilationResult:
        code = [I0P(I0P.I.PUTANON, 0)]
        return makeCompilationResult(code, f"AnonymousVariable", self)

    def codeU(self, addressSpace: dict[str, int]) -> CompilationResult:
        code = [I0P(I0P.I.POP)]
        return makeCompilationResult(code, f"CodeU AnonymousVariable", self)

    def ivars(self) -> set[str]:
        return set()

    def locals(self) -> set[str]:
        return set()

    def pretty_print(self, indent: int) -> str:
        return f"{bcolors.OKYELLOW}_{bcolors.ENDC}"


class Constructor(ASTNode):
    def __init__(self, name: str, args: List[ASTNode]):
        self.name = name
        self.args = args

    def codeA(self, addressSpace: dict[str, int]) -> CompilationResult:
        code = []
        for arg in self.args:
            code.append(arg.codeA(addressSpace))

        code += [I1P(I1P.I.PUTSTRUCT, f"{self.name}/{len(self.args)}")]

        return makeCompilationResult(code, f"Constructor {self.name}({', '.join([arg.pretty_print(0) for arg in self.args])})", self)

    def codeU(self, addressSpace: dict[str, int]) -> CompilationResult:
        args = []
        for i, arg in enumerate(self.args):
            args.append(I1P(I1P.I.SON, i+1))
            args.append(arg.codeU(addressSpace))

        A = label_generator()
        B = label_generator()

        args.append(I1P(I1P.I.UP, B))

        initialized_vars = self.ivars()

        code = [I1P(
            I1P.I.USTRUCT, f"{self.name}/{len(self.args)}", A), *args, I1P(I1P.I.JUMP_TARGET, A),
            check(initialized_vars, addressSpace), self.codeA(addressSpace), I0P(I0P.I.BIND), I1P(I1P.I.JUMP_TARGET, B)]

        return makeCompilationResult(code, f"CodeU Constructor {self.name}({', '.join([arg.pretty_print(0) for arg in self.args])})", self)

    def ivars(self) -> set[str]:
        ivars = set()
        for arg in self.args:
            ivars = ivars.union(arg.ivars())
        return ivars

    def locals(self) -> set[str]:
        locals = set()
        for arg in self.args:
            locals = locals.union(arg.locals())
        return locals

    def pretty_print(self, indent: int) -> str:
        # special treatment for lists
        if self.name == "NIL":
            return f"{bcolors.OKYELLOW}[]{bcolors.ENDC}"
        if self.name == "CONS":
            return f"{bcolors.OKYELLOW}[{bcolors.ENDC}{self.args[0].pretty_print(indent)}{bcolors.OKYELLOW}|{bcolors.ENDC}{self.args[1].pretty_print(indent)}{bcolors.OKYELLOW}]{bcolors.ENDC}"

        return f"{bcolors.OKYELLOW}{self.name}{bcolors.ENDC}({', '.join([arg.pretty_print(indent) for arg in self.args])})"


class Literal(ASTNode):
    def __init__(self, p: str, args: List[ASTNode]):
        self.p = p
        self.args = args

    def codeG(self, addressSpace: dict[str, int]) -> CompilationResult:
        args = []
        for arg in self.args:
            args.append(arg.codeA(addressSpace))

        B = label_generator()

        code = [I1P(I1P.I.MARK, B), *args, I1P(I1P.I.CALL,
                                               f"{self.p}/{len(self.args)}"), I1P(I1P.I.JUMP_TARGET, B)]

        return makeCompilationResult(code, f"Literal {self.p}({', '.join([arg.pretty_print(0) for arg in self.args])})", self)

    def codeU(self, addressSpace: dict[str, int]) -> CompilationResult:
        pass

    def ivars(self) -> set[str]:
        ivars = set()
        for arg in self.args:
            ivars = ivars.union(arg.ivars())
        return ivars

    def locals(self) -> set[str]:
        locals = set()
        for arg in self.args:
            locals = locals.union(arg.locals())
        return locals

    def pretty_print(self, indent: int) -> str:
        return f"{bcolors.OKGREEN}{self.p}{bcolors.ENDC}({', '.join([arg.pretty_print(indent) for arg in self.args])})"


class Unification(ASTNode):
    def __init__(self, left: ASTNode, right: ASTNode):
        self.left = left
        self.right = right

    def codeG(self, addressSpace: dict[str, int]) -> CompilationResult:

        if type(self.left) == Variable:
            name = self.left.X
            code = [I1P(I1P.I.PUTVAR, addressSpace[name]),
                    self.right.codeA(addressSpace),
                    I0P(I0P.I.BIND)]

            return makeCompilationResult(code, f"Unification", self)
        elif type(self.left) == InitializedVariable:
            name = self.left.X
            code = [I1P(I1P.I.PUTREF, addressSpace[name]),
                    self.right.codeU(addressSpace)]

            return makeCompilationResult(code, f"Unification", self)

    def ivars(self) -> set[str]:
        return self.left.ivars().union(self.right.ivars())

    def locals(self) -> set[str]:
        return self.left.locals().union(self.right.locals())

    def codeU(self, addressSpace: dict[str, int]) -> CompilationResult:
        pass

    def pretty_print(self, indent: int) -> str:
        return f"{self.left.pretty_print(indent)} = {self.right.pretty_print(indent)}"


class Clause(ASTNode):
    def __init__(self, head:  Literal, goals: List[ASTNode]):
        self.head = head
        self.goals = goals

    def codeC(self) -> CompilationResult:

        addressSpace = {}
        for arg in self.head.args:
            addressSpace[arg.X] = len(addressSpace)+1
        for goal in self.goals:
            for arg in (goal.locals()):
                if arg not in addressSpace:
                    addressSpace[arg] = len(addressSpace)+1

        body = []
        for node in self.goals:
            body.append(node.codeG(addressSpace))

        m = len(addressSpace)

        code = [I1P(I1P.I.PUSHENV, m), *body, I0P(I0P.I.POPENV)]

        return makeCompilationResult(code, f"Clause", self)

    def ivars(self) -> set[str]:
        s = self.head.ivars()
        for goal in self.goals:
            s = s.union(goal.ivars())
        return s

    def locals(self) -> set[str]:
        s = self.head.locals()
        for goal in self.goals:
            s = s.union(goal.locals())
        return s

    def codeU(self, addressSpace: dict[str, int]) -> CompilationResult:
        pass

    def pretty_print(self, indent: int) -> str:
        return f"{self.head.pretty_print(indent)} :- {', '.join([node.pretty_print(indent) for node in self.goals])}"


class Predicate(ASTNode):
    def __init__(self, clauses: List[Clause]):
        self.clauses = clauses

    def codeP(self) -> CompilationResult:
        name = f"{self.clauses[0].head.p}/{len(self.clauses[0].head.args)}"

        if len(self.clauses) == 1:
            code = [I1P(I1P.I.JUMP_TARGET, name), self.clauses[0].codeC()]
            return makeCompilationResult(code, f"Predicate {name}", self)

        else:
            try_clauses = []
            labels = []

            for clause in self.clauses[:-1]:
                Ai = label_generator()
                labels.append(Ai)
                try_clauses.append(I1P(I1P.I.TRY, Ai))

            labels.append(label_generator())

            code1 = [I1P(I1P.I.JUMP_TARGET, name), I0P(I0P.I.SETBTP), *
                     try_clauses, I0P(I0P.I.DELBTP), I1P(I1P.I.JUMP, labels[-1])]

            code2 = []
            for i, clause in enumerate(self.clauses):
                code2.append(I1P(I1P.I.JUMP_TARGET, labels[i]))
                code2.append(clause.codeC())

            return makeCompilationResult(code1+code2, f"Predicate {name}", self)

    def ivars(self) -> set[str]:
        s = set()
        for clause in self.clauses:
            s = s.union(clause.ivars())
        return s

    def locals(self) -> set[str]:
        s = set()
        for clause in self.clauses:
            s = s.union(clause.locals())
        return s

    def codeU(self, addressSpace: dict[str, int]) -> CompilationResult:
        pass

    def pretty_print(self, indent: int) -> str:
        return f"{NEWLINE.join([clause.pretty_print(indent) for clause in self.clauses])}"


class Program(ASTNode):
    def __init__(self, predicates: List[Predicate], query: Literal):
        self.predicates = predicates
        self.query = query

    def codeP(self) -> CompilationResult:
        A = label_generator()

        free_vars = self.query.locals()

        addressSpace = {}
        for i, arg in enumerate(free_vars):
            addressSpace[arg] = i+1

        d = len(addressSpace)

        init = [I1P(I1P.I.INIT, A), I1P(I1P.I.PUSHENV, d),
                self.query.codeG(addressSpace), I1P(I1P.I.HALT, d)]

        preds = [I1P(I1P.I.JUMP_TARGET, A), I0P(I0P.I.NO)]

        for pred in self.predicates:
            preds.append(pred.codeP())

        return makeCompilationResult(init+preds, f"Program", self)

    def ivars(self) -> set[str]:
        s = set()
        for pred in self.predicates:
            s = s.union(pred.ivars())
        return s

    def locals(self) -> set[str]:
        s = set()
        for pred in self.predicates:
            s = s.union(pred.locals())
        return s

    def pretty_print(self, indent: int) -> str:
        return f"{NEWLINE.join([pred.pretty_print(indent) for pred in self.predicates])}{NEWLINE}  ? {self.query.pretty_print(indent)}"
