from typing import Tuple
from classes.structure import Structure


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
            result = "Sensetive({0}, {1})".format(self.getName(), self.sensetive)
        else:
            result = "{0}".format(self.getName())
        return result

    def __repr__(self):
        return f"\tAlways({self.identifier!r}, {self.sensetive!r}, {self.sequence!r})\n"
