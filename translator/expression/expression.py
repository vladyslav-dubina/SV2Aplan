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
        or element_type == ElementsTypes.ASSIGN_SENSETIVE_ELEMENT
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
    previus_action = False
    (name_part, counter_type) = getNamePartAndCounter(element_type)
    action_name = "{0}_{1}".format(name_part, Counters_Object.getCounter(counter_type))

    if sv_structure:
        beh_index = sv_structure.getLastBehaviorIndex()
        if sv_structure and beh_index is not None:
            protocol = sv_structure.behavior[beh_index]
            if len(protocol.body) > 0:
                last_element = protocol.body[len(protocol.body) - 1]
                if last_element.element_type == ElementsTypes.ACTION_ELEMENT:
                    previus_action = True
                    action = last_element.pointer_to_related

    action = Action(action_name, source_interval)

    action.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )
    action.description_end.append(f"{node_str}")
    action.description_action_name = name_part
    if isinstance(node_str, str):
        node_str = node_str.split(" ")
    if (
        element_type == ElementsTypes.ASSIGN_ELEMENT
        or element_type == ElementsTypes.REPEAT_ELEMENT
        or element_type == ElementsTypes.ASSIGN_SENSETIVE_ELEMENT
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
            body_start = ""
            if obj_def is not None:
                body_start = f"{obj_def}"

            else:
                body_start = f"{self.module.identifier}#{self.module.ident_uniq_name}"

            action.description_start.append(body_start)
            action.description_action_name = name_part
            action.description_end.append(description)

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

                action.description_start.append(obj_def)
                action.description_action_name = name_part
                action.description_end.append(expression)

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
    remove_association: bool = False,
) -> Tuple[Action, str, Tuple[int, int], bool]:
    previus_action = False
    (name_part, counter_type) = getNamePartAndCounter(element_type)

    action = None
    last_element = None

    action_name = "{0}_{1}".format(name_part, Counters_Object.getCounter(counter_type))

    action = Action(action_name, ctx.getSourceInterval(), element_type=element_type)

    expression = ctx.getText()
    expression = valuesToAplanStandart(expression)
    if (
        element_type == ElementsTypes.ASSIGN_ELEMENT
        or element_type == ElementsTypes.REPEAT_ELEMENT
        or element_type == ElementsTypes.ASSIGN_SENSETIVE_ELEMENT
    ):

        action.precondition.addElement(Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT))
        taskAssignIfPosible(self, ctx, action.postcondition)
        postcondition: NodeArray = NodeArray(ElementsTypes.POSTCONDITION_ELEMENT)
        self.body2Aplan(
            ctx,
            sv_structure=sv_structure,
            name_space=name_space_element,
            destination_node_array=postcondition,
        )

        if postcondition.getLen() == 0:
            return (None, None, None, None)

        action.postcondition += postcondition

    else:
        if not previus_action:
            action.postcondition.addElement(
                Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT)
            )
        precondition: NodeArray = NodeArray(ElementsTypes.PRECONDITION_ELEMENT)
        self.body2Aplan(
            ctx,
            sv_structure=sv_structure,
            name_space=name_space_element,
            destination_node_array=precondition,
        )
        if precondition.getLen() == 0:
            return (None, None, None, None)

        action.precondition = precondition

    action.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )

    action.description_action_name = f"{name_part}"

    action.description_end.append(f"{expression}")

    action_pointer: Action = None
    last_element = None
    out_block_len = self.module.out_of_block_elements.getLen()

    if not remove_association:
        if sv_structure is not None:
            beh_index = sv_structure.getLastBehaviorIndex()
            if beh_index is not None:
                protocol = sv_structure.behavior[beh_index]
                last_element, previus_action, action_name = findAssociatedAction(
                    protocol,
                    element_type,
                    name_part,
                    action,
                    previus_action,
                    action_name,
                )

        elif out_block_len > 0:
            protocol: Protocol = self.module.out_of_block_elements.getElementByIndex(
                out_block_len - 1
            )
            last_element, previus_action, action_name = findAssociatedAction(
                protocol,
                element_type,
                name_part,
                action,
                previus_action,
                action_name,
            )

    action = copyToAssociatedAction(last_element, action)

    if not previus_action:
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
    if not previus_action:
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

    if action_name is not None:
        action_parametrs_count = action.parametrs.getLen()
        action_identifier = action.identifier
        if action_pointer:
            action_identifier = action_pointer.identifier
        action_name = f"{action_identifier}{action.parametrs.getIdentifiersListString(action_parametrs_count)}"

        if element_type == ElementsTypes.ASSIGN_SENSETIVE_ELEMENT:
            action_name = f"Sensetive({action_name})"
        if last_element:
            last_element.identifier = action_name

    if previus_action:
        return (None, None, None, None)

    return (action_pointer, action_name, source_interval, uniq)


def findAssociatedAction(
    protocol: Protocol | None,
    element_type: ElementsTypes,
    name_part: str,
    action: Action,
    previus_action: bool,
    action_name: str,
):
    last_element = None
    if protocol and len(protocol.body) > 0:
        last_element = protocol.body[len(protocol.body) - 1]
        if (
            last_element.element_type == ElementsTypes.ACTION_ELEMENT
            and last_element.pointer_to_related
            and last_element.pointer_to_related.element_type == element_type
            and last_element.pointer_to_related.description_action_name == name_part
        ):
            previus_action = True
            action_name = action.identifier
        else:
            last_element = None

    return (last_element, previus_action, action_name)


def copyToAssociatedAction(last_element: Action, action: Action):
    if last_element:
        previous_action: Action = last_element.pointer_to_related
        previous_action.description_end += action.description_end
        previous_action.description_start += action.description_start

        if previous_action.precondition.elements[0].identifier != "1":
            previous_action.precondition.addElement(
                Node(";", (0, 0), ElementsTypes.SEMICOLON_ELEMENT)
            )
            previous_action.precondition += action.precondition

        if previous_action.postcondition.elements[0].identifier != "1":
            previous_action.postcondition.addElement(
                Node(";", (0, 0), ElementsTypes.SEMICOLON_ELEMENT)
            )
            previous_action.postcondition += action.postcondition

        action = previous_action

    return action


def createSizeExpression(
    self: SV2aplan, identifier, size, source_interval: Tuple[int, int]
):
    (name_part, counter_type) = getNamePartAndCounter(ElementsTypes.ASSIGN_ELEMENT)
    action_name = "{0}_{1}".format(name_part, Counters_Object.getCounter(counter_type))
    action = Action(
        action_name, source_interval, element_type=ElementsTypes.ASSIGN_ELEMENT
    )
    expressiont = "{0}.{1}.size = {2}".format(
        self.module.ident_uniq_name, identifier, size
    )

    # PRECONDITION
    action.precondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))

    # DESCRIPTION
    action.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )
    action.description_end.append(expressiont)
    action.description_action_name = name_part

    # POSTCONDITION
    node = Node(identifier, (0, 0), ElementsTypes.ARRAY_SIZE_ELEMENT)
    node.module_name = self.module.ident_uniq_name
    action.postcondition.addElement(node)

    action.postcondition.addElement(Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT))

    action.postcondition.addElement(
        Node(str(size), (0, 0), ElementsTypes.NUMBER_ELEMENT)
    )

    # PROTOCOL
    protocol_name = "ARRAY_INIT_{0}".format(self.module.ident_uniq_name_upper)
    protocol = self.module.out_of_block_elements.findElement(protocol_name)

    previus_action = False

    if isinstance(protocol, Protocol):
        action_pointer: Action = action

        last_element, previus_action, action_name = findAssociatedAction(
            protocol,
            ElementsTypes.ASSIGN_ELEMENT,
            name_part,
            action_pointer,
            previus_action,
            action_name,
        )
        if last_element:
            action_pointer: Action = last_element.pointer_to_related
            # POSTCONDITION
            action_pointer.postcondition.addElement(
                Node(";", (0, 0), ElementsTypes.SEMICOLON_ELEMENT)
            )
            action_pointer.postcondition += action.postcondition

            # DESCRIPTION
            action_pointer.description_start += action.description_start
            action_pointer.description_end += action.description_end

        if not previus_action:
            protocol.addBody(
                BodyElement(
                    action.identifier,
                    action,
                    ElementsTypes.ACTION_ELEMENT,
                )
            )

    else:
        protocol = Protocol(
            "ARRAY_INIT_{0}".format(self.module.ident_uniq_name_upper),
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

    if not previus_action:
        self.module.actions.addElement(action)
        Counters_Object.incrieseCounter(counter_type)
