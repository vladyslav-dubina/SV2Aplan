from typing import Tuple
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.structure import Structure


class LoopStmt(Structure):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        name_space_level: int,
    ):
        super().__init__(
            identifier,
            source_interval,
            element_type=ElementsTypes.LOOP_ELEMENT,
            name_space_level=name_space_level,
        )
        self.is_loop = True

    def __repr__(self):
        return f"\Loop({self.identifier!r}, {self.sequence!r})\n"


class ForeverStmt(Structure):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        name_space_level: int,
    ):
        super().__init__(
            identifier,
            source_interval,
            element_type=ElementsTypes.FOREVER_ELEMENT,
            name_space_level=name_space_level,
        )
        self.is_forever = True

    def __repr__(self):
        return f"\Forever({self.identifier!r}, {self.sequence!r})\n"


class WhileStmt(Structure):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        name_space_level: int,
    ):
        super().__init__(
            identifier,
            source_interval,
            element_type=ElementsTypes.WHILE_ELEMENT,
            name_space_level=name_space_level,
        )

        self.is_while = True


    def __repr__(self):
        return f"\While({self.identifier!r}, {self.sequence!r})\n"
