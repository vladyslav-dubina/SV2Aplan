import re
from typing import Tuple, List
from classes.action_parametr import ActionParametrArray
from classes.basic import Basic, BasicArray
from classes.actions import Action, ActionParts
from classes.structure import Structure
from utils.string_formating import removeTrailingComma
from classes.counters import CounterTypes
from utils.utils import Counters_Object


class Task(Basic):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
    ):
        super().__init__(identifier, source_interval)
        self.initial_parametrs: ActionParametrArray = ActionParametrArray()
        self.structure: Structure | None = None
        self.postcondition: ActionParts = ActionParts()
        self.parametrs = []

    def generateAction(
        self, precondition: ActionParts, description: ActionParts, parametrs: List[str]
    ):
        action = Action(
            self.identifier,
            Counters_Object.getCounter(CounterTypes.TASK_COUNTER),
            self.source_interval,
        )
        action.precondition = precondition
        action.description = description
        self.replaseParametrs(parametrs)
        action.postcondition = self.postcondition
        Counters_Object.incrieseCounter(CounterTypes.TASK_COUNTER)
        return action

    def getActionName(self):
        return "{0}_{1}".format(self.identifier, self.number)

    def __str__(self):
        return "{0}{1},".format(self.identifier, self.getBody())

    def __repr__(self):
        return f"\Task({self.identifier!r}, {self.number!r}, {self.sequence!r} {self.postcondition!r})\n"


class TaskArray(BasicArray):
    def __init__(self):
        super().__init__(Task)

    def isUniqAction(self, task: Task):
        for element in self.elements:
            if element == task:
                return (element.identifier, element.source_interval)
        return None, (None, None)

    def getLastTask(self):
        return len(self.getElements()) - 1

    def __repr__(self):
        return f"TaskArray(\n{self.elements!r}\t)"
