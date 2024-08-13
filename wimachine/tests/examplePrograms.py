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


relatives = Program(
    [
        Predicate([
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("manuel"))]),
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("simone"))]),
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("evi"))]),
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("elias"))]),
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("hannes"))]),
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("irmgard"))]),
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("elmar"))]),
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("elisabeth"))]),
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("oswald"))]),
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("maria"))]),
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("peter"))]),
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("frida"))]),
            Clause(Literal("person", [Variable("X")]), [
                   Unification(InitializedVariable("X"), Atom("hansl"))]),
        ]),
        Predicate([
            # manuel - irmgard
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("manuel")),
                Unification(InitializedVariable("P"), Atom("irmgard")),
            ]),
            # manuel - elmar
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("manuel")),
                Unification(InitializedVariable("P"), Atom("elmar")),
            ]),
            # simone - irmgard
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("simone")),
                Unification(InitializedVariable("P"), Atom("irmgard")),
            ]),
            # simone - elmar
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("simone")),
                Unification(InitializedVariable("P"), Atom("elmar")),
            ]),
            # evi - elisabeth
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("evi")),
                Unification(InitializedVariable("P"), Atom("elisabeth")),
            ]),
            # evi - oswald
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("evi")),
                Unification(InitializedVariable("P"), Atom("oswald")),
            ]),
            # elias - elisabeth
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("elias")),
                Unification(InitializedVariable("P"), Atom("elisabeth")),
            ]),
            # elias - oswald
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("elias")),
                Unification(InitializedVariable("P"), Atom("oswald")),
            ]),
            # hannes - elisabeth
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("hannes")),
                Unification(InitializedVariable("P"), Atom("elisabeth")),
            ]),
            # hannes - oswald
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("hannes")),
                Unification(InitializedVariable("P"), Atom("oswald")),
            ]),
            # irmgard - maria
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("irmgard")),
                Unification(InitializedVariable("P"), Atom("maria")),
            ]),
            # irmgard - peter
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("irmgard")),
                Unification(InitializedVariable("P"), Atom("peter")),
            ]),
            # elmar - frida
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("elmar")),
                Unification(InitializedVariable("P"), Atom("frida")),
            ]),
            # elmar - hansl
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("elmar")),
                Unification(InitializedVariable("P"), Atom("hansl")),
            ]),
            # oswald - frida
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("oswald")),
                Unification(InitializedVariable("P"), Atom("frida")),
            ]),
            # oswald - hansl
            Clause(Literal("is_child", [Variable("C"), Variable("P")]), [
                Unification(InitializedVariable("C"), Atom("oswald")),
                Unification(InitializedVariable("P"), Atom("hansl")),
            ]),
        ]),
        # sibling
        Predicate([
            Clause(Literal("sibling", [Variable("X"), Variable("Y")]), [
                Literal("is_child", [InitializedVariable("X"), Variable("P")]),
                Literal("is_child", [InitializedVariable(
                    "Y"), InitializedVariable("P")]),
            ]),
        ]),
        # grandis_child
        Predicate([
            Clause(Literal("grandson", [Variable("X"), Variable("Y")]), [
                Literal("is_child", [InitializedVariable("X"), Variable("P")]),
                Literal("is_child", [InitializedVariable(
                    "P"), InitializedVariable("Y")]),
            ]),
        ]),
        # ancestor
        Predicate([
            Clause(Literal("ancestor", [Variable("X"), Variable("Y")]), [
                Literal("is_child", [InitializedVariable(
                    "Y"), InitializedVariable("X")]),
            ]),
            Clause(Literal("ancestor", [Variable("X"), Variable("Y")]), [
                Literal("is_child", [InitializedVariable(
                    "Y"), Variable("Z")]),
                Literal("ancestor", [InitializedVariable(
                    "X"), InitializedVariable("Z")]),
            ]),
        ]),
        # descendant
        Predicate([
            Clause(Literal("descendant", [Variable("X"), Variable("Y")]), [
                Literal("ancestor", [InitializedVariable(
                    "Y"), InitializedVariable("X")]),
            ]),
        ]),
        # cousin
        Predicate([
            Clause(Literal("cousin", [Variable("X"), Variable("Y")]), [
                Literal("is_child", [InitializedVariable("X"), Variable("P")]),
                Literal("is_child", [InitializedVariable("Y"), Variable("Q")]),
                Literal("sibling", [InitializedVariable(
                    "P"), InitializedVariable("Q")]),
            ]),
        ]),
        # probably married
        Predicate([
            Clause(Literal("probably_married", [Variable("X"), Variable("Y")]), [
                Literal("is_child", [Variable("C"), InitializedVariable("X")]),
                Literal("is_child", [InitializedVariable(
                    "C"), InitializedVariable("Y")]),
            ]),
        ]),

    ],
    Literal("probably_married", [Variable("X"), Variable("Y")])
)


expr = Program(
    [
        Predicate([
            Clause(Literal("p", [Variable("X")]), [
                Unification(InitializedVariable("X"), Atom("a")),
            ])
        ]),


        Predicate([
            Clause(Literal("q1", [Variable("X"), Variable("Y")]), [
                Unification(InitializedVariable("Y"), Atom("a")),

            ])

        ]),
        Predicate([
            Clause(Literal("q2", [Variable("X"), Variable("Y")]), [
                Unification(InitializedVariable("Y"), Atom("b")),

            ])

        ]),


        Predicate([
            Clause(Literal("branch", [Variable("X"), Variable("Y")]), [
                Literal("p", [InitializedVariable("X")]),
                Cut(),
                Literal("q1", [InitializedVariable(
                    "X"), InitializedVariable("Y")]),
            ]),
            Clause(Literal("branch", [Variable("X"), Variable("Y")]), [
                Literal("q2", [InitializedVariable(
                    "X"), InitializedVariable("Y")]),
            ]),




        ]),

    ],
    Literal("branch", [Atom("b"), Variable("Y")])
)
