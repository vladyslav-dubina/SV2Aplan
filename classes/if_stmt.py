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
        self.step = 1

        self.left_cond = BodyElementArray()
        self.right_cond = BodyElementArray()

    def setCondCount(self, if_count: int, else_count: int):
        self.else_count = else_count
        self.if_count = if_count
        self.step = 1

    def __repr__(self):
        return f"\IfStmt({self.identifier!r}, {self.sequence!r})\n"
