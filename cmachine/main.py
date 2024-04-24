from Nodes import BinaryOperation, UnaryOperator, Assignment, Variable, Number, StatementSequence, Comma, If, IfElse, Print, While, For, DeclareVariable, ArrayAccess, Dereference, AddressOf, DeclareStruct, StructAccess, Malloc
from Instructions import Instructions
from Instructions import Instructions0Params as I0P, Instructions1Params as I1P
from State import State


if __name__ == '__main__':

    expr = StatementSequence(
        DeclareVariable("int*", 1, 1, "a",
                        StatementSequence(
                            Assignment(Variable("a"), Malloc(Number(10))),
                            DeclareVariable("int", 1, 1, "i",
                                            StatementSequence(
                                                For(
                                                    Assignment(
                                                        Variable("i"), Number(0)),
                                                    BinaryOperation(
                                                        Variable("i"), I0P.I.LEQ, Number(9)),
                                                    Assignment(Variable("i"),
                                                               BinaryOperation(
                                                        Variable("i"), I0P.I.ADD, Number(1))),
                                                    StatementSequence(
                                                        Assignment(
                                                            ArrayAccess(
                                                                Variable("a"), Variable("i")),
                                                            Variable("i")),



                                                    )),
                                                Print(ArrayAccess(
                                                    Variable("a"), Number(5))),
                                                DeclareVariable("int*", 1, 1, "b",
                                                                StatementSequence(
                                                                    Assignment(
                                                                        Variable("b"), AddressOf(ArrayAccess(Variable("a"), Number(6)))),
                                                                    Print(Dereference(
                                                                        Variable("b"))),

                                                                )
                                                                ))
                                            ))))

    variable_adress: dict[str, int] = {}
    variable_values: dict[str, int] = {}

    code = expr.code(variable_adress, 0)

    s = State(code)

    s.stack.initVariables(variable_adress, variable_values)

    print(expr, "\n")
    print(code, "\n")

    s.run(debug=False)
