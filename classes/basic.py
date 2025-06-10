from typing import List, Tuple
from classes.element_types import ElementsTypes
from utils.utils import Color, is_interval_contained, printWithColor


class Basic:
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        from classes.counters import CounterTypes
        from utils.utils import Counters_Object

        self.identifier = identifier
        self.sequence = (Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),)
        self.source_interval: Tuple[int, int] = source_interval
        self.element_type: ElementsTypes = element_type
        self.number: int | None = None

    def copy(self):
        basic = Basic(
            self.identifier,
            self.source_interval,
            self.element_type,
        )
        basic.number = self.number
        return basic

    def getName(self):
        if self.number is None:
            return self.identifier
        else:
            return "{0}_{1}".format(self.identifier, self.number)

    def __repr__(self):
        return f"\tBasic({self.identifier!r}, {self.sequence!r}, {self.source_interval!r})\n"


class BasicArray:
    def __init__(self, element_type: Basic):
        self.elements: List[Basic] = []
        self.element_type: Basic = element_type

    def checkSourceInteval(self, source_interval: Tuple[int, int]):
        for element in self.elements:
            if is_interval_contained(source_interval, element.source_interval):
                return False
        return True

    def copy(self):
        new_aray: BasicArray = BasicArray(Basic)
        for element in self.getElements():
            new_aray.addElement(element.copy())
        return new_aray

    def reverse(self):
        self.elements = list(reversed(self.elements))
        return self

    def reverse_copy(self):
        new_array = self.copy()
        new_array.elements = list(reversed(self.elements))
        return new_array

    def insert(self, index: int, element: Basic):
        self.elements.insert(index, element)

    def getElementsIE(
        self,
        include: ElementsTypes | None = None,
        exclude: ElementsTypes | None = None,
        include_identifier: str | None = None,
        exclude_identifier: str | None = None,
    ):
        result: BasicArray = BasicArray()
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

    def __iadd__(self, other):
        if isinstance(other, BasicArray):
            if self.element_type != other.element_type:
                printWithColor(
                    f"WARNING: Adding BasicArray of type {other.element_type} to BasicArray of type {self.element_type}.",
                    Color.YELLOW,
                )
            self.elements.extend(other.elements)
        elif isinstance(other, Basic):
            self.addElement(other)
        else:
            raise TypeError(
                f"Cannot add object of type {type(other)} to BasicArray of type {self.element_type}."
            )
        return self

    def addElement(self, new_element: Basic):
        self.elements.append(new_element)
        if not isinstance(new_element, self.element_type):
            printWithColor(
                f"WARNING: Object should be of type {self.element_type} but you passed an object of type {type(new_element)}. \n Object: {new_element}",
                Color.YELLOW,
            )
        return self.getLen() - 1

    def findElement(
        self,
        identifier: str,
    ):
        for element in self.elements:
            if element.identifier == identifier:
                return element
        return None

    def getElementIndex(
        self,
        identifier: str,
    ):
        for index, element in enumerate(self.elements):
            if element.identifier == identifier:
                return index
        return None

    def getElement(
        self,
        identifier: str,
    ):
        for element in self.elements:
            if element.identifier == identifier:
                return element
        return None

    def getElementByIndex(self, index):
        return self.elements[index]

    def getLastElement(self) -> Basic | None:
        if self.getLen() > 0:
            return self.elements[self.getLen() - 1]
        else:
            return None

    def removeElement(self, element):
        self.elements.remove(element)

    def removeElementByIndex(self, index):
        element = self.getElementByIndex(index)
        if element:
            self.elements.remove(element)

    def getElements(self):
        return self.elements

    def getLen(self):
        return len(self.elements)

    def __repr__(self):
        return f"ElementArray(\n{self.elements!r}\t)"
