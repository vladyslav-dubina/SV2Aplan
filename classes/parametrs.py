import re
from typing import Tuple, List
from classes.basic import Basic, BasicArray
from utils.string_formating import removeTrailingComma


class Parametr(Basic):
    def __init__(
        self,
        identifier: str,
        type: str,
        source_interval: Tuple[int, int] = (0, 0),
        action_name: str = "",
    ):
        if len(action_name) > 0:
            action_name += "_"
        self.type = type
        self.unique_identifier = action_name + ""
        self.module_name: str | None = None
        super().__init__(identifier, source_interval)

    def copy(self):
        action_param = Parametr(self.identifier, self.type, self.source_interval)
        action_param.unique_identifier = self.unique_identifier
        action_param.number = self.number
        return action_param

    def __str__(self) -> str:
        if "var" in self.type:
            return f"{self.identifier}"
        else:
            return f"{self.unique_identifier}:{self.type}"

    def __repr__(self):
        return f"\Parametr({self.identifier!r}, {self.type!r})\n"


class ParametrArray(BasicArray):
    def __init__(self):
        super().__init__(Parametr)

    def copy(self):
        new_aray: ParametrArray = ParametrArray()
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def insert(self, index: int, element: Parametr):
        {self.elements.insert(index, element)}

    def addElement(self, new_element: Parametr):
        if isinstance(new_element, self.element_type):
            is_uniq_element = self.findElement(new_element.identifier)
            if is_uniq_element is not None:
                return (False, self.getElementIndex(is_uniq_element.identifier))

            self.elements.append(new_element)
            return (True, self.getElementIndex(new_element.identifier))
        else:
            raise TypeError(
                f"Object should be of type {self.element_type} but you passed an object of type {type(new_element)}. \n Object: {new_element}"
            )

    def generateParametrNameByIndex(self, index):
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        base = len(alphabet)
        name = ""

        while index >= 0:
            name = alphabet[index % base] + name
            index = index // base - 1

            if len(name) > 1 and name[0] == name[1]:
                current_index = alphabet.index(name[0])
                next_index = (current_index + 1) % len(alphabet)
                name = alphabet[next_index] + name[1:]

        return name

    def getIdentifiersListString(self, parametrs_count):
        result = ""
        if parametrs_count <= self.getLen():
            for index in range(parametrs_count):
                if index == 0:
                    result += "("

                if index != 0:
                    result += ", "
                result += self.elements[index].identifier
                if index == self.getLen() - 1:
                    result += ")"
        else:
            raise ValueError(
                f"The number of arguments passed {self.getLen()} is different from the number expected {parametrs_count}"
            )
        return result

    def generateUniqNamesForParamets(
        self,
    ):
        for index, element in enumerate(self.getElements()):
            element.unique_identifier = self.generateParametrNameByIndex(index)

    def __str__(self):
        result = ""
        for index, element in enumerate(self.getElements()):
            if index != 0:
                result += ", "
            result += str(element)
        return result

    def __repr__(self):
        return f"ParametrArray(\n{self.elements!r}\t)"
