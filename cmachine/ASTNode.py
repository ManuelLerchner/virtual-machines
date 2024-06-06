from abc import abstractmethod, ABCMeta
import io
import json

from Instructions import Instructions, Instructions0Params


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

    @abstractmethod
    def codeR(self, addressSpace: dict[str, int], n) -> CompilationResult:
        pass

    @abstractmethod
    def codeL(self, addressSpace: dict[str, int], n) -> CompilationResult:
        pass

    @abstractmethod
    def pretty_print(self):
        pass

    @abstractmethod
    def getType(self):
        pass

    def __repr__(self):
        return self.pretty_print(0)

    def code(self, addressSpace: dict[str, int], n) -> CompilationResult:
        return makeCompilationResult([self.codeR(addressSpace, n), Instructions0Params(
            Instructions0Params.I.POP)], "Code", self)


def makeCompilationResult(code, description: str, node: ASTNode) -> CompilationResult:
    if type(code) == list:
        return CompilationResult([*code], description,  node)
    if type(code) == CompilationResult:
        return code
    else:
        raise Exception("Unknown type")
