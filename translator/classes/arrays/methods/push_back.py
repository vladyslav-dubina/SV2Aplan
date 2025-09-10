from typing import Tuple
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from Core.src.classes.actions import Action
from Core.src.classes.declarations import Declaration
from Core.src.classes.element_types import ElementsTypes
from Core.src.classes.node import Node
from Core.src.classes.protocols import BodyElement, Protocol
from Core.src.classes.structure import Structure
from translator.classes.base_translator import BaseTranslator


class PushBackTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        sv_structure: Structure,
        task_identifier: str,
        object_identifier: str,
        arguments_list: SystemVerilogParser.List_of_argumentsContext,
        source_interval: Tuple[int, int],
    ):
        decl = self.design_unit.declarations.getElement(object_identifier)
        if isinstance(decl, Declaration):
            (name_part, counter_type) = self._translator_ptr.getTranslator(
                "expr"
            ).getNamePartAndCounter(ElementsTypes.ASSIGN_ELEMENT)
            action_name = "{0}_{1}".format(name_part, self.counters.get(counter_type))
            action = Action(
                action_name,
                source_interval,
                element_type=ElementsTypes.ASSIGN_ELEMENT,
            )

            action.precondition.addElement(
                Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT)
            )
            description = "{0}.{1}[{0}.{1}.size] = {3}".format(
                object_identifier,
                task_identifier,
                decl.dimension_size,
                arguments_list.getText(),
            )
            action.description_start.append(
                f"{self.design_unit.identifier}#{self.design_unit.ident_uniq_name}"
            )
            action.description_action_name = name_part
            action.description_end.append(description)

            description = "{0}.{1}.size += 1".format(
                object_identifier,
                task_identifier,
            )
            action.description_end.append(description)

            node = Node(object_identifier, (0, 0), ElementsTypes.ARRAY_ELEMENT)
            node.design_unit_name = self.design_unit.ident_uniq_name
            action.postcondition.addElement(node.copy())
            node.element_type = ElementsTypes.ARRAY_SIZE_ELEMENT
            node.bit_selection = True
            action.postcondition.addElement(node.copy())
            action.postcondition.addElement(
                Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
            )
            self._translator_ptr.body2Aplan(
                arguments_list,
                sv_structure=sv_structure,
                destination_node_array=action.postcondition,
            )
            action.postcondition.addElement(
                Node(";", (0, 0), ElementsTypes.SEMICOLON_ELEMENT)
            )

            # Increase size
            node = Node(object_identifier, (0, 0), ElementsTypes.ARRAY_SIZE_ELEMENT)
            node.design_unit_name = self.design_unit.ident_uniq_name
            action.postcondition.addElement(node.copy())
            action.postcondition.addElement(
                Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
            )
            action.postcondition.addElement(node.copy())
            action.postcondition.addElement(
                Node("+", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
            )
            action.postcondition.addElement(
                Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT)
            )

            previus_action = False
            last_element = None
            if sv_structure is not None:
                beh_index = sv_structure.getLastBehaviorIndex()
                if beh_index is not None:
                    protocol = sv_structure.behavior[beh_index]
                    while True:
                        if isinstance(protocol, Structure):
                            protocol = protocol.behavior[
                                protocol.getLastBehaviorIndex()
                            ]
                            continue
                        else:
                            break
                    action_pointer: Action = action
                    (
                        last_element,
                        previus_action,
                        action_name,
                    ) = self._translator_ptr.getTranslator("expr").findAssociatedAction(
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
                        protocol.addBodyElement(
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
                    struct.addBodyElement(
                        BodyElement(
                            action.identifier,
                            action,
                            ElementsTypes.ACTION_ELEMENT,
                        )
                    )
                    self.design_unit.out_of_block_elements.addElement(struct)

            if not previus_action:
                self.design_unit.actions.addElement(action)
                self.counters.incriese(counter_type)
