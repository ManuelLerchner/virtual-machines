from Nodes import *
from Instructions import Instructions0Params as I0P, Instructions1Params as I1P
from Interpreter import Interpreter


if __name__ == '__main__':

    expr = LetIn([
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

    variable_adress: dict[str, (chr, int)] = {
        "a": ('L', 1)
    }

    print(expr, "\n")

    code = expr.codeV(variable_adress, 1)

    print(f"Code: [{len(code)} instructions]\n{code}\n")

    s = Interpreter(code)

    s.run(debug=True)

    # print("Exit code: ", s.stack.stack[0], "\n")
