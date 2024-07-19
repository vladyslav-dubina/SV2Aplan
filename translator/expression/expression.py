from typing import List, Tuple

from classes.action_parametr import ActionParametrArray
from classes.action_precondition import ActionPreconditionArray
from classes.actions import Action
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import (
    addBracketsAfterNegation,
    addBracketsAfterTilda,
    addLeftValueForUnaryOrOperator,
    addSpacesAroundOperators,
    doubleOperators2Aplan,
    notConcreteIndex2AplanStandart,
    parallelAssignment2Assignment,
    replaceParametrsCalls,
    valuesToAplanStandart,
    vectorSizes2AplanStandart,
)
from utils.utils import Counters_Object


def prepareExpressionStringImpl(
    self: SV2aplan, expression: str, expr_type: ElementsTypes
):
    expression = valuesToAplanStandart(expression)
    expression = doubleOperators2Aplan(expression)
    expression = addLeftValueForUnaryOrOperator(expression)
    expression = addSpacesAroundOperators(expression)
    if (
        ElementsTypes.ASSIGN_FOR_CALL_ELEMENT != expr_type
        and ElementsTypes.ASSIGN_ARRAY_FOR_CALL_ELEMENT != expr_type
    ):
        expression_with_replaced_names = self.module.findAndChangeNamesToAgentAttrCall(
            expression
        )
    else:
        expression_with_replaced_names = expression

    expression_with_replaced_names = addBracketsAfterNegation(
        expression_with_replaced_names
    )
    expression_with_replaced_names = addBracketsAfterTilda(
        expression_with_replaced_names
    )
    expression_with_replaced_names = vectorSizes2AplanStandart(
        expression_with_replaced_names
    )
    if ElementsTypes.ASSIGN_ELEMENT == expr_type:
        expression_with_replaced_names = parallelAssignment2Assignment(
            expression_with_replaced_names
        )
    expression_with_replaced_names = notConcreteIndex2AplanStandart(
        expression_with_replaced_names, self.module
    )
    expression_with_replaced_names = replaceParametrsCalls(
        self.module.parametrs, expression_with_replaced_names
    )
    return (expression, expression_with_replaced_names)


def expression2AplanImpl(
    self: SV2aplan,
    input: str | List[str],
    element_type: ElementsTypes,
    source_interval: Tuple[int, int],
    input_parametrs: (
        Tuple[str | None, ActionParametrArray | None, ActionPreconditionArray | None]
        | None
    ) = None,
):

    name_part = ""
    counter_type = CounterTypes.NONE_COUNTER

    if element_type == ElementsTypes.ASSERT_ELEMENT:
        name_part = "assert"
        counter_type = CounterTypes.ASSERT_COUNTER
    elif element_type == ElementsTypes.CONDITION_ELEMENT:
        name_part = "cond"
        counter_type = CounterTypes.CONDITION_COUNTER
    elif (
        element_type == ElementsTypes.ASSIGN_ELEMENT
        or element_type == ElementsTypes.ASSIGN_FOR_CALL_ELEMENT
    ):
        name_part = "assign"
        counter_type = CounterTypes.ASSIGNMENT_COUNTER
    elif element_type == ElementsTypes.ASSIGN_ARRAY_FOR_CALL_ELEMENT:
        name_part = "assign_array"
        counter_type = CounterTypes.ASSIGNMENT_COUNTER
    elif element_type == ElementsTypes.REPEAT_ELEMENT:
        name_part = "repeat_iteration"
        counter_type = CounterTypes.REPEAT_COUNTER

    action_name = "{0}_{1}".format(name_part, Counters_Object.getCounter(counter_type))

    if (
        element_type != ElementsTypes.ASSIGN_FOR_CALL_ELEMENT
        and element_type != ElementsTypes.ASSIGN_ARRAY_FOR_CALL_ELEMENT
    ):
        input = self.module.name_change.changeNamesInStr(input)
        expression, expression_with_replaced_names = self.prepareExpressionString(
            input, element_type
        )

    action = Action(
        name_part,
        Counters_Object.getCounter(counter_type),
        source_interval,
    )

    if (
        element_type == ElementsTypes.ASSIGN_ELEMENT
        or element_type == ElementsTypes.REPEAT_ELEMENT
    ):
        action.precondition.body.append("1")
        action.postcondition.body.append(expression_with_replaced_names)
        action.description.body.append(
            f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({expression})'"
        )
    elif element_type == ElementsTypes.ASSIGN_FOR_CALL_ELEMENT:
        action.precondition.body.append("1")
        description = ""
        for index, input_str in enumerate(input):
            if index != 0:
                description += "; "
            (
                expression,
                expression_with_replaced_names,
            ) = self.prepareExpressionString(input_str, element_type)
            action.postcondition.body.append(expression_with_replaced_names)
            description += expression
        obj_def, parametrs, precondition = input_parametrs
        body = ""
        if obj_def is not None:
            body = f"{obj_def}:action '{name_part} ({description})'"
        else:
            body = f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({description})'"
        action.description.body.append(body)

    elif element_type == ElementsTypes.ASSIGN_ARRAY_FOR_CALL_ELEMENT:
        if input_parametrs is not None:
            obj_def, parametrs, precondition = input_parametrs
            action.precondition.body.append(str(precondition))

            (
                expression,
                expression_with_replaced_names,
            ) = self.prepareExpressionString(input, element_type)
            action.postcondition.body.append(expression_with_replaced_names)
            action.exist_parametrs = parametrs

            action.description.body.append(
                f"{obj_def}:action '{name_part} ({expression})'"
            )
    else:
        action.precondition.body.append(expression_with_replaced_names)
        action.postcondition.body.append("1")
        action.description.body.append(
            f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({expression})'"
        )

    if self.inside_the_task == True:
        task = self.module.tasks.getLastTask()
        if task is not None:
            action.findParametrInBodyAndSetParametrs(task)

    action_check_result, source_interval = self.module.actions.isUniqAction(action)
    uniq = False
    if action_check_result is None:
        uniq = True
        self.module.actions.addElement(action)
    else:
        Counters_Object.decrieseCounter(counter_type)
        action_name = action_check_result

    if self.inside_the_task == True and action_name is not None:
        action_parametrs_count = action.parametrs.getLen()
        action_name = f"{action_name}{action.parametrs.getIdentifiersListString(action_parametrs_count)}"

    Counters_Object.incrieseCounter(counter_type)
    return (action_name, source_interval, uniq)
