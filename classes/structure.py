from typing import Tuple, List
from classes.parametrs import ParametrArray
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
        self.parametrs: ParametrArray = ParametrArray()
        self.additional_params: str | None = None

    def copy(self):
        struct = Structure(self.identifier, self.source_interval, self.element_type)
        for element in self.behavior:
            struct.behavior.append(element.copy())
        struct.elements = self.elements.copy()
        struct.parametrs = self.parametrs.copy()
        struct.additional_params = self.additional_params
        struct.number = self.number
        return struct

    def updateLinks(self, module):
        for element in self.behavior:
            element.updateLinks(module)

    def setNumber(self, number):
        self.setNumberToProtocols(number)
        self.number = number

    def getName(self, params_include: bool = True):
        identifier = self.identifier

        if self.number:
            identifier = "{0}_{1}".format(identifier, self.number)
        if params_include == True:
            if self.additional_params is not None:
                identifier = "{0}({1})".format(identifier, self.additional_params)
            elif self.parametrs.getLen() > 0:
                identifier = "{0}({1})".format(identifier, str(self.parametrs))
        return identifier

    def setNumberToProtocols(self, number):
        for element in self.behavior:
            element.number = number

    def getLastBehaviorIndex(self):
        if not self.behavior:
            return None
        return len(self.behavior) - 1

    def insertBehavior(self, index: int, element: Protocol):
        self.behavior.insert(index, element)

    def addProtocol(
        self,
        protocol_identifier: str,
        element_type: ElementsTypes | None = None,
        parametrs: ParametrArray | None = None,
        inside_the_task: bool = False,
    ):
        tmp: ParametrArray = ParametrArray()
        if inside_the_task is False:
            if self.parametrs is not None:
                tmp += self.parametrs
            if parametrs is not None:
                tmp += parametrs
        else:
            tmp = parametrs
        self.behavior.append(Protocol(protocol_identifier, (0, 0), element_type, tmp))
        return len(self.behavior) - 1

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
        if self.number is None:
            return f"\tStructure({self.identifier!r}, {self.sequence!r})\n"
        else:
            return (
                f"\tStructure({self.identifier!r}_{self.number!r}, {self.sequence!r})\n"
            )


class StructureArray(BasicArray):
    def __init__(self, element_type: Basic | None = None):
        if element_type is None:
            super().__init__(Structure)
        else:
            super().__init__(element_type)

    def copy(self):
        new_aray: StructureArray = StructureArray()
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def getElementsIE(
        self,
        include: ElementsTypes | None = None,
        exclude: ElementsTypes | None = None,
        include_identifier: str | None = None,
        exclude_identifier: str | None = None,
    ):
        result: StructureArray = StructureArray()
        elements = self.elements

        if (
            include is None
            and exclude is None
            and include_identifier is None
            and exclude_identifier is None
        ):
            return self.copy()

        for element in elements:
            if include is not None and element.element_type is not include:
                continue
            if exclude is not None and element.element_type is exclude:
                continue
            if (
                include_identifier is not None
                and element.identifier is not include_identifier
            ):
                continue
            if (
                exclude_identifier is not None
                and element.identifier is exclude_identifier
            ):
                continue

            result.addElement(element)

        return result

    def updateLinks(self, module):
        for element in self.getElements():
            element.updateLinks(module)

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
