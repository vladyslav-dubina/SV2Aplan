import re
from typing import Tuple, List
from classes.action_parametr import ActionParametr, ActionParametrArray
from classes.basic import Basic, BasicArray
from utils.string_formating import removeTrailingComma
from utils.utils import isVariablePresent


class ActionParts:
    def __init__(self):
        self.body: List[str] = []

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
        number: int,
        source_interval: Tuple[int, int],
        exist_parametrs: ActionParametrArray | None = None,
    ):
        self.number = number
        identifier_tmp = identifier + "_" + str(number)
        super().__init__(identifier_tmp, source_interval)
        self.precondition: ActionParts = ActionParts()
        self.postcondition: ActionParts = ActionParts()
        self.description: ActionParts = ActionParts()
        self.exist_parametrs: ActionParametrArray | None = exist_parametrs
        self.parametrs: ActionParametrArray = ActionParametrArray()

    def getBody(self):
        if self.exist_parametrs is not None:
            return f""" = ( Exist ({self.exist_parametrs}) (\n\t\t({self.precondition})->\n\t\t("{self.description};")\n\t\t({self.postcondition})))"""
        elif self.parametrs.getLen() > 0:
            return f"""({self.parametrs}) = (\n\t\t({self.precondition})->\n\t\t("{self.description};")\n\t\t({self.postcondition}))"""
        else:
            return f""" = (\n\t\t({self.precondition})->\n\t\t("{self.description};")\n\t\t({self.postcondition}))"""

    def getActionName(self):
        return "{0}_{1}".format(self.identifier, self.number)

    def findReturnAndReplaceToParametr(self, task):
        return_var_name = f"return_{task.identifier}"
        for index, element in enumerate(self.precondition.body):
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
                print(element)
                self.postcondition.body[index] = element
                task.parametrs.addElement(
                    ActionParametr(
                        return_var_name,
                        "var",
                    )
                )
        for index, element in enumerate(self.postcondition.body):
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
                self.postcondition.body[index] = element
                task.parametrs.addElement(
                    ActionParametr(
                        return_var_name,
                        "var",
                    )
                )

    def findParametrInBodyAndSetParametrs(self, task):
        for task_parametr in task.parametrs.getElements():
            if isVariablePresent(str(self.precondition), task_parametr.identifier):
                self.parametrs.addElement(task_parametr)

            if isVariablePresent(str(self.postcondition), task_parametr.identifier):
                self.parametrs.addElement(task_parametr)

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

    def isUniqAction(self, action: Action):
        for element in self.elements:
            if element == action:
                return (element.identifier, element.source_interval)
        return None, (None, None)

    def getActionsInStrFormat(self):
        result = ""
        for element in self.elements:
            result += "\n"
            result += str(element)

        result = removeTrailingComma(result)

        return result

    def __repr__(self):
        return f"ActionsArray(\n{self.elements!r}\t)"
