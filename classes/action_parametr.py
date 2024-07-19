import re
from typing import Tuple, List
from classes.basic import Basic, BasicArray
from utils.string_formating import removeTrailingComma


class ActionParametr(Basic):
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
        self.uniq_identifier = action_name + ""
        super().__init__(identifier, source_interval)

    def __str__(self) -> str:
        if "var" in self.type:
            return f"{self.type} {self.identifier}"
        else:
            return f"{self.uniq_identifier}:{self.type}"

    def __repr__(self):
        return f"\ActionParametr({self.identifier!r}, {self.type!r})\n"


class ActionParametrArray(BasicArray):
    def __init__(self):
        super().__init__(ActionParametr)

    def parametrsCount(self):
        return len(self.elements)

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
        if parametrs_count <= self.parametrsCount():
            for index in range(parametrs_count):
                if index == 0:
                    result += "("

                if index != 0:
                    result += ", "
                result += self.elements[index].identifier
                if index == len(self.elements) - 1:
                    result += ")"
        else:
            raise ValueError(
                f"The number of arguments passed {self.parametrsCount()} is different from the number expected {parametrs_count}"
            )
        return result

    def generateUniqNamesForParamets(
        self,
    ):
        for index, element in enumerate(self.getElements()):
            element.uniq_identifier = self.generateParametrNameByIndex(index)

    def __str__(self):
        result = ""
        for index, element in enumerate(self.getElements()):
            if index != 0:
                result += ";"
            result += str(element)
        return result

    def __repr__(self):
        return f"ActionParametrArray(\n{self.elements!r}\t)"
