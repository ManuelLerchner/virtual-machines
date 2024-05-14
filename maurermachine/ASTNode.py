from abc import abstractmethod, ABCMeta

from Instructions import Instructions, Instructions0Params as I0P, Instructions1Params as I1P


def getvar(x, addressSpace, sd):
    t, v = addressSpace[x]
    if t == "L":
        return [I1P(I1P.I.PUSHLOC, sd-v)]
    elif t == "G":
        return [I1P(I1P.I.PUSHGLOB, v)]


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


class ASTNode(metaclass=ABCMeta):
    def __init__(self, node_type, children=None):
        self.node_type = node_type
        self.children = children if children is not None else []

    # @abstractmethod
    def codeV(self, addressSpace: dict[str, int], sd: int) -> list[Instructions]:
        """
        Compute value store it in the heap, returns reference on stack
        """
        pass

    def codeB(self, addressSpace: dict[str, int], sd: int) -> list[Instructions]:
        """
        Compute Base value and store it on the stack
        """
        return [*self.codeV(addressSpace, sd), I0P(I0P.I.GETBASIC)]

    def codeC(self, addressSpace: dict[str, int], sd: int) -> list[Instructions]:
        """
        Stores a closure on the heap and returns a reference on the stack
        """
        freeVars = self.getFreeVariables(set())
        new_address_space = {}
        code = []
        for i, var in enumerate(freeVars):
            code += getvar(var, addressSpace, sd+i)
            new_address_space[var] = ("G", i)

        A = label_generator()
        B = label_generator()

        return code + [I1P(I1P.I.MKVEC, len(freeVars)), I1P(I1P.I.MKCLOS, A), I1P(I1P.I.JUMP, B), I1P(I1P.I.JUMP_TARGET, A)] + self.codeV(new_address_space, 0) + [I0P(I0P.I.UPDATE), I1P(I1P.I.JUMP_TARGET, B)]

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
