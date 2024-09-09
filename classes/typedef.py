from typing import Tuple
from classes.basic import Basic, BasicArray
from classes.declarations import AplanDeclType, DeclTypes, DeclarationArray
from classes.element_types import ElementsTypes


class Typedef(Basic):
    def __init__(
        self,
        identifier: str,
        unique_identifier: str,
        source_interval: Tuple[int, int],
        file_path: str,
        data_type: DeclTypes,
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        super().__init__(identifier, source_interval, element_type)
        self.declarations: DeclarationArray = DeclarationArray()
        self.file_path: str = file_path
        self.unique_identifier = unique_identifier
        self.data_type = data_type

    def copy(self):
        typedef = Typedef(
            self.identifier,
            self.unique_identifier,
            self.source_interval,
            self.file_path,
            self.data_type,
            self.element_type,
        )
        typedef.declarations = self.declarations.copy()
        return typedef

    def __str__(self) -> str:
        result = f"{self.unique_identifier}:"

        if self.data_type is DeclTypes.ENUM_TYPE:
            result += "("
            for index, element in enumerate(self.declarations.getElements()):
                if index != 0:
                    result += ",\n\t\t\t"

                result += element.getName()

            result += "\n\t\t)"

        elif self.data_type is DeclTypes.STRUCT_TYPE:
            result += "obj ("
            for index, element in enumerate(self.declarations.getElements()):
                if index != 0:
                    result += ",\n\t\t\t"

                result += element.getAplanDecltype(AplanDeclType.STRUCT)

            result += "\n\t\t)"
        return result

    def __repr__(self):
        return f"Typedef(\n\t\t{self.identifier!r},{self.unique_identifier!r},{self.file_path!r}\n)"


class TypedefArray(BasicArray):
    def __init__(self):
        super().__init__(Typedef)

    def copy(self):
        new_aray: TypedefArray = TypedefArray()
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def getElementByIndex(self, index) -> Typedef:
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
        result: TypedefArray = TypedefArray()
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
        unique_identifier: str,
        source_interval: Tuple[int, int],
    ):
        for element in self.elements:
            if (
                element.identifier == identifier
                or element.source_interval == source_interval
                or element.unique_identifier == unique_identifier
            ):
                return element
        return None

    def addElement(self, new_element: Typedef):
        if isinstance(new_element, self.element_type):
            is_uniq_element = self.findElementWithSource(
                new_element.identifier,
                new_element.unique_identifier,
                new_element.source_interval,
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

    def __str__(self):
        result = ""
        for index, element in enumerate(self.getElements()):
            if index != 0:
                result += ",\n\t\t"
            else:
                result += "\t\t"

            result += str(element)
        return result

    def __repr__(self):
        return f"TypedefArray(\n{self.elements!r}\n)"
