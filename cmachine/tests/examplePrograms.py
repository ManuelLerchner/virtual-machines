from Nodes import Arrow, BinaryOperation, FunctionCall, FunctionDefinition, Program, Return, UnaryOperator, Assignment, Variable, Number, StatementSequence, Comma, If, IfElse, Print, While, For, DeclareVariable, ArrayAccess, Dereference, AddressOf, DeclareStruct, StructAccess, Malloc
from Instructions import Instructions
from Instructions import Instructions0Params as I0P, Instructions1Params as I1P
from cmachine.Interpreter import Interpreter
from ASTNode import AdressEntry

# int[4] x;
# int[4] y;
# int i;
# for (i = 0; (i lt 4); i = (i add 1))
#   x[i] = i
#   y[i] = (i mul 2)
# int dot_product;
# for (i = 0; (i lt 4); i = (i add 1))
#   dot_product = (dot_product add (x[i] mul y[i]))
dot_product_example = DeclareVariable("int", 1, 4, "x",
                                      DeclareVariable("int", 1, 4, "y",
                                                      StatementSequence(
                                                          DeclareVariable("int", 1, 1, "i",
                                                                          StatementSequence(
                                                                              For(
                                                                                  Assignment(
                                                                                      Variable("i"), Number(0)),
                                                                                  BinaryOperation(
                                                                                      Variable("i"), I0P.I.LT, Number(4)),
                                                                                  Assignment(Variable("i"), BinaryOperation(
                                                                                      Variable("i"), I0P.I.ADD, Number(1))),
                                                                                  StatementSequence(
                                                                                      Assignment(ArrayAccess(
                                                                                          "x", Variable("i")), Variable("i")),
                                                                                      Assignment(ArrayAccess(
                                                                                          "y", Variable("i")), BinaryOperation(
                                                                                          Variable("i"), I0P.I.MUL, Number(2))
                                                                                      )
                                                                                  )
                                                                              ),
                                                                              DeclareVariable("int", 1, 1, "dot_product",
                                                                                              For(
                                                                                                  Assignment(
                                                                                                      Variable("i"), Number(0)),
                                                                                                  BinaryOperation(
                                                                                                      Variable("i"), I0P.I.LT, Number(4)),
                                                                                                  Assignment(Variable("i"), BinaryOperation(
                                                                                                      Variable("i"), I0P.I.ADD, Number(1))),
                                                                                                  StatementSequence(
                                                                                                      Assignment(
                                                                                                          Variable(
                                                                                                              "dot_product"),
                                                                                                          BinaryOperation(
                                                                                                              Variable(
                                                                                                                  "dot_product"),
                                                                                                              I0P.I.ADD,
                                                                                                              BinaryOperation(
                                                                                                                  ArrayAccess(
                                                                                                                      "x", Variable("i")),
                                                                                                                  I0P.I.MUL,
                                                                                                                  ArrayAccess(
                                                                                                                      "y", Variable("i"))
                                                                                                              )
                                                                                                          )))
                                                                                              ))
                                                                          )
                                                                          )
                                                      ))
                                      )

pointer = StatementSequence(
    DeclareStruct("t", [
        DeclareVariable("int", 1, 7, "a", StatementSequence()),
        DeclareVariable("t*", 1, 1, "b", StatementSequence()),
    ],
        "str",
        DeclareVariable("t*", 1, 1, "ptr",
                        StatementSequence(
                            Assignment(
                                    Variable(
                                        "t*", "ptr"), AddressOf(Variable("t", "str"))
                            ),
                            Assignment(

                                ArrayAccess(
                                    Arrow(Variable("t*", "ptr"), "a"), Number(5)), Number(7)),

                            Print(ArrayAccess(
                                Arrow(Variable("t*", "ptr"), "a"), Number(5)))
                        )
                        ))
)

fib = Program([], [
    FunctionDefinition("int", "fac", [
        DeclareVariable("int", 1, 1, "x", StatementSequence())
    ],
        IfElse(
        BinaryOperation(
            Variable("int", "x"), I0P.I.LEQ, Number(0)),
        Return(Number(1)),
        Return(BinaryOperation(
            Variable("int", "x"),
            I0P.I.MUL,
            FunctionCall(Variable("*fac(int)", "fac"), [BinaryOperation(
                Variable("int", "x"), I0P.I.SUB, Number(1))])
        ))
    )
    ),
    FunctionDefinition("int", "main", [],
                       DeclareVariable("int", 1, 1, "res",
                                       StatementSequence(
                                           Assignment(Variable("int", "res"),
                                                      FunctionCall(Variable("*fac(int)", "fac"), [Number(8)])),

                                           Return(Variable("int", "res")))
                                       )
                       )

])

if __name__ == '__main__':
    variable_adress: dict[str, AdressEntry] = {}
    variable_values: dict[str, int] = {}

    code = dot_product_example.code(variable_adress, 0)

    s = Interpreter(code)

    s.stack.initVariables(variable_adress, variable_values)

    print(dot_product_example, "\n")
    print(code, "\n")

    s.run(debug=False)

    assert s.stack.to_list()[-1] == 28

    print("\nResult:", s.stack.to_list()[-1]
          if s.stack.SP >= 0 else "Empty stack")
