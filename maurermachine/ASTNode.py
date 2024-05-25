import io
from abc import abstractmethod, ABCMeta
import json
from Instructions import Instructions, Instructions0Params as I0P, Instructions1Params as I1P


LABEL_COUNTER = 0


def base10ToBase26Letter_A_is_ONE(num):  # 1-based
    ''' Converts any positive integer to Base26(letters only) with no 0th
    case. Useful for applications such as spreadsheet columns to determine which
    Letterset goes with a positive integer.
    '''
    if num <= 0:
        return ""
    s = ""
    while (num > 0):
        s += (chr(97+(num-1) % 26))
        num -= 1
        num //= 26
    return s[::-1]


def label_generator():
    global LABEL_COUNTER
    LABEL_COUNTER += 1
    return f"{base10ToBase26Letter_A_is_ONE(LABEL_COUNTER)}"


def strip_ansi_colour(text: str) -> iter:
    """Strip ANSI colour sequences from a string.

    Args:
        text (str): Text string to be stripped.

    Returns:
        iter[str]: A generator for each returned character. Note,
        this will include newline characters.

    """
    buff = io.StringIO(text)
    while (b := buff.read(1)):
        if b == '\x1b':
            while (b := buff.read(1)) != 'm':
                continue
        else:
            yield b


class CompilationResult:
    def __init__(self, code: list, description: str, node):
        self.code = code
        self.description = description
        self.node = node

    def to_map(self):
        children = []

        for i in self.code:
            if type(i) == CompilationResult:
                children.append(i.to_map())
            else:
                children.append("".join(strip_ansi_colour(str(i))))

        data = {
            "description": self.description,
            "description_node": self.node.pretty_print(0) if self.node is not None else None,
            "code": children
        }

        return data

    def to_json(self):
        map = self.to_map()
        string = json.dumps(map, indent=4)

        return string

    def to_code(self):
        code = []
        for i in self.code:
            if type(i) == CompilationResult:
                code += i.to_code()
            else:
                code.append(i)
        return code


class ASTNode(metaclass=ABCMeta):
    def __init__(self, node_type, children=None):
        self.node_type = node_type
        self.children = children if children is not None else []

    # @abstractmethod
    def codeV(self, addressSpace: dict[str, int], sd: int) -> CompilationResult:
        """
        Compute value store it in the heap, returns reference on stack
        """
        pass

    def codeB(self, addressSpace: dict[str, int], sd: int) -> CompilationResult:
        """
        Compute Base value and store it on the stack
        """
        return makeCompilationResult([self.codeV(addressSpace, sd), I0P(I0P.I.GETBASIC)], f"Base value", self)

    def codeC(self, addressSpace: dict[str, int], sd: int) -> CompilationResult:
        """
        Stores a closure on the heap and returns a reference on the stack
        """
        freeVars = self.getFreeVariables(set())
        new_address_space = addressSpace.copy()
        code_globals = []
        for i, var in enumerate(freeVars):
            new_address_space[var] = ("G", i)
            code_globals.append(*getvar(var, addressSpace, sd+i))

        A = label_generator()
        B = label_generator()

        body = self.codeV(new_address_space, 0)

        res_code = [*code_globals] + [I1P(I1P.I.MKVEC, len(freeVars)), I1P(I1P.I.MKCLOS, A), I1P(I1P.I.JUMP, B), I1P(
            I1P.I.JUMP_TARGET, A)] + [body] + [I0P(I0P.I.UPDATE), I1P(I1P.I.JUMP_TARGET, B)]

        return makeCompilationResult(res_code, f"Closure", self)

    @abstractmethod
    def getFreeVariables(boundVars: set[str]) -> set[str]:
        """
        Stores a closure on the heap and returns a reference on the stack
        """
        pass

    @abstractmethod
    def pretty_print(self):
        pass

    def __repr__(self):
        return self.pretty_print(0)


def makeCompilationResult(code, description: str, node: ASTNode) -> CompilationResult:
    if type(code) == list:
        return CompilationResult([*code], description,  node)
    if type(code) == CompilationResult:
        return code
    else:
        raise Exception("Unknown type")


def getvar(x, addressSpace, sd):
    t, v = addressSpace[x]
    if t == "L":
        code = [I1P(I1P.I.PUSHLOC, sd-v)]
    elif t == "G":
        code = [I1P(I1P.I.PUSHGLOB, v)]

    return code
