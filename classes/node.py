from enum import Enum, auto
from typing import Tuple
from classes.basic import Basic, BasicArray
from classes.element_types import ElementsTypes
from utils.string_formating import addEqueToBGET
from utils.utils import containsOnlyPipe, isNumericString


class RangeTypes(Enum):
    START = auto()
    END = auto()
    UNDEFINED = auto()
    START_END = auto()


class Node(Basic):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int] = (0, 0),
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        super().__init__(identifier, source_interval, element_type)
        self.expression: str | None = None
        self.module_name: str | None = None
        self.bit_selection: bool = False
        self.range_selection: RangeTypes = RangeTypes.UNDEFINED

    def copy(self):
        node = Node(self.identifier, self.source_interval, self.element_type)
        node.expression = self.expression
        node.module_name = self.module_name
        node.bit_selection = self.bit_selection
        node.range_selection = self.range_selection

        return node

    def getName(self) -> str:
        result = self.identifier
        if self.module_name:
            result = "{0}.{1}".format(self.module_name, result)
        if self.range_selection == RangeTypes.START_END:
            result = "({0})".format(result)
        if self.range_selection == RangeTypes.START:
            result = "({0}".format(result)
        if self.range_selection == RangeTypes.END:
            result = "{0})".format(result)
        if self.bit_selection:
            if isNumericString(self.identifier):
                result = "({0})".format(result)
            else:
                result = ", {0})".format(result)
        return result

    def __str__(self) -> str:
        return self.identifier


class NodeArray(BasicArray):
    def __init__(self, node_type: ElementsTypes):
        super().__init__(Node)
        self.node_type = node_type

    def __str__(self) -> str:
        result = ""
        negation_operators = "~!"
        bracket_flag = False
        for index, element in enumerate(self.elements):

            if index != 0:
                if (
                    bracket_flag
                    and element.element_type is ElementsTypes.OPERATOR_ELEMENT
                ):
                    result += ")"
                    bracket_flag = False

                if (
                    element.element_type is ElementsTypes.DOT_ELEMENT
                    or element.element_type is ElementsTypes.SEMICOLON_ELEMENT
                ):
                    pass
                else:
                    previus_element = self.elements[index - 1]
                    if previus_element.element_type is ElementsTypes.DOT_ELEMENT:
                        pass
                    elif (
                        element.bit_selection
                        or element.range_selection == RangeTypes.START_END
                        or element.range_selection == RangeTypes.START
                        or element.range_selection == RangeTypes.END
                    ):
                        pass
                    else:
                        if "(" not in element.identifier:
                            if previus_element.identifier in negation_operators:
                                result += "("
                                bracket_flag = True
                            else:
                                if (
                                    "(" in previus_element.identifier
                                    or ")" in element.identifier
                                ):
                                    bracket_flag = False
                                    pass
                                else:
                                    result += " "
                        else:
                            result += " "

            identifier = str(element.getName())
            if element.element_type is ElementsTypes.ARRAY_ELEMENT:
                identifier = identifier + ".value"
            if element.element_type is ElementsTypes.ARRAY_SIZE_ELEMENT:
                identifier = identifier + ".size"

            if index + 1 < len(self.elements):
                next_element = self.getElementByIndex(index + 1)
                if next_element.bit_selection:
                    if isNumericString(next_element.identifier) is None:
                        identifier = "BGET({0}".format(identifier)

            if self.element_type == ElementsTypes.PRECONDITION_ELEMENT:

                identifier = addEqueToBGET(identifier)

            if containsOnlyPipe(identifier) and (
                previus_element.element_type is ElementsTypes.OPERATOR_ELEMENT
            ):

                identifier = "{0} {1}".format(
                    self.getElementByIndex(0).getName(), identifier
                )

            if "++" in str(element.identifier):
                result += "= {0} + 1".format(previus_element.getName())

            elif "--" in str(element.identifier):
                result += "= {0} - 1".format(previus_element.getName())

            else:
                if element.element_type is ElementsTypes.SEMICOLON_ELEMENT:
                    if index != self.getLen() - 1:
                        result += f"{identifier}\n\t\t"
                else:
                    result += identifier

            if bracket_flag and index == len(self.elements) - 1:
                result += ")"
                bracket_flag = False

        return result

    def getElementByIndex(self, index) -> Node:
        return self.elements[index]
