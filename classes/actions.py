import re
from typing import Tuple, List
from classes.parametrs import Parametr, ParametrArray
from classes.basic import Basic, BasicArray
from classes.element_types import ElementsTypes
from classes.node import NodeArray
from utils.string_formating import removeTrailingComma
from utils.utils import isVariablePresent


class ActionParts:
    def __init__(self):
        self.body: List[str] = []

    def copy(self):
        action_part = ActionParts()
        action_part.body = self.body.copy()
        return action_part

    def __str__(self):
        body_to_str = ""
        for index, elem in enumerate(self.body):
            if index != 0:
                body_to_str += "; "
            body_to_str += elem
        return body_to_str


class Action(Basic):
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        exist_parametrs: ParametrArray = ParametrArray(),
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        super().__init__(identifier, source_interval, element_type)
        self.precondition: NodeArray = NodeArray(ElementsTypes.PRECONDITION_ELEMENT)
        self.postcondition: NodeArray = NodeArray(ElementsTypes.POSTCONDITION_ELEMENT)
        self.description_start: List[str] = []
        self.description_action_name: str = ""
        self.description_end: List[str] = []
        self.exist_parametrs: ParametrArray = exist_parametrs
        self.parametrs: ParametrArray = ParametrArray()

    def copy(self):
        action = Action(
            self.identifier,
            self.source_interval,
            self.exist_parametrs.copy(),
            self.element_type,
        )
        action.precondition = self.precondition.copy()
        action.postcondition = self.postcondition.copy()
        action.description_start = self.description_start
        action.description_action_name = self.description_action_name
        action.description_end = self.description_end
        action.parametrs = self.parametrs.copy()

        return action

    def getNameWithParams(self):
        if self.parametrs:
            if self.parametrs.getLen() == 0:
                return self.identifier
            else:
                return "{0}({1})".format(self.identifier, str(self.parametrs))
        else:
            return self.identifier

    def findParametrInBodyAndSetParametrs(self, parametrs):
        for parametr in parametrs.getElements():
            if isVariablePresent(str(self.precondition), parametr.identifier):
                self.parametrs.addElement(parametr)

            if isVariablePresent(str(self.postcondition), parametr.identifier):
                self.parametrs.addElement(parametr)

    def getBody(self):

        description = ""

        for index, element in enumerate(self.description_start):
            if index != 0:
                if element == self.description_start[index - 1]:
                    continue
                description += "; "
            description += element

        description += ":action '"
        description += f"{self.description_action_name} ("
        for index, element in enumerate(self.description_end):
            if index != 0:
                if element == self.description_end[index - 1]:
                    continue
                description += "; "
            description += element
        description += ")'"

        if self.exist_parametrs.getLen() > 0:
            return f""" = ( Exist ({self.exist_parametrs}) (\n\t\t({self.precondition})->\n\t\t("{description};")\n\t\t({self.postcondition})))"""
        elif self.parametrs.getLen() > 0:
            return f"""({self.parametrs}) = (\n\t\t({self.precondition})->\n\t\t("{description};")\n\t\t({self.postcondition}))"""
        else:
            return f""" = (\n\t\t({self.precondition})->\n\t\t("{description};")\n\t\t({self.postcondition}))"""

    def __str__(self):
        return "{0}{1},".format(self.identifier, self.getBody())

    def __repr__(self):
        return f"\tAction({self.identifier!r}, {self.number!r}, {self.sequence!r})\n"

    def __eq__(self, other):
        if isinstance(other, Action):
            return self.getBody() == other.getBody()
        return False


class ActionArray(BasicArray):
    def __init__(self):
        super().__init__(Action)

    def copy(self):
        new_aray: ActionArray = ActionArray()
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
        result: ActionArray = ActionArray()
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

    def isUniqAction(self, action: Action):
        for element in self.elements:
            if element == action:
                return (element, element.identifier, element.source_interval)
        return None, None, (None, None)

    def isUniqActionBySourceInterval(self, source_interval):
        for element in self.elements:
            if element.source_interval == source_interval:
                return element
        return None

    def getActionsInStrFormat(self):
        result = ""
        for index, element in enumerate(self.elements):
            if index != 0:
                result += "\n"
            result += str(element)

        result = removeTrailingComma(result)

        return result

    def __repr__(self):
        return f"ActionsArray(\n{self.elements!r}\t)"

    """
    def __init__(self):
        super().__init__(Action)

    def copy(self):
        new_aray: ActionArray = ActionArray()
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
        result: ActionArray = ActionArray()
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

    def isUniqAction(self, action: Action):
        for element in self.elements:
            if element == action:
                return (element, element.identifier, element.source_interval)
        return None, None, (None, None)

    def getActionsInStrFormat(self):
        result = ""
        for element in self.elements:
            result += "\n"
            result += str(element)

        result = removeTrailingComma(result)

        return result

    def __repr__(self):
        return f"ActionsArray(\n{self.elements!r}\t)"
"""
