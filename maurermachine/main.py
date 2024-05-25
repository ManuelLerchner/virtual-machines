from Nodes import *
from Instructions import Instructions0Params as I0P, Instructions1Params as I1P
from Interpreter import Interpreter


if __name__ == '__main__':

    expr = LetRecIn(
        [(Variable("app"), Fun(
            [Variable("l"), Variable("y")],
            MatchList(
                Variable("l"),
                Variable("y"),
                [Variable("h"), Variable("t")],
                Cons(
                    Variable("h"),
                    Apply(
                        Variable("app"),
                        [Variable("t"), Variable("y")]
                    )
                )
            )
        ))
        ],
        LetRecIn(
            [(Variable("map"), Fun(
                [Variable("f"), Variable("l")],
                MatchList(
                    Variable("l"),
                    Nil(),
                    [Variable("h"), Variable("t")],
                    Cons(
                        Apply(Variable("f"), [Variable("h")]),
                        Apply(Variable("map"), [Variable("f"), Variable("t")])
                    )
                )
            ))],

            Apply(
                Variable("map"),
                [Fun([Variable("x")], Print(Variable("x"))),

                 Apply(
                    Variable("map"),
                    [Fun([Variable("x")], BinaryOperation(Variable("x"), I0P.I.MUL, Variable("x"))),
                     Apply(
                     Variable("app"),
                     [Cons(BaseType(1), Cons(BaseType(2), Cons(BaseType(3), Nil()))),
                      Cons(BaseType(4), Cons(BaseType(5), Cons(BaseType(6), Nil())))]
                     )])]
            )

        )

    )

    variable_adress: dict[str, (chr, int)] = {

    }

    print(expr, "\n")

    comp_result = expr.codeV(variable_adress, 0)

    comp_result_json = comp_result.to_json()

    with open("comp_result.json", "w") as f:
        f.write(comp_result_json)

    code = comp_result.to_code()

    print(f"Code: [{len(code)} instructions]\n{code}\n")

    s = Interpreter(code)

    s.run(debug=False, pretty=False)

    print("Exit code: ", s.stack.stack[0], "\n")
