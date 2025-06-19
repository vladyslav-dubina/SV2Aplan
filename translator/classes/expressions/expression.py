from typing import List, Tuple
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.action_precondition import ActionPreconditionArray
from AppModule.app.classes.actions import Action
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.node import Node, NodeArray
from AppModule.app.classes.parametrs import ParametrArray
from AppModule.app.classes.protocols import BodyElement, Protocol
from AppModule.app.classes.structure import Structure
from AppModule.app.utils.counters import CounterTypes
from translator.classes.base_translator import BaseTranslator


class ExpressionTranslator(BaseTranslator):
    _name_part = ""
    _action: Action = None
    _action_name = ""
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def getNamePartAndCounter(
        self, element_type: ElementsTypes
    ) -> Tuple[str, CounterTypes]:
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

    def taskAssignIfPosible(self, ctx, destination_node_array: NodeArray):
        if isinstance(ctx, SystemVerilogParser.ExpressionContext):
            task = self.design_unit.tasks.getLastTask()
            if task is not None:
                destination_node_array.addElement(
                    Node(task.identifier, (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
                )
                destination_node_array.addElement(
                    Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
                )

    def findAssociatedAction(
        self,
        protocol: Protocol | None,
        element_type: ElementsTypes,
        name_part: str,
        action: Action,
        previus_action: bool,
        action_name: str,
    ):
        last_element = None
        if protocol and len(protocol.body) > 0:
            last_element = protocol.body.getElementByIndex(len(protocol.body) - 1)
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

    def copyToAssociatedAction(self, last_element: Action, action: Action) -> Action:
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

    def prepareExpressionString(self, expression: str):
        expression = self.str_formater.valuesToAplanStandart(expression)
        expression = self.str_formater.addSpacesAroundOperators(expression)
        expression_with_replaced_names = self.str_formater.vectorSizes2AplanStandart(
            expression
        )
        expression_with_replaced_names = (
            self.str_formater.notConcreteIndex2AplanStandart(
                expression_with_replaced_names, self.design_unit
            )
        )

        parametrs_array = self.design_unit.value_parametrs

        expression_with_replaced_names = self.str_formater.replaceValueParametrsCalls(
            parametrs_array, expression_with_replaced_names
        )
        return (expression, expression_with_replaced_names)

    def actionFromNodeStr(
        self,
        node_str: str | List[str],
        source_interval: Tuple[int, int],
        element_type: ElementsTypes,
        input_parametrs: (
            Tuple[str | None, ParametrArray | None, ActionPreconditionArray | None]
            | None
        ) = None,
    ):
        self.logger.warning("Action fromn str", node_str)
        exit(1)
        # self.findStruct()
        # (name_part, counter_type) = self.getNamePartAndCounter(element_type)
        # action_name = "{0}_{1}".format(name_part, self.counters.get(counter_type))

        # if self.last_struct:
        #     beh_index = self.last_struct.getLastBehaviorIndex()
        #     if self.last_struct and beh_index is not None:
        #         protocol = self.last_struct.behavior[beh_index]
        #         if len(protocol.body) > 0:
        #             last_element = protocol.body[len(protocol.body) - 1]
        #             if last_element.element_type == ElementsTypes.ACTION_ELEMENT:
        #                 action = last_element.pointer_to_related

        # action = Action(action_name, source_interval)

        # action.description_start.append(
        #     f"{self.design_unit.identifier}#{self.design_unit.ident_uniq_name}"
        # )
        # action.description_end.append(f"{node_str}")
        # action.description_action_name = name_part
        # if isinstance(node_str, str):
        #     node_str = node_str.split(" ")
        # if (
        #     element_type == ElementsTypes.ASSIGN_ELEMENT
        #     or element_type == ElementsTypes.REPEAT_ELEMENT
        #     or element_type == ElementsTypes.ASSIGN_SENSETIVE_ELEMENT
        # ):
        #     action.precondition.addElement(
        #         Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT)
        #     )
        #     for element in node_str:
        #         node_element_type = ElementsTypes.IDENTIFIER_ELEMENT
        #         if self.utils.isNumericString(element):
        #             node_element_type = ElementsTypes.NUMBER_ELEMENT
        #         elif self.utils.containsOperator(element):
        #             node_element_type = ElementsTypes.OPERATOR_ELEMENT
        #         index = action.postcondition.addElement(
        #             Node(element, (0, 0), node_element_type)
        #         )
        #         node = action.postcondition.getElementByIndex(index)

        #         decl = self.design_unit.declarations.getElement(node.identifier)
        #         if decl:
        #             node.design_unit_name = self.design_unit.ident_uniq_name

        # elif element_type == ElementsTypes.ASSIGN_FOR_CALL_ELEMENT:
        #     if input_parametrs is not None:
        #         action.precondition.addElement(
        #             Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT)
        #         )
        #         description = ""
        #         for index, input_str in enumerate(node_str):
        #             if index != 0:
        #                 description += "; "
        #             (
        #                 expression,
        #                 expression_with_replaced_names,
        #             ) = self.prepareExpressionString(input_str)

        #             node_element_type = ElementsTypes.IDENTIFIER_ELEMENT
        #             if self.utils.isNumericString(expression_with_replaced_names):
        #                 node_element_type = ElementsTypes.NUMBER_ELEMENT
        #             elif self.utils.containsOperator(expression_with_replaced_names):
        #                 node_element_type = ElementsTypes.OPERATOR_ELEMENT

        #             action.postcondition.addElement(
        #                 Node(expression_with_replaced_names, (0, 0), node_element_type)
        #             )
        #             if index != len(node_str) - 1:
        #                 action.postcondition.addElement(
        #                     Node(";", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        #                 )
        #             description += expression
        #         obj_def, parametrs, precondition = input_parametrs
        #         body_start = ""
        #         if obj_def is not None:
        #             body_start = f"{obj_def}"

        #         else:
        #             body_start = (
        #                 f"{self.design_unit.identifier}#{self.design_unit.ident_uniq_name}"
        #             )

        #         action.description_start.append(body_start)
        #         action.description_action_name = name_part
        #         action.description_end.append(description)

        # elif element_type == ElementsTypes.ASSIGN_ARRAY_FOR_CALL_ELEMENT:
        #     if input_parametrs is not None:
        #         for element in node_str:
        #             obj_def, parametrs, precondition = input_parametrs
        #             action.precondition = precondition
        #             (
        #                 expression,
        #                 expression_with_replaced_names,
        #             ) = self.prepareExpressionString(element)
        #             node_element_type = ElementsTypes.IDENTIFIER_ELEMENT
        #             if self.utils.isNumericString(expression_with_replaced_names):
        #                 node_element_type = ElementsTypes.NUMBER_ELEMENT
        #             elif self.utils.containsOperator(expression_with_replaced_names):
        #                 node_element_type = ElementsTypes.OPERATOR_ELEMENT
        #             action.postcondition.addElement(
        #                 Node(expression_with_replaced_names, (0, 0), node_element_type)
        #             )

        #             action.exist_parametrs = parametrs

        #             action.description_start.append(obj_def)
        #             action.description_action_name = name_part
        #             action.description_end.append(expression)

        # else:
        #     for element in node_str:
        #         node_element_type = ElementsTypes.IDENTIFIER_ELEMENT
        #         if self.utils.isNumericString(element):
        #             node_element_type = ElementsTypes.NUMBER_ELEMENT
        #         elif self.utils.containsOperator(element):
        #             node_element_type = ElementsTypes.OPERATOR_ELEMENT
        #         index = action.precondition.addElement(
        #             Node(element, (0, 0), node_element_type)
        #         )
        #         node = action.precondition.getElementByIndex(index)
        #         decl = self.design_unit.declarations.getElement(node.identifier)
        #         if decl:
        #             node.design_unit_name = self.design_unit.ident_uniq_name

        #     action.postcondition.addElement(
        #         Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT)
        #     )

        # (
        #     action_pointer,
        #     action_check_result,
        #     source_interval,
        # ) = self.design_unit.actions.isUniqAction(action)

        # uniq = False
        # if action_check_result is None:
        #     uniq = True
        #     index = self.design_unit.actions.addElement(action)
        #     action_pointer = self.design_unit.actions.getElementByIndex(index)
        #     if self.last_struct is not None:
        #         self.last_struct.elements.addElement(action)
        # else:
        #     self.counters.decriese(counter_type)
        #     action_name = action_check_result
        #     if self.last_struct is not None:
        #         self.last_struct.elements.addElement(action_pointer)

        # if element_type != ElementsTypes.REPEAT_ELEMENT:
        #     self.counters.incriese(counter_type)

        # return (action_pointer, action_name, source_interval, uniq)

    def translate(
        self, ctx, remove_association: bool = False
    ) -> Tuple[Action, str, Tuple[int, int], bool]:
        self.findStruct()

        previus_action = False
        (self._name_part, self._counter_type) = self.getNamePartAndCounter(
            self.last_element_type
        )

        self._action = None
        last_element = None

        self._action_name = "{0}_{1}".format(
            self._name_part, self.counters.get(self._counter_type)
        )

        self._action = Action(
            self._action_name,
            ctx.getSourceInterval(),
            element_type=self.last_element_type,
        )

        expression = ctx.getText()
        expression = self.str_formater.valuesToAplanStandart(expression)

        if (
            self.last_element_type == ElementsTypes.ASSIGN_ELEMENT
            or self.last_element_type == ElementsTypes.REPEAT_ELEMENT
            or self.last_element_type == ElementsTypes.ASSIGN_SENSETIVE_ELEMENT
        ):
            self._action.precondition.addElement(
                Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT)
            )
            self.taskAssignIfPosible(ctx, self._action.postcondition)
            self._action.postcondition.action_type = self.last_element_type
            self.last_node_array = self._action.postcondition

        else:
            if not previus_action:
                self._action.postcondition.addElement(
                    Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT)
                )
            self._action.precondition.action_type = self.last_element_type
            self.last_node_array = self._action.precondition

        self._action.description_start.append(
            f"{self.design_unit.identifier}#{self.design_unit.ident_uniq_name}"
        )

        self._action.description_action_name = f"{self._name_part}"

        self._action.description_end.append(f"{expression}")
        return

    def insertOperator(self):
        if not self.last_operator:
            return

        if not self.last_node_array:
            return

        self.last_node_array.addElement(
            Node(self.last_operator, (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        self.last_operator = None

    def exit(self, remove_association: bool = False):
        if len(self._action.postcondition) == 0 or len(self._action.precondition) == 0:
            self.last_node_array = None
            return (None, None, None, None)

        action_pointer: Action = None
        last_element = None
        out_block_len = len(self.design_unit.out_of_block_elements)

        previus_action = False

        if not remove_association:
            if self.last_struct is not None:
                beh_index = self.last_struct.getLastBehaviorIndex()
                if beh_index is not None:
                    protocol = self.last_struct.behavior[beh_index]

                    while True:
                        if isinstance(protocol, Structure):
                            protocol = protocol.behavior[
                                protocol.getLastBehaviorIndex()
                            ]
                            continue
                        else:
                            break
                    (
                        last_element,
                        previus_action,
                        self._action_name,
                    ) = self.findAssociatedAction(
                        protocol,
                        self.last_element_type,
                        self._name_part,
                        self._action,
                        previus_action,
                        self._action_name,
                    )
            elif out_block_len > 0:
                protocol: Protocol = (
                    self.design_unit.out_of_block_elements.getElementByIndex(
                        out_block_len - 1
                    )
                )
                (
                    last_element,
                    previus_action,
                    self._action_name,
                ) = self.findAssociatedAction(
                    protocol,
                    self.last_element_type,
                    self._name_part,
                    self._action,
                    previus_action,
                    self._action_name,
                )

        self._action = self.copyToAssociatedAction(last_element, self._action)
        if not previus_action:
            (
                action_pointer,
                action_check_result,
                source_interval,
            ) = self.design_unit.actions.isUniqAction(self._action)
        params_for_finding: ParametrArray = ParametrArray()
        if self.inside_the_task == True:
            task = self.design_unit.tasks.getLastTask()
            params_for_finding += task.parametrs

        if self.design_unit.input_parametrs is not None:
            params_for_finding += self.design_unit.input_parametrs

        self._action.findParametrInBodyAndSetParametrs(params_for_finding)

        uniq = False
        if not previus_action:
            if action_check_result is None:
                uniq = True
                index = self.design_unit.actions.addElement(self._action)
                action_pointer = self.design_unit.actions.getElementByIndex(index)
                if self.last_struct is not None:
                    self.last_struct.elements.addElement(self._action)
            else:
                self.counters.decriese(self._counter_type)
                self._action_name = action_check_result
                if self.last_struct is not None:
                    self.last_struct.elements.addElement(action_pointer)

            if self.last_element_type != ElementsTypes.REPEAT_ELEMENT:
                self.counters.incriese(self._counter_type)

        if self._action_name is not None:
            action_parametrs_count = len(self._action.parametrs)
            action_identifier = self._action.identifier
            if action_pointer:
                action_identifier = action_pointer.identifier
            self._action_name = f"{action_identifier}{self._action.parametrs.getIdentifiersListString(action_parametrs_count)}"

            if self.last_element_type == ElementsTypes.ASSIGN_SENSETIVE_ELEMENT:
                self._action_name = f"Sensetive({self._action_name})"
            if last_element:
                last_element.identifier = self._action_name
        if previus_action:
            self.last_node_array = None
            return (None, None, None, None)

        self.last_node_array = None
        return (action_pointer, self._action_name, source_interval, uniq)

    def createSizeExpression(self, identifier, size, source_interval: Tuple[int, int]):
        (name_part, counter_type) = self.getNamePartAndCounter(
            ElementsTypes.ASSIGN_ELEMENT
        )
        action_name = "{0}_{1}".format(name_part, self.counters.get(counter_type))
        action = Action(
            action_name, source_interval, element_type=ElementsTypes.ASSIGN_ELEMENT
        )
        expressiont = "{0}.{1}.size = {2}".format(
            self.design_unit.ident_uniq_name, identifier, size
        )

        # PRECONDITION
        action.precondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))

        # DESCRIPTION
        action.description_start.append(
            f"{self.design_unit.identifier}#{self.design_unit.ident_uniq_name}"
        )
        action.description_end.append(expressiont)
        action.description_action_name = name_part

        # POSTCONDITION
        node = Node(identifier, (0, 0), ElementsTypes.ARRAY_SIZE_ELEMENT)
        node.design_unit_name = self.design_unit.ident_uniq_name
        action.postcondition.addElement(node)

        action.postcondition.addElement(
            Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )

        action.postcondition.addElement(
            Node(str(size), (0, 0), ElementsTypes.NUMBER_ELEMENT)
        )

        # PROTOCOL
        protocol_name = "ARRAY_INIT_{0}".format(self.design_unit.ident_uniq_name_upper)
        protocol = self.design_unit.out_of_block_elements.getElement(protocol_name)

        previus_action = False

        if isinstance(protocol, Protocol):
            action_pointer: Action = action

            last_element, previus_action, action_name = self.findAssociatedAction(
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
                protocol.addBodyElement(
                    BodyElement(
                        action.identifier,
                        action,
                        ElementsTypes.ACTION_ELEMENT,
                    )
                )

        else:
            protocol = Protocol(
                "ARRAY_INIT_{0}".format(self.design_unit.ident_uniq_name_upper),
                source_interval,
            )

            protocol.addBodyElement(
                BodyElement(
                    action.identifier,
                    action,
                    ElementsTypes.ACTION_ELEMENT,
                )
            )
            self.design_unit.out_of_block_elements.addElement(protocol)

        if not previus_action:
            self.design_unit.actions.addElement(action)
            self.counters.incriese(counter_type)
