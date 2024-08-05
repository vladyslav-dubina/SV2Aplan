from typing import List, Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.action_parametr import ActionParametr, ActionParametrArray
from classes.action_precondition import ActionPreconditionArray
from classes.actions import Action
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.module import ModuleArray
from classes.node import Node, NodeArray
from classes.structure import Structure
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
from utils.utils import (
    Counters_Object,
    getValuesLeftOfEqualsOrDot,
    isFunctionCallPresentAndReplace,
)


def prepareExpressionStringImpl(
    self: SV2aplan,
    expression: str,
    expr_type: ElementsTypes,
):
    expression = valuesToAplanStandart(expression)
    expression = doubleOperators2Aplan(expression)
    expression = addLeftValueForUnaryOrOperator(expression)
    expression = addSpacesAroundOperators(expression)
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
    parametrs_array = self.module.parametrs

    expression_with_replaced_names = replaceParametrsCalls(
        parametrs_array, expression_with_replaced_names
    )
    return (expression, expression_with_replaced_names)


def taskAssignIfPosible(self: SV2aplan, ctx, destination_node_array: NodeArray):
    if isinstance(ctx, SystemVerilogParser.ExpressionContext):
        task = self.module.tasks.getLastTask()
        if task is not None:
            destination_node_array.addElement(
                Node(task.identifier, (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
            )
            destination_node_array.addElement(
                Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
            )


def expression2AplanImpl(
    self: SV2aplan,
    ctx,
    element_type: ElementsTypes,
    sv_structure: Structure | None = None,
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

    action = Action(
        action_name,
        ctx.getSourceInterval(),
    )

    expression = ctx.getText()
    expression = valuesToAplanStandart(expression)
    if (
        element_type == ElementsTypes.ASSIGN_ELEMENT
        or element_type == ElementsTypes.REPEAT_ELEMENT
    ):
        action.precondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))
        taskAssignIfPosible(self, ctx, action.postcondition)
        self.body2Aplan(ctx, destination_node_array=action.postcondition)
        
        action.description = f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({expression})'"
        """
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
            """
    else:
        taskAssignIfPosible(self, ctx, action.precondition)
        self.body2Aplan(ctx, destination_node_array=action.precondition)
        action.postcondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))
        action.description = f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({expression})'"

    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action)

    uniq = False
    if action_check_result is None:
        uniq = True
        index = self.module.actions.addElement(action)
        action_pointer = self.module.actions.getElementByIndex(index)
        if sv_structure is not None:
            sv_structure.elements.addElement(action)
    else:
        Counters_Object.decrieseCounter(counter_type)
        action_name = action_check_result
        if sv_structure is not None:
            print(sv_structure)
            sv_structure.elements.addElement(action_pointer)

    if element_type != ElementsTypes.REPEAT_ELEMENT:
        Counters_Object.incrieseCounter(counter_type)

    return (action_pointer, action_name, source_interval, uniq)


def expression2AplanImpl2(
    self: SV2aplan,
    input: str | List[str],
    element_type: ElementsTypes,
    source_interval: Tuple[int, int],
    input_parametrs: (
        Tuple[str | None, ActionParametrArray | None, ActionPreconditionArray | None]
        | None
    ) = None,
    sv_structure: Structure | None = None,
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
    matches = None

    if (
        element_type != ElementsTypes.ASSIGN_FOR_CALL_ELEMENT
        and element_type != ElementsTypes.ASSIGN_ARRAY_FOR_CALL_ELEMENT
    ):
        input = self.module.name_change.changeNamesInStr(input)
        expression, expression_with_replaced_names = self.prepareExpressionString(
            input, element_type
        )
        matches = getValuesLeftOfEqualsOrDot(expression)

    packages = self.module.packages_and_objects.getElementsIE(
        include=ElementsTypes.PACKAGE_ELEMENT,
        exclude_ident_uniq_name=self.module.ident_uniq_name,
    )

    objects = self.program.modules.getElementsIE(
        include=ElementsTypes.OBJECT_ELEMENT,
        include_ident_uniq_names=matches,
        exclude_ident_uniq_name=self.module.ident_uniq_name,
    )

    object_pointer = None
    if objects.getLen() > 0:
        object_pointer = objects.elements[0].ident_uniq_name

    packages += self.program.modules.getElementsIE(
        include=ElementsTypes.CLASS_ELEMENT,
        exclude_ident_uniq_name=self.module.ident_uniq_name,
    )

    functions_list = self.module.tasks.getElementsIE(
        ElementsTypes.FUNCTION_ELEMENT
    ).getElements()
    functions_list += self.module.tasks.getElementsIE(
        ElementsTypes.CONSTRUCTOR_ELEMENT
    ).getElements()

    for package in packages.getElements():
        functions_list += package.tasks.getElementsIE(
            ElementsTypes.FUNCTION_ELEMENT
        ).getElements()
        functions_list += package.tasks.getElementsIE(
            ElementsTypes.CONSTRUCTOR_ELEMENT
        ).getElements()

    for function in functions_list:
        function_result_var = None
        if function.element_type is ElementsTypes.CONSTRUCTOR_ELEMENT:
            function_result_var_for_replase = "{0}".format(self.module.ident_uniq_name)
        else:
            function_result_var = "{0}_call_result_{1}".format(
                function.identifier,
                Counters_Object.getCounter(CounterTypes.TASK_COUNTER),
            )
            function_result_var_for_replase = "{0}.{1}".format(
                self.module.ident_uniq_name, function_result_var
            )

        (
            is_present,
            expression_with_replaced_names,
            function_call,
        ) = isFunctionCallPresentAndReplace(
            expression_with_replaced_names,
            function.identifier,
            function_result_var_for_replase,
        )

        if is_present:
            self.funtionCall2Aplan(
                function,
                sv_structure,
                function_result_var,
                function_call,
                source_interval,
                object_pointer,
            )
            if function.element_type is ElementsTypes.CONSTRUCTOR_ELEMENT:
                return (None, None, None, None)

    action = Action(
        "{0}_{1}".format(
            name_part,
            Counters_Object.getCounter(counter_type),
        ),
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
    if self.inside_the_function == True or packages:
        task = self.module.tasks.getLastTask()

    action.findReturnAndReplaceToParametr(task, packages)

    if self.inside_the_task == True:
        task = self.module.tasks.getLastTask()

    action.findParametrInBodyAndSetParametrs(task)

    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action)
    uniq = False
    if action_check_result is None:
        uniq = True
        index = self.module.actions.addElement(action)
        action_pointer = self.module.actions.getElementByIndex(index)
        if sv_structure is not None:
            sv_structure.elements.addElement(action)
    else:
        Counters_Object.decrieseCounter(counter_type)
        action_name = action_check_result
        if sv_structure is not None:
            sv_structure.elements.addElement(action_pointer)

    if self.inside_the_task == True and action_name is not None:
        action_parametrs_count = action.parametrs.getLen()
        action_name = f"{action_name}{action.parametrs.getIdentifiersListString(action_parametrs_count)}"

    if element_type != ElementsTypes.REPEAT_ELEMENT:
        Counters_Object.incrieseCounter(counter_type)
    return (action_pointer, action_name, source_interval, uniq)
