from typing import Tuple
from classes.basic import Basic, BasicArray
from classes.element_types import ElementsTypes
from utils.string_formating import addEqueToBGET
from utils.utils import isNumericString


class Node(Basic):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        super().__init__(identifier, source_interval, element_type)
        self.expression: str | None = None
        self.module_name: str | None = None
        self.bit_selection: str | None = None
        self.range_selection: str | None = None

    def getName(self) -> str:
        result = self.identifier
        if self.module_name:
            result = "{0}.{1}".format(self.module_name, result)
        if self.range_selection:
            result = "{0}({1})".format(result, self.range_selection)
        if self.bit_selection:
            if isNumericString(self.bit_selection):
                result = "{0}({1})".format(result, self.bit_selection)
            else:
                result = "BGET({0}, {1})".format(result, self.bit_selection)
        return result

    def __str__(self) -> str:
        return self.identifier


class NodeArray(BasicArray):
    def __init__(self, node_type: ElementsTypes):
        super().__init__(Node)
        self.node_type = node_type

    def __str__(self) -> str:
        result = ""
        for index, element in enumerate(self.elements):
            bracket_flag = False
            if index != 0:
                previus_element = self.elements[index - 1]
                if (
                    "~" in previus_element.identifier
                    or "!" in previus_element.identifier
                ):
                    result += "("
                    bracket_flag = True
                else:
                    result += " "

            identifier = str(element.getName())
            if self.element_type == ElementsTypes.PRECONDITION_ELEMENT:

                identifier = addEqueToBGET(identifier)

            result += identifier

            if bracket_flag:
                result += ")"

        return result

    def getElementByIndex(self, index) -> Node:
        return self.elements[index]
