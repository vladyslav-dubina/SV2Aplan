from typing import Tuple
from classes.element_types import ElementsTypes
from classes.protocols import BodyElementArray
from classes.structure import Structure


class IfStmt(Structure):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        name_space_level: int,
    ):
        super().__init__(
            identifier,
            source_interval,
            element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
            name_space_level=name_space_level,
        )
        self.else_count = 0
        self.if_count = 0
        self.last_step = 0
        self.step = 1

    def setCondCount(self, if_count: int, else_count: int):
        self.else_count = else_count
        self.if_count = if_count
        if self.else_count == self.if_count:
            self.last_step = if_count + 1
        self.step = 1

    def __repr__(self):
        return f"\IfStmt({self.identifier!r}, {self.sequence!r})\n"
