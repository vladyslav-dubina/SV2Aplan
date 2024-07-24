from typing import Tuple
from classes.basic import Basic, BasicArray
import re


class NameChange(Basic):
    def __init__(
        self, identifier: str, source_interval: Tuple[int, int], original_name: str
    ):
        super().__init__(identifier, source_interval)
        self.original_name = original_name

    def copy(self):
        return NameChange(self.identifier, self.source_interval, self.original_name)

    def __repr__(self):
        return f"NameChange(\t{self.identifier!r}, {self.original_name!r}\n)"


class NameChangeArray(BasicArray):
    def __init__(self):
        super().__init__(NameChange)

    def copy(self):
        new_aray: NameChangeArray = NameChangeArray()
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def addElement(self, new_element: NameChange):
        if isinstance(new_element, self.element_type):
            is_uniq_element = self.findElement(new_element.identifier)
            if is_uniq_element is not None:
                return self.getElementIndex(is_uniq_element.identifier)

            self.elements.append(new_element)
            self.elements = sorted(
                self.elements,
                key=lambda element: len(element.identifier),
                reverse=True,
            )
            return self.getElementIndex(new_element.identifier)
        else:
            raise TypeError(
                f"Object should be of type {self.element_type} but you passed an object of type {type(new_element)}. \n Object: {new_element}"
            )

    def deleteElement(self, identifier: str | None):
        if identifier is not None:
            element = self.findElement(identifier)
            if element is not None:
                self.elements.remove(element)

    def changeNamesInStr(self, expression: str):
        for elem in self.elements:
            expression = re.sub(
                r"\b{}\b".format(re.escape(elem.original_name)),
                "{}".format(elem.identifier),
                expression,
            )
        return expression

    def __repr__(self):
        return f"NameChangeArray(\n{self.elements!r}\n)"
