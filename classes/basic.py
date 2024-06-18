from typing import List, Tuple


class Basic:
    def __init__(
        self, identifier: str, sequence: int, source_interval: Tuple[int, int]
    ):
        self.identifier = identifier
        self.sequence = sequence
        self.source_interval: Tuple[int, int] = source_interval

    def __repr__(self):
        return f"\tBasic{self.identifier!r}\n"


class BasicArray:
    def __init__(self, element_type: Basic):
        self.elements: List[Basic] = []
        self.element_type: Basic = element_type

    def addElement(self, new_element: Basic):
        if isinstance(new_element, self.element_type):
            self.elements.append(new_element)
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

    def removeElement(self, element):
        self.elements.remove(element)

    def getElements(self):
        return self.elements

    def getElementByIndex(self, index):
        return self.elements[index]

    def __repr__(self):
        return f"ElementArray(\n{self.elements!r}\t)"
