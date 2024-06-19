from typing import Tuple, List
from enum import Enum, auto
from classes.basic import Basic, BasicArray
from utils import replaceParametrsCalls, extractVectorSize, vectorSize2AplanVectorSize


class DeclTypes(Enum):
    WIRE = auto()
    INT = auto()
    REG = auto()
    INPORT = auto()
    OUTPORT = auto()
    IF_STATEMENT = auto()

    def checkType(type_str: str):
        if type_str == "int":
            return DeclTypes.INT
        return DeclTypes.INT


class Declaration(Basic):
    def __init__(
        self,
        data_type: DeclTypes,
        identifier: str,
        expression: str,
        size_expression: str,
        size: int,
        dimension_expression: str,
        dimension_size: int,
        source_interval: Tuple[int, int],
    ):
        super().__init__(identifier, source_interval)
        self.data_type = data_type
        self.expression = expression
        self.size = size
        self.size_expression = size_expression
        self.dimension_expression = dimension_expression
        self.dimension_size = dimension_size

    def getAplanDecltype(self):
        if self.data_type == DeclTypes.INT:
            return "int"
        elif (
            self.data_type == DeclTypes.INPORT
            or self.data_type == DeclTypes.OUTPORT
            or self.data_type == DeclTypes.WIRE
            or self.data_type == DeclTypes.REG
        ):
            if self.dimension_size > 0:
                return f"(Bits {self.size}) -> Bits {self.dimension_size}"
            elif self.size > 0:
                return "Bits " + str(self.size)
            else:
                return "bool"

    def __repr__(self):
        return f"\tDeclaration({self.data_type!r}, {self.identifier!r}, {self.expression!r}, {self.size!r}, {self.sequence!r})\n"


class DeclarationArray(BasicArray):
    def __init__(self):
        super().__init__(Declaration)

    def addElement(self, new_element: Declaration):
        if isinstance(new_element, self.element_type):
            self.elements.append(new_element)
            self.elements = sorted(
                self.elements,
                key=lambda element: len(element.identifier),
                reverse=True,
            )
            return self.getElementIndex(new_element.identifier)
        else:
            raise TypeError(
                f"Object should be of type {self.element_type} but you passed an object of type {type(new_element)}. \n Object: {new_element}"
            )

    def getDeclarationsWithExpressions(self):
        result = []
        for element in self.elements:
            if len(element.expression) > 0:
                result.append(element)
        return result

    def recalculateSizeExpressions(self, parametrs):
        for element in self.elements:
            if len(element.size_expression) > 0:
                expression = replaceParametrsCalls(parametrs, element.size_expression)
                vector_size = extractVectorSize(expression)
                aplan_vector_size = [0]
                if vector_size is not None:
                    aplan_vector_size = vectorSize2AplanVectorSize(
                        vector_size[0], vector_size[1]
                    )
                element.size = aplan_vector_size[0]

    def isIncludeInputPorts(self):
        for element in self.elements:
            if element.data_type == DeclTypes.INPORT:
                return True
        return False

    def getInputPorts(self):
        result: List[Declaration] = []
        for element in self.elements:
            if element.data_type == DeclTypes.INPORT:
                result.append(element)
        return result

    def isIncludeOutputPorts(self):
        for element in self.elements:
            if element.data_type == DeclTypes.OUTPORT:
                return True
        return False

    def getOutputPorts(self):
        result: List[Declaration] = []
        for element in self.elements:
            if element.data_type == DeclTypes.OUTPORT:
                result.append(element)
        return result

    def __repr__(self):
        return f"DeclarationsArray(\n{self.elements!r}\n)"
