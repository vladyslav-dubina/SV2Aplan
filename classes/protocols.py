import re
from typing import Tuple, List
from classes.action_parametr import ActionParametrArray
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
        self.body: List[Tuple[Basic | None, str, ElementsTypes]] = []
        self.parametrs: ActionParametrArray = ActionParametrArray()

    def copy(self):
        protocol = Protocol(self.identifier, self.source_interval, self.element_type)
        for element in self.body:
            protocol.body.append(element)
        protocol.parametrs.copy()
        return protocol

    def setBody(self, body: Tuple[Basic | None, str, ElementsTypes]):
        self.body.clear()
        self.body.append(body)

    def addBody(self, body: Tuple[Basic | None, str, ElementsTypes]):
        self.body.append(body)

    def getName(self):
        if self.number is None:
            if self.parametrs.getLen() > 0:
                return "{0}({1})".format(self.identifier, str(self.parametrs))
            else:
                return self.identifier
        else:
            return "{0}_{1}{2}".format(
                self.identifier, self.number, str(self.parametrs)
            )

    def __str__(self):
        body_to_str = ""
        for index, body_element in enumerate(self.body):
            protocol_element = False
            element, element_str, element_type = body_element
            if index != 0:
                if self.element_type == ElementsTypes.GENERATE_ELEMENT:
                    body_to_str += " || "
                else:
                    prev_element, prev_element_str, prev_element_type = self.body[
                        index - 1
                    ]
                    if element_type == ElementsTypes.FOREVER_ELEMENT:
                        body_to_str += ";"
                    elif prev_element_type == ElementsTypes.ACTION_ELEMENT and (
                        element_type == ElementsTypes.ACTION_ELEMENT
                        or element_type == ElementsTypes.PROTOCOL_ELEMENT
                    ):
                        body_to_str += "."
                    else:
                        protocol_element = True
                        body_to_str += ";"

            if element is not None:
                element_str = re.sub(
                    r"\b{}\b".format(re.escape(element.identifier)),
                    element.getName(),
                    element_str,
                )

            if element_type == ElementsTypes.FOREVER_ELEMENT:
                body_to_str += "{" + element_str + "}"
            elif protocol_element == False:
                body_to_str += element_str
            else:
                body_to_str += "(" + element_str + ")"
            if index == len(self.body) - 1:
                body_to_str += ","

        if self.parametrs.getLen() > 0:
            return "{0} = {1}".format(
                self.getName(),
                body_to_str,
            )
        else:
            return "{0} = {1}".format(
                self.getName(),
                body_to_str,
            )

    def __repr__(self):
        return f"\tProtocol({self.identifier!r}, {self.sequence!r})\n"


class ProtocolArray(BasicArray):
    def __init__(self):
        super().__init__(Protocol)

    def copy(self):
        new_aray: ProtocolArray = ProtocolArray()
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def getProtocolsInStrFormat(self):
        result = ""
        for element in self.elements:
            result += "\n"
            result += str(element)
        result = removeTrailingComma(result)
        return result

    def __repr__(self):
        return f"ProtocolsArray(\n{self.elements!r}\n)"
