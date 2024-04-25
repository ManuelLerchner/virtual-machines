from Nodes import *
from Instructions import Instructions0Params as I0P, Instructions1Params as I1P
from Interpreter import Interpreter


if __name__ == '__main__':

    expr = Program([
        DeclareVariable("int", 1, 1, "out", StatementSequence())
    ], [
        FunctionDefinition("int", "fib", [
            DeclareVariable("int", 1, 1, "n", StatementSequence())
        ],
            IfElse(
            BinaryOperation(
                Variable("int", "n"), I0P.I.LEQ, Number(1)),
            Return(Variable("int", "n")),
            Return(BinaryOperation(
                FunctionCall(Variable("*fac(int)", "fib"), [BinaryOperation(
                    Variable("int", "n"), I0P.I.SUB, Number(1))]),
                I0P.I.ADD,
                FunctionCall(Variable("*fac(int)", "fib"), [BinaryOperation(
                    Variable("int", "n"), I0P.I.SUB, Number(2))])
            ))
        )
        ),
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

                           StatementSequence(
                               Assignment(Variable("int", "out"),
                                          FunctionCall(Variable("*fac(int)", "fib"), [Number(16)])),
            Print(Variable("int", "out")),
            Assignment(Variable("int", "out"),
                                   BinaryOperation(
                Variable("int", "out"),
                I0P.I.ADD,
                FunctionCall(
                    Variable("*fac(int)", "fac"), [Number(16)])
            )),
            Print(Variable("int", "out")),
                               Return(Variable("int", "out"))
        )
        )

    ])

    variable_adress: dict[str, (chr, int)] = {}

    print(expr, "\n")

    code = expr.code(variable_adress, 0)

    print(f"Code: [{len(code)} instructions]\n{code}\n")

    s = Interpreter(code)

    print("Running...\n")

    s.run(debug=False)

    print("Exit code: ", s.stack.stack[0], "\n")
