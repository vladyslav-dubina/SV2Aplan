from typing import Tuple
from classes.basic import Basic, BasicArray
from classes.element_types import ElementsTypes


class CondPredicate(Basic):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
        name_space_level: int = 0,
    ):
        super().__init__(identifier, source_interval, element_type)
        self.name_space_level = name_space_level

    def copy(self):
        cond = CondPredicate(
            self.identifier,
            self.source_interval,
            self.element_type,
        )
        return cond

    def __repr__(self):
        return f"\CondPredicate({self.identifier!r}, {self.element_type!r}, level:{self.name_space_level!r}, {self.source_interval!r})\n"


class CondPredicateArray(BasicArray):
    def __init__(self):
        super().__init__(CondPredicate)

    def copy(self):
        new_aray: CondPredicateArray = CondPredicateArray()
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def addElement(self, new_element: CondPredicate):
        if isinstance(new_element, self.element_type):
            self.elements.append(new_element)
            return self.getElementIndex(new_element.identifier)
        else:
            raise TypeError(
                f"Object should be of type {self.element_type} but you passed an object of type {type(new_element)}. \n Object: {new_element}"
            )

    def getElementsIE(
        self,
        include: ElementsTypes | None = None,
        exclude: ElementsTypes | None = None,
        include_identifier: str | None = None,
        exclude_identifier: str | None = None,
    ):
        result: CondPredicateArray = CondPredicateArray()
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

    def getLastElement(self) -> CondPredicate | None:
        if self.getLen() > 0:
            return self.elements[self.getLen() - 1]
        else:
            return None

    def __repr__(self):
        return f"CondPredicateArray(\n{self.elements!r}\n)"
