from typing import Tuple
from classes.structure import Structure, StructureArray


class Always(Structure):
    def __init__(
        self,
        identifier: str,
        sensetive: str | None,
        source_interval: Tuple[int, int],
    ):
        super().__init__(identifier, source_interval)
        self.sensetive = sensetive

    def getSensetiveForB0(self):
        result = ""
        if self.sensetive is not None:
            result = "Sensetive({0}, {1})".format(self.identifier, self.sensetive)
        else:
            result = "Sensetive({0})".format(self.identifier)
        return result

    def __repr__(self):
        return f"\tAlways({self.identifier!r}, {self.sensetive!r}, {self.sequence!r})\n"


class AlwaysArray(StructureArray):
    def __init__(self):
        super().__init__(Always)

    def __repr__(self):
        return f"AlwaysArray(\n{self.elements!r}\n)"
