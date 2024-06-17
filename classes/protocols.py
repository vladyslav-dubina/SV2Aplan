from typing import Tuple, List
from classes.basic import Basic, BasicArray
from classes.declarations import DeclTypes
from utils import removeTrailingComma


class Protocol(Basic):
    def __init__(
        self, identifier: str, sequence: int, source_interval: Tuple[int, int]
    ):
        super().__init__(identifier, sequence, source_interval)
        self.body: List[str] = []
        self.type: DeclTypes | None = None

    def setType(self, type: DeclTypes | None):
        self.type = type

    def identifierToBody(self):
        self.body.insert(0, self.identifier)
        self.identifier = ""

    def setIdentifier(self, identifier: str):
        self.identifier = identifier

    def setBody(self, body: str):
        self.body.clear()
        self.body.append(body)

    def addBody(self, body: str):
        self.body.append(body)

    def __str__(self):
        body_to_str = ""
        for index, elem in enumerate(self.body):
            if index != 0:
                body_to_str += "."
            body_to_str += elem
            if index == len(self.body) - 1:
                body_to_str += ","
        return "{0} = {1}".format(self.identifier, body_to_str)

    def __repr__(self):
        return f"\tProtocol({self.identifier!r}, {self.sequence!r})\n"
    
class ProtocolArray(BasicArray):
    def __init__(self):
        super().__init__(Protocol)

    def getProtocolsInStrFormat(self):
        result = ""
        for element in self.elements:
            result += "\n"
            result += str(element)
        result = removeTrailingComma(result)
        return result

    def __repr__(self):
        return f"ProtocolsArray(\n{self.elements!r}\n)"