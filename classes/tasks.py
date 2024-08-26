import re
from typing import Tuple, List
from classes.parametrs import ParametrArray
from classes.basic import Basic, BasicArray
from classes.actions import ActionParts
from classes.element_types import ElementsTypes
from classes.structure import Structure


class Task(Basic):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        element_type: ElementsTypes = ElementsTypes.TASK_ELEMENT,
    ):
        super().__init__(identifier, source_interval, element_type)
        self.initial_parametrs: ParametrArray = ParametrArray()
        self.structure: Structure | None = None
        self.postcondition: ActionParts = ActionParts()
        self.parametrs: ParametrArray = ParametrArray()

    def findReturnParam(self):
        retunr_var = f"return_{self.identifier}"
        for element in self.parametrs.getElements():
            if element.identifier == retunr_var:
                return True

    def copy(self):
        task = Task(self.identifier, self.source_interval, self.element_type)
        task.initial_parametrs = self.initial_parametrs.copy()
        task.structure = self.structure.copy()
        task.postcondition = self.postcondition.copy()
        task.parametrs = self.parametrs.copy()
        task.number = self.number
        return task

    def __str__(self):
        return "{0}({1}),".format(self.structure.identifier, self.parametrs)

    def __repr__(self):
        return f"\Task({self.identifier!r},  {self.sequence!r}, {self.postcondition!r}, {self.parametrs!r}, {self.initial_parametrs!r}, {self.structure!r})\n"


class TaskArray(BasicArray):
    def __init__(self):
        super().__init__(Task)

    def copy(self):
        new_aray: TaskArray = TaskArray()
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
        result: TaskArray = TaskArray()
        elements = self.elements

        if include is None and exclude is None:
            return self

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

    def isUniqAction(self, task: Task):
        for element in self.elements:
            if element == task:
                return (element.identifier, element.source_interval)
        return None, (None, None)

    def getFunctions(self):
        result: List[Task] = []
        for element in self.getElements():
            if element.element_type == ElementsTypes.FUNCTION_ELEMENT:
                result.append(element)

        return result

    def getElementsIE(
        self, include: ElementsTypes | None = None, exclude: ElementsTypes | None = None
    ):
        result: TaskArray = TaskArray()
        elements = self.elements

        if include is None and exclude is None:
            return self

        for element in elements:
            if include is not None and element.element_type is not include:
                continue
            if exclude is not None and element.element_type is exclude:
                continue
            result.addElement(element)

        return result

    def getLastTask(self):
        index = len(self.getElements()) - 1
        if index >= 0:
            return self.getElementByIndex(index)
        return None

    def __repr__(self):
        return f"TaskArray(\n{self.elements!r}\t)"
