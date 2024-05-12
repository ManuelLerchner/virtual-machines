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
