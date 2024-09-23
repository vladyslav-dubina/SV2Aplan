from typing import Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.declarations import Declaration
from classes.element_types import ElementsTypes
from classes.node import Node
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from translator.expression.expression import findAssociatedAction, getNamePartAndCounter
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def createPushBack(
    self: SV2aplan,
    sv_structure: Structure,
    task_identifier: str,
    object_identifier: str,
    arguments_list: SystemVerilogParser.List_of_argumentsContext,
    source_interval: Tuple[int, int],
):

    decl = self.module.declarations.findElement(object_identifier)
    if isinstance(decl, Declaration):
        (name_part, counter_type) = getNamePartAndCounter(ElementsTypes.ASSIGN_ELEMENT)
        action_name = "{0}_{1}".format(
            name_part, Counters_Object.getCounter(counter_type)
        )
        action = Action(
            action_name,
            source_interval,
            element_type=ElementsTypes.ASSIGN_ELEMENT,
        )

        action.precondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))
        description = "{0}.{1}[{0}.{1}.size] = {3}".format(
            object_identifier,
            task_identifier,
            decl.dimension_size,
            arguments_list.getText(),
        )
        action.description_start.append(
            f"{self.module.identifier}#{self.module.ident_uniq_name}"
        )
        action.description_action_name = name_part
        action.description_end.append(description)

        description = "{0}.{1}.size += 1".format(
            object_identifier,
            task_identifier,
        )
        action.description_end.append(description)

        node = Node(object_identifier, (0, 0), ElementsTypes.ARRAY_ELEMENT)
        node.module_name = self.module.ident_uniq_name
        action.postcondition.addElement(node.copy())
        node.element_type = ElementsTypes.ARRAY_SIZE_ELEMENT
        node.bit_selection = True
        action.postcondition.addElement(node.copy())
        action.postcondition.addElement(
            Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        self.body2Aplan(
            arguments_list,
            sv_structure=sv_structure,
            name_space=ElementsTypes.NONE_ELEMENT,
            destination_node_array=action.postcondition,
        )
        action.postcondition.addElement(
            Node(";", (0, 0), ElementsTypes.SEMICOLON_ELEMENT)
        )

        # Increase size
        node = Node(object_identifier, (0, 0), ElementsTypes.ARRAY_SIZE_ELEMENT)
        node.module_name = self.module.ident_uniq_name
        action.postcondition.addElement(node.copy())
        action.postcondition.addElement(
            Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(node.copy())
        action.postcondition.addElement(
            Node("+", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT))

        previus_action = False
        last_element = None
        if sv_structure is not None:
            beh_index = sv_structure.getLastBehaviorIndex()
            if beh_index is not None:
                protocol = sv_structure.behavior[beh_index]
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
                    action_pointer = last_element.pointer_to_related
                    action_pointer.postcondition.addElement(
                        Node(";", (0, 0), ElementsTypes.SEMICOLON_ELEMENT)
                    )

                    action_pointer.description_start += action.description_start

                    action_pointer.description_end += action.description_end

                    action_pointer.postcondition += action.postcondition

                if not previus_action:
                    sv_structure.elements.addElement(action_pointer)
                    protocol.addBody(
                        BodyElement(
                            action_pointer.identifier,
                            action_pointer,
                            ElementsTypes.ACTION_ELEMENT,
                        )
                    )
            else:
                struct = Protocol(
                    "B_{0}".format(action.getName()),
                    source_interval,
                )
                struct.addBody(
                    BodyElement(
                        action.identifier,
                        action,
                        ElementsTypes.ACTION_ELEMENT,
                    )
                )
                self.module.out_of_block_elements.addElement(struct)

        if not previus_action:
            self.module.actions.addElement(action)
            Counters_Object.incrieseCounter(counter_type)
