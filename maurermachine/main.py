from Nodes import *
from Instructions import Instructions0Params as I0P, Instructions1Params as I1P
from Interpreter import Interpreter


if __name__ == '__main__':

    expr = LetIn([
        (Variable("a"),
         BinaryOperation(
            BaseType(19),
            I0P.I.ADD,
            BaseType(23)
        ))],
        BinaryOperation(
        Variable("a"),
        I0P.I.MUL,
        BaseType(2)
    )
    )

    variable_adress: dict[str, (chr, int)] = {
    }

    print(expr, "\n")

    code = expr.codeB(variable_adress, 0)

    print(f"Code: [{len(code)} instructions]\n{code}\n")

    s = Interpreter(code)

    s.run(debug=True, pretty=False)

    print("Exit code: ", s.stack.stack[0], "\n")
