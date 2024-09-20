from typing import Tuple
from classes.basic import Basic, BasicArray

from classes.element_types import ElementsTypes


class ProcessedElement(Basic):
    def __init__(self, identifier: str, source_interval: Tuple[int, int]):
        super().__init__(identifier, source_interval)

    def copy(self):
        processed_element = ProcessedElement(self.identifier, self.source_interval)
        processed_element.number = self.number
        return processed_element

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

    def getElementsIE(
        self,
        include: ElementsTypes | None = None,
        exclude: ElementsTypes | None = None,
        include_identifier: str | None = None,
        exclude_identifier: str | None = None,
    ):
        result: ProcessedElementArray = ProcessedElementArray()
        elements = self.elements

        if (
            include is None
            and exclude is None
            and include_identifier is None
            and exclude_identifier is None
        ):
            return self.copy()

        for element in elements:
            if include is not None and element.element_type is not include:
                continue
            if exclude is not None and element.element_type is exclude:
                continue
            if (
                include_identifier is not None
                and element.identifier is not include_identifier
            ):
                continue
            if (
                exclude_identifier is not None
                and element.identifier is exclude_identifier
            ):
                continue

            result.addElement(element)

        return result

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
