from typing import Tuple
from classes.element_types import ElementsTypes
from classes.structure import Structure


class CaseStmt(Structure):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        name_space_level: int ,
    ):
        super().__init__(
            identifier,
            source_interval,
            element_type=ElementsTypes.CASE_STATEMENT_ELEMENT,
            name_space_level=name_space_level,
        )
        self.expression: str | None = None

    def __repr__(self):
        return (
            f"\CaseStmt({self.identifier!r}, {self.sensetive!r}, {self.sequence!r})\n"
        )
