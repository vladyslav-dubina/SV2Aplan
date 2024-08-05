from typing import Tuple
from classes.basic import Basic, BasicArray
from classes.element_types import ElementsTypes


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

    def getName(self) -> str:
        if self.module_name:
            return "{0}.{1}".format(self.module_name, self.identifier)
        else:
            return self.identifier

    def __str__(self) -> str:
        return self.identifier


class NodeArray(BasicArray):
    def __init__(self):
        super().__init__(Node)

    def __str__(self) -> str:
        result = ""
        for index, element in enumerate(self.elements):
            if index != 0:
                result += " "
            result += str(element.getName())

        return result

    def getElementByIndex(self, index) -> Node:
        return self.elements[index]
