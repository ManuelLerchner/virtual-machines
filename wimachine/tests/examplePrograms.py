from Nodes import *
from main import makeList

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
