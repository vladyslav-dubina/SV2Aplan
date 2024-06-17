from typing import Tuple
from classes.basic import Basic, BasicArray


class Parametr(Basic):
    def __init__(
        self, identifier: str, sequence: int, source_interval: Tuple[int, int]
    ):
        super().__init__(identifier, sequence, source_interval)

    def __repr__(self):
        return f"\tParametr({self.identifier!r})\n"
    
class ParametrArray(BasicArray):
    def __init__(self):
        super().__init__(Parametr)

    def __repr__(self):
        return f"ParametrsArray(\n{self.elements!r}\n)"
