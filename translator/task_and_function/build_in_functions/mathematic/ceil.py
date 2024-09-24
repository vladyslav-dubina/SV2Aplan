from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.parametrs import Parametr, ParametrArray
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from translator.task_and_function.build_in_functions.mathematic.modf import (
    modf2AplanImpl,
)
from utils.utils import Counters_Object, isNumericString


def createCeilAction(
    self: SV2aplan, return_the_wlole_part: bool, node_type: ElementsTypes
):
    name_part = "_rtfp"
    if return_the_wlole_part:
        name_part = "_rtwp"

    action = Action(
        f"ceil{name_part}", (0, 0), element_type=ElementsTypes.ASSIGN_ELEMENT
    )

    action.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )

    if return_the_wlole_part:
        action.description_end.append(f"return integral_part + 1")
    else:
        action.description_end.append(f"return integral_part")

    action.description_action_name = f"ceil{name_part}"

    node = Node(
        "fractional_part",
        (0, 0),
        ElementsTypes.IDENTIFIER_ELEMENT,
    )
    node.module_name = self.module.identifier
    action.precondition.addElement(node.copy())

    if return_the_wlole_part:
        action.precondition.addElement(
            Node(
                ">",
                (0, 0),
                ElementsTypes.OPERATOR_ELEMENT,
            )
        )
    else:
        action.precondition.addElement(
            Node(
                "<",
                (0, 0),
                ElementsTypes.OPERATOR_ELEMENT,
            )
        )
    action.precondition.addElement(
        Node(
            "0.0",
            (0, 0),
            ElementsTypes.NUMBER_ELEMENT,
        )
    )

    node = Node("result_ceil", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
    node.module_name = self.module.ident_uniq_name
    action.postcondition.addElement(node.copy())
    action.postcondition.addElement(Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
    node = Node(
        "integral_part",
        (0, 0),
        node_type,
    )
    node.module_name = self.module.ident_uniq_name
    action.postcondition.addElement(node.copy())
    if return_the_wlole_part:
        action.postcondition.addElement(
            Node("+", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT))

    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action)

    if action_check_result is None:
        action_pointer: Action = action
        self.module.actions.addElement(action)

    return action_pointer


def ceil2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.System_tf_callContext,
    sv_structure: Structure | None = None,
    destination_node_array: NodeArray | None = None,
):
    input_var = ctx.list_of_arguments().getText()
    decl = None
    node_type = ElementsTypes.NUMBER_ELEMENT

    self.module.declarations.addElement(
        Declaration(
            DeclTypes.INT,
            "result_ceil",
            "",
            "",
            0,
            "",
            0,
            (0, 0),
        )
    )

    if isNumericString(input_var) is None:
        decl = self.module.declarations.findElement(input_var)
        if decl:
            input_var = f"{self.module.ident_uniq_name}.{decl.identifier}"
        node_type = ElementsTypes.IDENTIFIER_ELEMENT

    action_ceil_rtwp = createCeilAction(self, True, node_type)
    action_ceil_rtfp = createCeilAction(self, False, node_type)

    if destination_node_array:
        node = Node("result_ceil", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
        node.module_name = self.module.ident_uniq_name
        destination_node_array.addElement(node.copy())

    protocol_params_input: ParametrArray = ParametrArray()
    protocol_params_input.addElement(
        Parametr(
            f"{input_var}",
            "var",
        )
    )

    protocol_params: ParametrArray = ParametrArray()
    protocol_params.addElement(
        Parametr(
            "x",
            "var",
        )
    )

    beh_protocol_name = "CEIL_{0}".format(
        Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER),
    )
    Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)

    if sv_structure:
        beh_index = sv_structure.getLastBehaviorIndex()
        if beh_index is not None:
            sv_structure.behavior[beh_index].addBody(
                BodyElement(
                    identifier=beh_protocol_name,
                    element_type=ElementsTypes.PROTOCOL_ELEMENT,
                    parametrs=protocol_params_input,
                )
            )

        last_prototcol = sv_structure.behavior[len(sv_structure.behavior) - 1]

        new_protocol = Protocol(
            beh_protocol_name,
            (0, 0),
            parametrs=protocol_params,
        )

        sv_structure.behavior[len(sv_structure.behavior) - 1] = new_protocol

        modf2AplanImpl(
            self,
            ctx.getSourceInterval(),
            sv_structure,
            destination_node_array,
            protocol_params,
        )

        beh_index = sv_structure.getLastBehaviorIndex()
        if beh_index is not None:
            body = f"{action_ceil_rtwp.identifier}"
            sv_structure.behavior[beh_index].addBody(
                BodyElement(
                    body,
                    action_ceil_rtwp,
                    ElementsTypes.IF_CONDITION_LEFT,
                )
            )
            body = f"{action_ceil_rtfp.identifier}"
            sv_structure.behavior[beh_index].addBody(
                BodyElement(
                    body,
                    action_ceil_rtfp,
                    ElementsTypes.IF_CONDITION_RIGTH,
                )
            )
        sv_structure.behavior.append(last_prototcol)
