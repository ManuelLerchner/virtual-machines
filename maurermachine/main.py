from Nodes import *
from Instructions import Instructions0Params as I0P, Instructions1Params as I1P
from Interpreter import Interpreter


if __name__ == '__main__':

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
            Variable("fac"), [BaseType(5)]
    )
    )

    variable_adress: dict[str, (chr, int)] = {
        "a": ('L', 1)
    }

    print(expr, "\n")

    code = expr.codeV(variable_adress, 0)

    print(f"Code: [{len(code)} instructions]\n{code}\n")

    s = Interpreter(code)

    s.run(debug=True, pretty=True)

    # print("Exit code: ", s.stack.stack[0], "\n")
