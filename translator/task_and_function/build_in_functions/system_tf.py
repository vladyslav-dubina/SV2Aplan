from typing import List
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.parametrs import Parametr, ParametrArray
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from translator.task_and_function.build_in_functions.mathematic.ceil import (
    ceil2AplanImpl,
)
from translator.task_and_function.build_in_functions.mathematic.floor import (
    floor2AplanImpl,
)
from translator.task_and_function.build_in_functions.mathematic.pow import pow2AplanImpl
from translator.utils import createProtocol


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
    elif system_tf_identifier == "$ceil":
        ceil2AplanImpl(
            self,
            ctx,
            sv_structure=sv_structure,
            destination_node_array=destination_node_array,
        )
        return
    elif system_tf_identifier == "$floor":
        floor2AplanImpl(
            self,
            ctx,
            sv_structure=sv_structure,
            destination_node_array=destination_node_array,
        )
        return
    elif system_tf_identifier == "$pow":
        pow2AplanImpl(
            self,
            ctx,
            sv_structure=sv_structure,
            destination_node_array=destination_node_array,
        )
        return
    elif system_tf_identifier == "$size":

        (
            name_part,
            element_type,
            action_name,
            parametrs,
            description_start,
            description_end,
            description_action_name,
            precondition,
            postcondition,
            body,
        ) = size2AplanImpl(
            self,
            ctx,
            parametrs,
            description_start,
            description_end,
            precondition,
            postcondition,
        )

        if destination_node_array:
            node = Node("return_size", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
            node.module_name = self.module.ident_uniq_name
            destination_node_array.addElement(node.copy())

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

    createProtocol(self, action_pointer, body, action_name, None, sv_structure)


def size2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.System_tf_callContext,
    parametrs: ParametrArray,
    description_start: List[str],
    description_end: List[str],
    precondition: NodeArray,
    postcondition: NodeArray,
):
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
    description_start.append(f"{self.module.identifier}#{self.module.ident_uniq_name}")
    description_end.append(f"result = {array}.size")
    description_action_name = name_part

    precondition.addElement(Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT))
    postcondition.addElement(Node("result", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT))
    postcondition.addElement(Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
    postcondition.addElement(node.copy())
    body = f"{action_name}(return_size)"

    return (
        name_part,
        element_type,
        action_name,
        parametrs,
        description_start,
        description_end,
        description_action_name,
        precondition,
        postcondition,
        body,
    )
