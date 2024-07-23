from typing import List, Tuple
from classes.element_types import ElementsTypes


class Basic:
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        from classes.counters import CounterTypes
        from utils.utils import Counters_Object

        self.identifier = identifier
        self.sequence = (Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),)
        self.source_interval: Tuple[int, int] = source_interval
        self.element_type: ElementsTypes = element_type

    def __repr__(self):
        return f"\tBasic({self.identifier!r}, {self.sequence!r}, {self.source_interval!r})\n"


class BasicArray:
    def __init__(self, element_type: Basic):
        self.elements: List[Basic] = []
        self.element_type: Basic = element_type

    def addElement(self, new_element: Basic):
        if isinstance(new_element, self.element_type):
            self.elements.append(new_element)
            return self.getLen() - 1
        else:
            raise TypeError(
                f"Object should be of type {self.element_type} but you passed an object of type {type(new_element)}. \n Object: {new_element}"
            )

    def findElement(
        self,
        identifier: str,
    ):
        for element in self.elements:
            if element.identifier == identifier:
                return element
        return None

    def getElementIndex(
        self,
        identifier: str,
    ):
        for index, element in enumerate(self.elements):
            if element.identifier == identifier:
                return index
        return None

    def getElement(
        self,
        identifier: str,
    ):
        for element in self.elements:
            if element.identifier == identifier:
                return element
        return None

    def getElementByIndex(self, index):
        return self.elements[index]

    def removeElement(self, element):
        self.elements.remove(element)

    def getElements(self):
        return self.elements

    def getLen(self):
        return len(self.elements)

    def __repr__(self):
        return f"ElementArray(\n{self.elements!r}\t)"
