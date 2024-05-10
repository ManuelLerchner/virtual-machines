from abc import abstractmethod, ABCMeta

from Instructions import Instructions, Instructions0Params


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
        return [*self.codeV(addressSpace, sd), Instructions0Params(Instructions0Params.I.GETBASIC)]
        pass

    # @abstractmethod
    def codeC(self, addressSpace: dict[str, int], sd: int) -> list[Instructions]:
        """
        Stores a closure on the heap and returns a reference on the stack
        """
        pass

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
