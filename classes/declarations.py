from typing import Tuple, List
from enum import Enum, auto
from classes.actions import Action
from classes.basic import Basic, BasicArray
from classes.element_types import ElementsTypes

from utils.string_formating import replaceValueParametrsCalls
from utils.utils import extractVectorSize, vectorSize2AplanVectorSize


class DeclTypes(Enum):
    WIRE = auto()
    INT = auto()
    REG = auto()
    LOGIC = auto()
    INPORT = auto()
    OUTPORT = auto()
    STRING = auto()
    BIT = auto()
    ENUM = auto()
    ENUM_TYPE = auto()
    STRUCT_TYPE = auto()
    UNION_TYPE = auto()
    STRUCT = auto()
    UNION = auto()
    CLASS = auto()
    TIME = auto()
    REAL = auto()
    ARRAY = auto()
    NONE = auto()

    def checkType(type_str: str, types):
        from classes.module import Module

        if "int" == type_str:
            return DeclTypes.INT
        if "real" == type_str:
            return DeclTypes.REAL
        elif "time" == type_str:
            return DeclTypes.TIME
        elif "reg" == type_str:
            return DeclTypes.REG
        elif "logic" == type_str:
            return DeclTypes.LOGIC
        elif "wire" == type_str:
            return DeclTypes.WIRE
        elif "string" == type_str:
            return DeclTypes.STRING
        elif "bit" == type_str:
            return DeclTypes.BIT
        else:
            for type in types:
                if isinstance(type, Module):
                    if type_str == type.ident_uniq_name:
                        return DeclTypes.CLASS
                else:
                    if type_str == type.identifier:
                        if type.data_type is DeclTypes.ENUM_TYPE:
                            return DeclTypes.ENUM
                        elif type.data_type is DeclTypes.STRUCT_TYPE:
                            return DeclTypes.STRUCT
                        elif type.data_type is DeclTypes.UNION_TYPE:
                            return DeclTypes.UNION

        return DeclTypes.NONE


class AplanDeclType(Enum):
    STRUCT = auto()
    PARAMETRS = auto()
    NONE = auto()


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
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
        action: Action | None = None,
        struct_name: str | None = None,
    ):
        super().__init__(identifier, source_interval, element_type)
        self.data_type = data_type
        self.expression = expression
        self.size = size
        self.size_expression = size_expression
        self.dimension_expression = dimension_expression
        self.dimension_size = dimension_size
        self.action: Action | None = action
        self.file_path: str = ""
        self.struct_name: str = struct_name

    def copy(self):
        declaration = Declaration(
            self.data_type,
            self.identifier,
            self.expression,
            self.size_expression,
            self.size,
            self.dimension_expression,
            self.dimension_size,
            self.source_interval,
            self.element_type,
            self.action,
        )
        declaration.number = self.number
        return declaration

    def getAplanDecltype(self, type: AplanDeclType = AplanDeclType.NONE):
        result = ""
        if type is AplanDeclType.STRUCT:
            result += f"{self.identifier}:"

        if self.data_type == DeclTypes.INT:
            if self.dimension_size > 0:
                result += "(int) -> int"
            else:
                result += "int"
        elif self.data_type == DeclTypes.REAL:
            if self.dimension_size > 0:
                result += "(float) -> float"
            else:
                result += "float"
        elif self.data_type == DeclTypes.ARRAY:
            result += f"{self.size_expression}"
        elif (
            self.data_type == DeclTypes.INPORT
            or self.data_type == DeclTypes.OUTPORT
            or self.data_type == DeclTypes.WIRE
            or self.data_type == DeclTypes.REG
            or self.data_type == DeclTypes.LOGIC
        ):
            if self.dimension_size > 0:
                if type is AplanDeclType.PARAMETRS:
                    result += "Bits " + str(self.size)
                else:
                    result += f"(Bits {self.size}) -> Bits {self.dimension_size}"

            elif self.size > 0:
                result += "Bits " + str(self.size)
            else:
                result += "bool"
        elif self.data_type == DeclTypes.ENUM_TYPE:
            result += ""
        elif self.data_type == DeclTypes.CLASS:
            result += f"{self.size_expression}"
        elif self.data_type == DeclTypes.STRING:
            result += "string"
        elif (
            self.data_type == DeclTypes.ENUM
            or self.data_type == DeclTypes.STRUCT
            or self.data_type == DeclTypes.UNION
        ):
            result += f"{self.size_expression}"
        elif self.data_type == DeclTypes.TIME:
            result += "Bits " + str(64)
        return result

    def __repr__(self):
        return f"\tDeclaration({self.data_type!r}, {self.identifier!r}, {self.expression!r}, {self.size!r}, {self.dimension_size!r}, {self.sequence!r})\n"


class DeclarationArray(BasicArray):
    def __init__(self):
        super().__init__(Declaration)

    def copy(self):
        new_aray: DeclarationArray = DeclarationArray()
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def getElementByIndex(self, index) -> Declaration:
        return self.elements[index]

    def getElementsIE(
        self,
        include: ElementsTypes | None = None,
        exclude: ElementsTypes | None = None,
        include_identifier: str | None = None,
        exclude_identifier: str | None = None,
        file_path: str | None = None,
        data_type_incude: DeclTypes | None = None,
        data_type_exclude: DeclTypes | None = None,
    ):
        result: DeclarationArray = DeclarationArray()
        elements = self.elements

        if (
            include is None
            and exclude is None
            and include_identifier is None
            and exclude_identifier is None
            and file_path is None
            and data_type_incude is None
            and data_type_exclude is None
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

            if file_path is not None and element.file_path is not file_path:
                continue

            if (
                data_type_incude is not None
                and element.data_type is not data_type_incude
            ):
                continue

            if data_type_exclude is not None and element.data_type is data_type_exclude:
                continue

            result.addElement(element)
        return result

    def findElementWithSource(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
    ):
        for element in self.elements:
            if (
                element.identifier == identifier
                or element.source_interval == source_interval
            ):
                return element
        return None

    def addElement(self, new_element: Declaration):
        if isinstance(new_element, self.element_type):
            is_uniq_element = self.findElementWithSource(
                new_element.identifier, new_element.source_interval
            )
            if is_uniq_element is not None:
                return (False, self.getElementIndex(is_uniq_element.identifier))

            self.elements.append(new_element)
            self.elements = sorted(
                self.elements,
                key=lambda element: len(element.identifier),
                reverse=True,
            )
            return (True, self.getElementIndex(new_element.identifier))
        else:
            raise TypeError(
                f"Object should be of type {self.element_type} but you passed an object of type {type(new_element)}. \n Object: {new_element}"
            )

    def getDeclarationsWithExpressions(self):
        result = []
        for element in self.elements:
            if len(element.expression) > 0 and element.data_type != DeclTypes.ENUM_TYPE:
                result.append(element)
        return result

    def getInputPorts(self):
        result: List[Declaration] = []
        for element in self.elements:
            if element.data_type == DeclTypes.INPORT:
                result.append(element)
        return result

    def findDeclWithDimentionByName(
        self,
        identifier: str,
    ):
        element = self.findElement(identifier)
        if element is not None:
            if element.dimension_size > 0:
                return element
        return None

    def __repr__(self):
        return f"DeclarationsArray(\n{self.elements!r}\n)"
