from abc import abstractmethod, ABCMeta

from Instructions import Instructions, Instructions0Params
from collections import namedtuple


class AdressEntry:
    def __init__(self, typeSize, address):
        self.typeSize = typeSize
        self.address = address


class ASTNode(metaclass=ABCMeta):
    def __init__(self, node_type, children=None):
        self.node_type = node_type
        self.children = children if children is not None else []

    @abstractmethod
    def codeR(self, addressSpace: dict[str, AdressEntry], n) -> list[Instructions]:
        pass

    @abstractmethod
    def codeL(self, addressSpace: dict[str, AdressEntry], n) -> list[Instructions]:
        pass

    @abstractmethod
    def pretty_print(self):
        pass

    def __repr__(self):
        return self.pretty_print(0)

    def code(self, addressSpace: dict[str, AdressEntry], n) -> list[Instructions]:
        return [*self.codeR(addressSpace, n), Instructions0Params(
                Instructions0Params.I.POP)]
