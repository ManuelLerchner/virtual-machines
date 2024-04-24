from Nodes import BinaryOperation, UnaryOperator, Assignment, Variable, Number, StatementSequence, Comma, If, IfElse, Print, While, For, DeclareVariable, ArrayAccess, Dereference, AddressOf
from Instructions import Instructions
from Instructions import Instructions0Params as I0P, Instructions1Params as I1P
from State import State
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

if __name__ == '__main__':
    variable_adress: dict[str, AdressEntry] = {}
    variable_values: dict[str, int] = {}

    code = dot_product_example.code(variable_adress, 0)

    s = State(code)

    s.stack.initVariables(variable_adress, variable_values)

    print(dot_product_example, "\n")
    print(code, "\n")

    s.run(debug=False)

    assert s.stack.to_list()[-1] == 28

    print("\nResult:", s.stack.to_list()[-1]
          if s.stack.SP >= 0 else "Empty stack")
