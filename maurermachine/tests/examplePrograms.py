from Nodes import *
from Instructions import Instructions
from Instructions import Instructions0Params as I0P, Instructions1Params as I1P
from Interpreter import Interpreter
from ASTNode import AdressEntry

expr1 = LetIn(
    [(Variable("a"), BaseType(19)),
        (Variable("b"),  BinaryOperation(
            Variable("a"),
            I0P.I.MUL,
            Variable("a")
        ))],
    BinaryOperation(
        Variable("a"),
        I0P.I.ADD,
        Variable("b")
    ))


expr2 = LetIn([
    (Variable("a"), BaseType(17)),
    (Variable("f"), Fun(
        [Variable("b")],

        BinaryOperation(
            Variable("a"),
            I0P.I.ADD,
            Variable("b")
        )
    )),
],
    Apply(
    Variable("f"), [BaseType(42)]
))


expr = LetIn([
    (Variable("fac"),
     LetRecIn([
             (Variable("f"), Fun(
                 [Variable("x"), Variable("y")],

                 IfThenElse(
                     BinaryOperation(
                         Variable("y"),
                         I0P.I.LT,
                         BaseType(1)
                     ),
                     Variable("x"),

                     Apply(
                         Variable("f"),
                         [BinaryOperation(
                             Variable("x"), I0P.I.MUL, Variable("y")),

                          BinaryOperation(
                             Variable("y"),
                             I0P.I.SUB,
                             BaseType(1)
                         )]
                     )
                 )))
             ],
        Apply(
         Variable("f"), [BaseType(1)]
     )))],
    Apply(
    Variable("fac"), [BaseType(10)]
)
)
