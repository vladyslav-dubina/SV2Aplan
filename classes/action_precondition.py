import re
from typing import Tuple, List
from classes.basic import Basic, BasicArray
from utils.string_formating import removeTrailingComma


class ActionPrecondition(Basic):
    def __init__(
        self,
        precondition: str,
    ):
        self.precondition = precondition
        super().__init__("", (0, 0))

    def findAndChangeNamesToUniqNames(self, identifier, uniq_identifier):
        self.precondition = re.sub(
            r"\b{}\b".format(re.escape(identifier)),
            "{}".format(uniq_identifier),
            self.precondition,
        )

    def __str__(self) -> str:
        return self.precondition

    def __repr__(self):
        return f"\ActionPrecondition({self.identifier!r}, {self.precondition!r})\n"


class ActionPreconditionArray(BasicArray):
    def __init__(self):
        super().__init__(ActionPrecondition)

    def __str__(self):
        result = ""
        for index, element in enumerate(self.getElements()):
            if index != 0:
                result += ";"
            result += str(element)
        return result

    def __repr__(self):
        return f"ActionPreconditionArray(\n{self.elements!r}\t)"
