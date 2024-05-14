from Nodes import *
from Instructions import Instructions0Params as I0P, Instructions1Params as I1P
from Interpreter import Interpreter


if __name__ == '__main__':

    expr = LetRecIn([
        (Variable("fib"), Fun(
            [Variable("n")],

            IfThenElse(
                BinaryOperation(
                    Variable("n"),
                    I0P.I.LEQ,
                    BaseType(1)
                ),
                Variable("n"),

                BinaryOperation(
                    Apply(
                        Variable("fib"),
                        [BinaryOperation(
                            Variable("n"), I0P.I.SUB, BaseType(1)),
                         ]
                    ),
                    I0P.I.ADD,
                    Apply(
                        Variable("fib"),
                        [BinaryOperation(
                            Variable("n"), I0P.I.SUB, BaseType(2)),
                         ]
                    ))
            )))
    ],
        Apply(
        Variable("fib"), [

            BaseType(10)
        ]

    ))

    variable_adress: dict[str, (chr, int)] = {

    }

    print(expr, "\n")

    code = expr.codeV(variable_adress, 0)

    print(f"Code: [{len(code)} instructions]\n{code}\n")

    s = Interpreter(code)

    s.run(debug=False, pretty=False)

    print("Exit code: ", s.stack.stack[0], "\n")
