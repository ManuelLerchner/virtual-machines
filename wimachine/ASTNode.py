import io
from abc import abstractmethod, ABCMeta
import json
from Instructions import Instructions, Instructions0Params as I0P, Instructions1Params as I1P


LABEL_COUNTER = 0


def base10ToBase26Letter_A_is_ONE(num):  # 1-based
    ''' Converts any positive integer to Base26(letters only) with no 0th
    case. Useful for applications such as spreadsheet columns to determine which
    Letterset goes with a positive integer.

    Returns just uppercase letters.
    '''
    if num <= 0:
        return ""
    s = ""
    while num:
        num, rem = divmod(num - 1, 26)
        s = chr(65 + rem) + s
    return s


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
            "description": "".join(strip_ansi_colour(self.description)),
            "description_node": "".join(strip_ansi_colour(self.node.pretty_print(0))) if self.node is not None else None,
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
    def codeA(self, addressSpace: dict[str, int]) -> CompilationResult:
        """
        Compute value store it in the heap, returns reference on stack
        """
        pass

    # @abstractmethod
    def codeG(self, addressSpace: dict[str, int]) -> CompilationResult:
        """
        Compute value store it in the heap, returns reference on stack
        """
        pass

    def codeU(self, addressSpace: dict[str, int]) -> CompilationResult:
        """
        Compute value store it in the heap, returns reference on stack
        """
        pass

    def codeC(self) -> CompilationResult:
        """
        Compile clause
        """
        pass

    def codeP(self) -> CompilationResult:
        """
        Compile clause
        """
        pass

    def ivars(self) -> set[str]:
        """
        Returns set of all variables initialized variables
        """
        pass

    def locals(self) -> set[str]:
        """
        Returns set of all variables initialized variables
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
