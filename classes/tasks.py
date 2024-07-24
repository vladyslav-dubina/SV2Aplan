import re
from typing import Tuple, List
from classes.action_parametr import ActionParametrArray
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
        self.initial_parametrs: ActionParametrArray = ActionParametrArray()
        self.structure: Structure | None = None
        self.postcondition: ActionParts = ActionParts()
        self.parametrs: ActionParametrArray = ActionParametrArray()

    def __str__(self):
        return "{0}({1}),".format(self.structure.identifier, self.parametrs)

    def __repr__(self):
        return (
            f"\Task({self.identifier!r},  {self.sequence!r}, {self.postcondition!r})\n"
        )


class TaskArray(BasicArray):
    def __init__(self):
        super().__init__(Task)

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
