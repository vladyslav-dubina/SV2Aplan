from typing import Tuple, List
from classes.basic import Basic, BasicArray
from classes.protocols import Protocol
from classes.element_types import ElementsTypes


class Structure(Basic):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        super().__init__(identifier, source_interval, element_type)
        self.behavior: List[Protocol] = []
        self.elements: BasicArray = BasicArray(Basic)

    def getLastBehaviorIndex(self):
        if not self.behavior:
            return None
        return len(self.behavior) - 1

    def addProtocol(
        self, protocol_identifier: str, element_type: ElementsTypes | None = None
    ):
        self.behavior.append(Protocol(protocol_identifier, (0, 0), element_type))
        return len(self.behavior) - 1

    def getBehInStrFormat(self):
        result = ""
        if len(self.behavior) > 0:
            result = "{0} = ".format(self.identifier)
            for index, element in enumerate(self.behavior):
                if index != 0:
                    result += ",\n"
                result += str(element)
        return result

    def getBehLen(self):
        return len(self.behavior)

    def __str__(self):
        result = ""

        if len(self.behavior) >= 1:
            for element in self.behavior:
                result += "\n"
                result += str(element)
        return result

    def __repr__(self):
        return f"\tStructure({self.identifier!r}, {self.sequence!r})\n"


class StructureArray(BasicArray):
    def __init__(self, element_type: Basic | None = None):
        if element_type is None:
            super().__init__(Structure)
        else:
            super().__init__(element_type)

    def getAlwaysList(self):
        from classes.always import Always

        result: List[Always] = []
        for element in self.elements:
            if isinstance(element, Always) and len(element.behavior) >= 1:
                result.append(element)
        return result

    def getNoAlwaysStructures(self):
        from classes.always import Always

        result: List[Structure] = []
        for element in self.elements:
            if (
                isinstance(element, Always) == False
                and element.element_type is not ElementsTypes.TASK_ELEMENT
                and len(element.behavior) >= 1
            ):
                result.append(element)
        return result

    def getStructuresInStrFormat(self):
        result = ""
        for element in self.elements:
            result += str(element)
        return result

    def __repr__(self):
        return f"StructuresArray(\n{self.elements!r}\n)"
