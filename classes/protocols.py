from typing import Tuple, List
from classes.basic import Basic, BasicArray
from utils.string_formating import removeTrailingComma
from classes.element_types import ElementsTypes


class Protocol(Basic):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        super().__init__(identifier, source_interval, element_type)
        self.body: List[Tuple[str, ElementsTypes]] = []

    def identifierToBody(self):
        self.body.insert(0, (self.identifier, ElementsTypes.PROTOCOL_ELEMENT))
        self.identifier = ""

    def setIdentifier(self, identifier: str):
        self.identifier = identifier

    def setBody(self, body: Tuple[str, ElementsTypes]):
        self.body.clear()
        self.body.append(body)

    def addBody(self, body: Tuple[str, ElementsTypes]):
        self.body.append(body)

    def __str__(self):
        body_to_str = ""
        for index, body_element in enumerate(self.body):
            protocol_element = False
            element, element_type = body_element
            if index != 0:
                if self.element_type == ElementsTypes.GENERATE_ELEMENT:
                    body_to_str += " || "
                else:
                    prev_element, prev_element_type = self.body[index - 1]
                    if prev_element_type == ElementsTypes.ACTION_ELEMENT and (
                        element_type == ElementsTypes.ACTION_ELEMENT
                        or element_type == ElementsTypes.PROTOCOL_ELEMENT
                    ):
                        body_to_str += "."
                    else:
                        protocol_element = True
                        body_to_str += ";"
            if protocol_element == False:
                body_to_str += element
            else:
                body_to_str += "(" + element + ")"
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
