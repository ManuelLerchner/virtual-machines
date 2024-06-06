from Nodes import *

a = Program(
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
