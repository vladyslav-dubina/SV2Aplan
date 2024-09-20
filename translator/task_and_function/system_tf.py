from typing import List, Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.parametrs import Parametr, ParametrArray
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from translator.expression.expression import getNamePartAndCounter
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


embeaded_tf_list = ["$display", "$time"]


def systemTF2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.System_tf_callContext,
    destination_node_array: NodeArray | None = None,
    sv_structure: Structure | None = None,
):
    action = self.module.actions.isUniqActionBySourceInterval(ctx.getSourceInterval())
    action_name = ""
    precondition: NodeArray = NodeArray(ElementsTypes.PRECONDITION_ELEMENT)
    postcondition: NodeArray = NodeArray(ElementsTypes.POSTCONDITION_ELEMENT)
    description_start: List[str] = []
    description_end: List[str] = []
    description_action_name: str = ""
    parametrs: ParametrArray = ParametrArray()
    body = ""
    name_part = ""
    system_tf_identifier = ctx.system_tf_identifier().getText()
    element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT
    if system_tf_identifier == "$display":
        return
    elif system_tf_identifier == "$time":
        return
    elif system_tf_identifier == "$finish" or system_tf_identifier == "$stop":
        action_name = system_tf_identifier.replace("$", "")
        description_start.append(
            f"{self.module.identifier}#{self.module.ident_uniq_name}"
        )
        description_action_name = action_name
        name_part = action_name
        precondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))
        body = f"goal {action_name}"
    elif system_tf_identifier == "$size":
        name_part = "size"
        element_type = ElementsTypes.ASSIGN_ELEMENT
        self.module.declarations.addElement(
            Declaration(
                DeclTypes.INT,
                "return_size",
                "",
                "",
                0,
                "",
                0,
                ctx.getSourceInterval(),
            )
        )

        parametrs.addElement(
            Parametr(
                "result",
                "var",
            )
        )

        array = ctx.list_of_arguments().getText()
        decl = self.module.declarations.findElement(array)
        if decl is None:
            return

        node = Node(
            array,
            ctx.list_of_arguments().getSourceInterval(),
            ElementsTypes.ARRAY_SIZE_ELEMENT,
        )

        action_name = f"size_{array}"
        node.module_name = self.module.ident_uniq_name
        description_start.append(
            f"{self.module.identifier}#{self.module.ident_uniq_name}"
        )
        description_end.append(f"result = {array}.size")
        description_action_name = name_part

        precondition.addElement(Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT))
        postcondition.addElement(
            Node("result", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
        )
        postcondition.addElement(Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
        postcondition.addElement(node)
        body = f"{action_name}(return_size)"

        if destination_node_array:
            destination_node_array.addElement(
                Node("return_size", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
            )

    elif system_tf_identifier == "&pow":
        action_name = "pow"
        parametrs.addElement(
            Parametr(
                "x",
                "var",
            )
        )
        parametrs.addElement(
            Parametr(
                "y",
                "var",
            )
        )

    action = Action(action_name, ctx.getSourceInterval(), element_type=element_type)
    action.parametrs = parametrs
    action.precondition = precondition
    action.postcondition = postcondition
    action.description_start = description_start
    action.description_end = description_end
    action.description_action_name = description_action_name

    action_pointer: Action = action
    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action)

    if action_check_result is None:
        action_pointer: Action = action
        self.module.actions.addElement(action)

    if sv_structure is not None:

        beh_index = sv_structure.getLastBehaviorIndex()

        sv_structure.elements.addElement(action_pointer)

        if beh_index is not None:
            sv_structure.behavior[beh_index].addBody(
                BodyElement(body, action_pointer, ElementsTypes.ACTION_ELEMENT)
            )
        else:
            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
            b_index = sv_structure.addProtocol(
                "B_{0}".format(action_pointer.getName()),
                inside_the_task=(self.inside_the_task or self.inside_the_function),
            )
            sv_structure.behavior[b_index].addBody(
                BodyElement(body, action_pointer, ElementsTypes.ACTION_ELEMENT)
            )
    else:
        protocol_name = "{0}".format(name_part.upper())
        protocol: Protocol | None = self.module.out_of_block_elements.findElement(
            protocol_name
        )
        if isinstance(protocol, Protocol):
            protocol.addBody(
                BodyElement(
                    action.identifier,
                    action,
                    ElementsTypes.ACTION_ELEMENT,
                )
            )
        else:
            protocol = Protocol(
                protocol_name,
                ctx.getSourceInterval(),
            )

            protocol.addBody(
                BodyElement(
                    action.identifier,
                    action,
                    ElementsTypes.ACTION_ELEMENT,
                )
            )
            self.module.out_of_block_elements.addElement(protocol)


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
                if len(protocol.body) > 0:
                    last_element = protocol.body[len(protocol.body) - 1]
                    if (
                        last_element.element_type == ElementsTypes.ACTION_ELEMENT
                        and last_element.pointer_to_related.element_type
                        == ElementsTypes.ASSIGN_ELEMENT
                        and last_element.pointer_to_related.description_action_name
                        == name_part
                    ):
                        previus_action = True
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
