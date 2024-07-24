from typing import Tuple
from classes.basic import Basic, BasicArray
import re


class ProcessedElement(Basic):
    def __init__(self, identifier: str, source_interval: Tuple[int, int]):
        super().__init__(identifier, source_interval)

    def copy(self):
        return ProcessedElement(self.identifier, self.source_interval)

    def __repr__(self):
        return f"ProcessedElement(\t{self.identifier!r}, {self.source_interval!r}\n)"


class ProcessedElementArray(BasicArray):
    def __init__(self):
        super().__init__(ProcessedElement)

    def copy(self):
        new_aray: ProcessedElementArray = ProcessedElementArray()
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def addElement(self, new_element: ProcessedElement):
        if isinstance(new_element, self.element_type):
            if new_element not in self.elements:
                self.elements.append(new_element)
                return self.getElementIndex(new_element.identifier)
        else:
            raise TypeError(
                f"Object should be of type {self.element_type} but you passed an object of type {type(new_element)}. \n Object: {new_element}"
            )

    def isInProcessedElementAlready(self, source_interval: Tuple[int, int]):
        for elem in self.elements:
            if source_interval == elem.source_interval:
                return True
        return False

    def __repr__(self):
        return f"ProcessedElementArray(\n{self.elements!r}\n)"
