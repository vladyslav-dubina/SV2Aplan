import re
from typing import Tuple, List
from classes.action_parametr import ActionParametr, ActionParametrArray
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
        exist_parametrs: ActionParametrArray | None = None,
    ):
        super().__init__(identifier, source_interval)
        self.precondition: NodeArray = NodeArray()
        self.postcondition: NodeArray = NodeArray()
        self.description: str = ""
        self.exist_parametrs: ActionParametrArray | None = exist_parametrs
        self.parametrs: ActionParametrArray = ActionParametrArray()

    def getBody(self):
        if self.exist_parametrs is not None:
            return f""" = ( Exist ({self.exist_parametrs}) (\n\t\t({self.precondition})->\n\t\t("{self.description};")\n\t\t({self.postcondition})))"""
        elif self.parametrs.getLen() > 0:
            return f"""({self.parametrs}) = (\n\t\t({self.precondition})->\n\t\t("{self.description};")\n\t\t({self.postcondition}))"""
        else:
            return f""" = (\n\t\t({self.precondition})->\n\t\t("{self.description};")\n\t\t({self.postcondition}))"""

    def __str__(self):
        return "{0}{1},".format(self.identifier, self.getBody())

    def __repr__(self):
        return f"\tAction({self.identifier!r}, {self.number!r}, {self.sequence!r})\n"

    def __eq__(self, other):
        if isinstance(other, Action):
            return self.getBody() == other.getBody()
        return False

    """
    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
        exist_parametrs: ActionParametrArray | None = None,
    ):
        super().__init__(identifier, source_interval)
        self.precondition: ActionParts = ActionParts()
        self.postcondition: ActionParts = ActionParts()
        self.description: ActionParts = ActionParts()
        self.exist_parametrs: ActionParametrArray | None = exist_parametrs
        self.parametrs: ActionParametrArray = ActionParametrArray()

    def copy(self):
        action = Action(
            self.identifier,
            self.source_interval,
        )
        action.precondition = self.precondition.copy()
        action.postcondition = self.postcondition.copy()
        action.description = self.description.copy()
        if self.exist_parametrs is not None:
            action.exist_parametrs = self.exist_parametrs.copy()
        action.parametrs = self.parametrs.copy()
        action.number = self.number
        return action
"""


# def getBody(self):
#    if self.exist_parametrs is not None:
#         return f""" = ( Exist ({self.exist_parametrs}) (\n\t\t({self.precondition})->\n\t\t("{self.description};")\n\t\t({self.postcondition})))"""
#     elif self.parametrs.getLen() > 0:
#        return f"""({self.parametrs}) = (\n\t\t({self.precondition})->\n\t\t("{self.description};")\n\t\t({self.postcondition}))"""
#    else:
#        return f""" = (\n\t\t({self.precondition})->\n\t\t("{self.description};")\n\t\t({self.postcondition}))"""
"""
    def findReturnAndReplaceToParametrImpl(self, task, element, index, flag):
        return_var_name = f"return_{task.identifier}"
        if isVariablePresent(element, task.identifier) or isVariablePresent(
            element, "return"
        ):
            element = re.sub(
                r"\b{}\b".format(re.escape(task.identifier)),
                "{}".format(return_var_name),
                element,
            )
            element = re.sub(
                r"\b{}\b".format(re.escape("return")),
                "{} = ".format(return_var_name),
                element,
            )

            if flag:
                self.precondition.body[index] = element
            else:
                self.postcondition.body[index] = element
            task.parametrs.addElement(
                ActionParametr(
                    return_var_name,
                    "var",
                )
            )

    def findReturnAndReplaceToParametr(self, task, packages):
        if task is None and packages is None:
            return

        for index, element in enumerate(self.precondition.body):
            if task is not None:
                self.findReturnAndReplaceToParametrImpl(task, element, index, True)
            if packages is not None:
                for package in packages.getElementsIE().getElements():
                    for package_task in package.tasks.getElements():
                        self.findReturnAndReplaceToParametrImpl(
                            package_task, element, index, True
                        )
        for index, element in enumerate(self.postcondition.body):
            if task is not None:
                self.findReturnAndReplaceToParametrImpl(task, element, index, False)
            if packages is not None:
                for package in packages.getElementsIE().getElements():
                    for package_task in package.tasks.getElements():
                        self.findReturnAndReplaceToParametrImpl(
                            package_task, element, index, False
                        )

    def findParametrInBodyAndSetParametrs(self, task):
        if task is not None:
            for task_parametr in task.parametrs.getElements():
                if isVariablePresent(str(self.precondition), task_parametr.identifier):
                    self.parametrs.addElement(task_parametr)

                if isVariablePresent(str(self.postcondition), task_parametr.identifier):
                    self.parametrs.addElement(task_parametr)

    def __str__(self):
        if self.number is None:
            return "{0}{1},".format(self.identifier, self.getBody())
        else:
            return "{0}_{2}{1},".format(self.identifier, self.getBody(), self.number)

    def __repr__(self):
        return f"\tAction({self.identifier!r}, {self.number!r}, {self.sequence!r})\n"

    def __eq__(self, other):
        if isinstance(other, Action):
            return self.getBody() == other.getBody()
        return False
    """


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
