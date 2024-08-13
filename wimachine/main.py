from Nodes import *
from Instructions import Instructions0Params as I0P, Instructions1Params as I1P
from Interpreter import Interpreter


def makeList(args: List[ASTNode]) -> ASTNode:
    if len(args) == 0:
        return Constructor("NIL", [])
    else:
        return Constructor("CONS", [args[0], makeList(args[1:])])


listcompose = Program(
    [
        Predicate([
            Clause(Literal("app", [Variable("X"), Variable("Y"), Variable("Z")]), [
                Unification(InitializedVariable("X"),
                            Constructor("NIL", [])),
                Unification(InitializedVariable("Y"),
                            InitializedVariable("Z"))
            ]),
            Clause(Literal("app", [Variable("X"), Variable("Y"), Variable("Z")]), [
                Unification(InitializedVariable("X"), Constructor(
                    "CONS", [Variable("H"), Variable("X'")])),
                Unification(InitializedVariable("Z"), Constructor(
                    "CONS", [InitializedVariable("H"), Variable("Z'")])),
                Literal("app", [InitializedVariable("X'"),
                                InitializedVariable("Y"), InitializedVariable("Z'")])

            ])
        ]),
    ],
    Literal("app", [Variable("X"),
                    Variable("Y"),
                    makeList([Atom("a"), Atom("b"), Atom(
                        "d"), Atom("e"), Atom("f")])
                    ])
)

test = Program(
    [
        Predicate([
            Clause(Literal("t", [Variable("X")]), [
                Unification(InitializedVariable("X"), Atom("b"))]),
        ]),
        Predicate([
            Clause(Literal("p", []), [
                Literal("q", [Variable("X")]),
                Literal("t", [InitializedVariable("X")])
            ])]),
        Predicate([
            Clause(Literal("q", [Variable("X")]), [
                Literal("s", [InitializedVariable("X")])
            ])]),
        Predicate([
            Clause(Literal("s", [Variable("X")]), [
                Literal("t", [InitializedVariable("X")])]),
            Clause(Literal("s", [Variable("X")]), [
                Unification(InitializedVariable("X"), Atom("a"))
            ])
        ])
    ],
    Literal("p", [])
)


if __name__ == '__main__':

    expr = test

    print(expr, "\n")

    comp_result = expr.code()
    comp_result_json = comp_result.to_json()

    with open("comp_result.json", "w") as f:
        f.write(comp_result_json)

    code = comp_result.to_code()

    print(f"Code: [{len(code)} instructions]\n{code}\n")

    s = Interpreter(code)

    s.run(debug=True, pretty=False)
