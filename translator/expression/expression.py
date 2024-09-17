from typing import List, Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.parametrs import ParametrArray
from classes.action_precondition import ActionPreconditionArray
from classes.actions import Action
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import (
    addSpacesAroundOperators,
    notConcreteIndex2AplanStandart,
    replaceValueParametrsCalls,
    valuesToAplanStandart,
    vectorSizes2AplanStandart,
)
from utils.utils import (
    Counters_Object,
    containsOperator,
    isNumericString,
)


def prepareExpressionStringImpl(
    self: SV2aplan,
    expression: str,
    expr_type: ElementsTypes,
):
    expression = valuesToAplanStandart(expression)
    expression = addSpacesAroundOperators(expression)
    expression_with_replaced_names = vectorSizes2AplanStandart(expression)
    expression_with_replaced_names = notConcreteIndex2AplanStandart(
        expression_with_replaced_names, self.module
    )

    parametrs_array = self.module.value_parametrs

    expression_with_replaced_names = replaceValueParametrsCalls(
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


def getNamePartAndCounter(element_type: ElementsTypes) -> Tuple[str, CounterTypes]:
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

    return (name_part, counter_type)


def actionFromNodeStr(
    self: SV2aplan,
    node_str: str | List[str],
    source_interval: Tuple[int, int],
    element_type: ElementsTypes,
    sv_structure: Structure | None = None,
    input_parametrs: (
        Tuple[str | None, ParametrArray | None, ActionPreconditionArray | None] | None
    ) = None,
):
    (name_part, counter_type) = getNamePartAndCounter(element_type)
    action_name = "{0}_{1}".format(name_part, Counters_Object.getCounter(counter_type))

    action = Action(action_name, source_interval)

    action.description = f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({node_str})'"
    if isinstance(node_str, str):
        node_str = node_str.split(" ")
    if (
        element_type == ElementsTypes.ASSIGN_ELEMENT
        or element_type == ElementsTypes.REPEAT_ELEMENT
    ):
        action.precondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))
        for element in node_str:
            node_element_type = ElementsTypes.IDENTIFIER_ELEMENT
            if isNumericString(element):
                node_element_type = ElementsTypes.NUMBER_ELEMENT
            elif containsOperator(element):
                node_element_type = ElementsTypes.OPERATOR_ELEMENT
            element = self.module.name_change.changeNamesInStr(element)
            index = action.postcondition.addElement(
                Node(element, (0, 0), node_element_type)
            )
            node = action.postcondition.getElementByIndex(index)

            decl = self.module.declarations.getElement(node.identifier)
            if decl:
                node.module_name = self.module.ident_uniq_name

    elif element_type == ElementsTypes.ASSIGN_FOR_CALL_ELEMENT:
        if input_parametrs is not None:
            action.precondition.addElement(
                Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT)
            )
            description = ""
            for index, input_str in enumerate(node_str):
                if index != 0:
                    description += "; "
                (
                    expression,
                    expression_with_replaced_names,
                ) = self.prepareExpressionString(input_str, element_type)

                node_element_type = ElementsTypes.IDENTIFIER_ELEMENT
                if isNumericString(expression_with_replaced_names):
                    node_element_type = ElementsTypes.NUMBER_ELEMENT
                elif containsOperator(expression_with_replaced_names):
                    node_element_type = ElementsTypes.OPERATOR_ELEMENT

                action.postcondition.addElement(
                    Node(expression_with_replaced_names, (0, 0), node_element_type)
                )
                if index != len(node_str) - 1:
                    action.postcondition.addElement(
                        Node(";", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
                    )
                description += expression
            obj_def, parametrs, precondition = input_parametrs
            body = ""
            if obj_def is not None:
                body = f"{obj_def}:action '{name_part} ({description})'"
            else:
                body = f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({description})'"
            action.description = body
    elif element_type == ElementsTypes.ASSIGN_ARRAY_FOR_CALL_ELEMENT:
        if input_parametrs is not None:
            for element in node_str:
                obj_def, parametrs, precondition = input_parametrs
                action.precondition = precondition
                (
                    expression,
                    expression_with_replaced_names,
                ) = self.prepareExpressionString(element, element_type)
                node_element_type = ElementsTypes.IDENTIFIER_ELEMENT
                if isNumericString(expression_with_replaced_names):
                    node_element_type = ElementsTypes.NUMBER_ELEMENT
                elif containsOperator(expression_with_replaced_names):
                    node_element_type = ElementsTypes.OPERATOR_ELEMENT
                action.postcondition.addElement(
                    Node(expression_with_replaced_names, (0, 0), node_element_type)
                )

                action.exist_parametrs = parametrs

                action.description = f"{obj_def}:action '{name_part} ({expression})'"

    else:
        for element in node_str:
            node_element_type = ElementsTypes.IDENTIFIER_ELEMENT
            if isNumericString(element):
                node_element_type = ElementsTypes.NUMBER_ELEMENT
            elif containsOperator(element):
                node_element_type = ElementsTypes.OPERATOR_ELEMENT
            element = self.module.name_change.changeNamesInStr(element)
            index = action.precondition.addElement(
                Node(element, (0, 0), node_element_type)
            )
            node = action.precondition.getElementByIndex(index)
            decl = self.module.declarations.getElement(node.identifier)
            if decl:
                node.module_name = self.module.ident_uniq_name

        action.postcondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))

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

    if element_type != ElementsTypes.REPEAT_ELEMENT:
        Counters_Object.incrieseCounter(counter_type)

    return (action_pointer, action_name, source_interval, uniq)


def expression2AplanImpl(
    self: SV2aplan,
    ctx,
    element_type: ElementsTypes,
    sv_structure: Structure | None = None,
    name_space_element: ElementsTypes = ElementsTypes.NONE_ELEMENT,
) -> Tuple[Action, str, Tuple[int, int], bool]:
    (name_part, counter_type) = getNamePartAndCounter(element_type)

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
        self.body2Aplan(
            ctx,
            sv_structure=sv_structure,
            name_space=name_space_element,
            destination_node_array=action.postcondition,
        )
        if action.postcondition.getLen() == 0:
            return (None, None, None, None)
        action.description = f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({expression})'"
    else:
        # taskAssignIfPosible(self, ctx, action.precondition)
        self.body2Aplan(
            ctx,
            sv_structure=sv_structure,
            name_space=name_space_element,
            destination_node_array=action.precondition,
        )
        if action.precondition.getLen() == 0:
            return (None, None, None, None)
        action.postcondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))
        action.description = f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({expression})'"

    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action)

    params_for_finding: ParametrArray = ParametrArray()
    if self.inside_the_task == True:
        task = self.module.tasks.getLastTask()
        params_for_finding += task.parametrs

    if self.module.input_parametrs is not None:
        params_for_finding += self.module.input_parametrs
    action.findParametrInBodyAndSetParametrs(params_for_finding)

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

    if action_name is not None:
        action_parametrs_count = action.parametrs.getLen()
        action_name = f"{action_name}{action.parametrs.getIdentifiersListString(action_parametrs_count)}"

    if element_type != ElementsTypes.REPEAT_ELEMENT:
        Counters_Object.incrieseCounter(counter_type)

    return (action_pointer, action_name, source_interval, uniq)


def createSizeExpression(
    self: SV2aplan, identifier, size, source_interval: Tuple[int, int]
):
    (name_part, counter_type) = getNamePartAndCounter(ElementsTypes.ASSIGN_ELEMENT)
    action_name = "{0}_{1}".format(name_part, Counters_Object.getCounter(counter_type))
    action = Action(
        action_name,
        source_interval,
    )

    expressiont = "{0}.{1}.size = {2}".format(
        self.module.ident_uniq_name, identifier, size
    )
    action.precondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))
    action.description = "{0}#{1}:action '{2} ({3})'".format(
        self.module.identifier, self.module.ident_uniq_name, name_part, expressiont
    )
    node = Node(identifier, (0, 0), ElementsTypes.ARRAY_SIZE_ELEMENT)
    node.module_name = self.module.ident_uniq_name
    action.postcondition.addElement(node)

    action.postcondition.addElement(Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT))

    action.postcondition.addElement(
        Node(str(size), (0, 0), ElementsTypes.NUMBER_ELEMENT)
    )
    self.module.actions.addElement(action)
    protocol = Protocol(
        "B_{0}".format(action.getName()),
        source_interval,
    )

    protocol.addBody(
        BodyElement(
            action.identifier,
            action,
            ElementsTypes.ACTION_ELEMENT,
        )
    )
    self.module.out_of_block_elements.addElement(protocol)
    Counters_Object.incrieseCounter(counter_type)