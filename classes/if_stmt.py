from typing import List, Tuple
from classes.element_types import ElementsTypes
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
        self.init_predicate_count = 0
        self.cond_predicate_count = 0

    def setCondPredicateCount(self, count: int):
        self.init_predicate_count = count
        self.cond_predicate_count = count

    def __repr__(self):
        return f"\IfStmt({self.identifier!r}, {self.sequence!r})\n"
