import re
from typing import Tuple, List
from classes.basic import Basic, BasicArray
from utils.string_formating import removeTrailingComma


class ActionParametr(Basic):
    def __init__(
        self,
        identifier: str,
        type: str,
    ):
        self.type = type
        self.uniq_identifier = ""
        super().__init__(identifier, (0, 0))

    def __str__(self) -> str:
        return f"{self.uniq_identifier}:{self.type}"

    def __repr__(self):
        return f"\ActionParametr({self.identifier!r}, {self.type!r})\n"


class ActionParametrArray(BasicArray):
    def __init__(self):
        super().__init__(ActionParametr)

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