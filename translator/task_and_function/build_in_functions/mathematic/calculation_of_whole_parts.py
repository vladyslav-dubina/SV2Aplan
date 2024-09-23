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
from translator.system_verilog_to_aplan import SV2aplan
from translator.utils import createProtocol
from utils.utils import Counters_Object, isNumericString


def ceil2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.System_tf_callContext,
    sv_structure: Structure | None = None,
    destination_node_array: NodeArray | None = None,
):
    name_part = "ceil_rtfp"  # return the factorial part
    element_type = ElementsTypes.ASSIGN_ELEMENT
    input_var = ctx.list_of_arguments().getText()
    decl = None
    node_type = ElementsTypes.NUMBER_ELEMENT

    action_ceil_rtfp = Action(
        name_part, (0, 0), element_type=ElementsTypes.ASSIGN_ELEMENT
    )

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

    action_name = name_part
    action_ceil_rtfp.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )
    action_ceil_rtfp.description_end.append(f"return integral_part")
    action_ceil_rtfp.description_action_name = name_part

    action_ceil_rtfp.precondition.addElement(
        Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT)
    )

    node = Node("result_ceil", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
    node.module_name = self.module.ident_uniq_name
    action_ceil_rtfp.postcondition.addElement(node.copy())
    action_ceil_rtfp.postcondition.addElement(
        Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
    )
    node = Node(
        "integral_part",
        ctx.list_of_arguments().getSourceInterval(),
        node_type,
    )
    node.module_name = self.module.ident_uniq_name
    action_ceil_rtfp.postcondition.addElement(node.copy())

    body = f"{action_name}(return_size)"

    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action_ceil_rtfp)

    if action_check_result is None:
        self.module.actions.addElement(action_ceil_rtfp)

    name_part = "ceil_rtwp"  # return the whole part
    action_ceil_rtwp = Action(
        name_part, (0, 0), element_type=ElementsTypes.CONDITION_ELEMENT
    )

    action_ceil_rtwp.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )
    action_ceil_rtwp.description_end.append(f"return integral_part + 1 ")
    action_ceil_rtwp.description_action_name = name_part

    action_ceil_rtwp.precondition.addElement(
        Node(
            f"{self.module.identifier}.fractional_part",
            (0, 0),
            ElementsTypes.IDENTIFIER_ELEMENT,
        )
    )
    action_ceil_rtwp.precondition.addElement(
        Node(
            ">",
            (0, 0),
            ElementsTypes.OPERATOR_ELEMENT,
        )
    )
    action_ceil_rtwp.precondition.addElement(
        Node(
            "0.0",
            (0, 0),
            ElementsTypes.NUMBER_ELEMENT,
        )
    )

    node = Node("result_ceil", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
    node.module_name = self.module.ident_uniq_name
    action_ceil_rtwp.postcondition.addElement(node.copy())
    action_ceil_rtwp.postcondition.addElement(
        Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
    )
    node = Node(
        "integral_part",
        ctx.list_of_arguments().getSourceInterval(),
        node_type,
    )
    node.module_name = self.module.ident_uniq_name
    action_ceil_rtwp.postcondition.addElement(node.copy())
    action_ceil_rtwp.postcondition.addElement(
        Node("+", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
    )
    action_ceil_rtwp.postcondition.addElement(
        Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT)
    )

    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action_ceil_rtwp)

    if action_check_result is None:
        self.module.actions.addElement(action_ceil_rtwp)

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

    Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
    beh_protocol_name = "B_{0}".format(
        Counters_Object.getCounter(CounterTypes.B_COUNTER),
    )
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
        ceil_protocol_name = "CEIL_{0}".format(
            Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER),
        )
        Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
        if beh_index is not None:
            sv_structure.behavior[beh_index].addBody(
                BodyElement(
                    identifier=ceil_protocol_name,
                    element_type=ElementsTypes.PROTOCOL_ELEMENT,
                )
            )

        sv_structure.addProtocol(ceil_protocol_name)

        beh_index = sv_structure.getLastBehaviorIndex()
        if beh_index is not None:
            body = f"{action_ceil_rtwp.identifier}"
            sv_structure.behavior[beh_index].addBody(
                BodyElement(
                    body,
                    action_pointer,
                    ElementsTypes.IF_CONDITION_LEFT,
                )
            )
            body = f"{action_ceil_rtfp.identifier}"
            sv_structure.behavior[beh_index].addBody(
                BodyElement(
                    body,
                    action_pointer,
                    ElementsTypes.IF_CONDITION_RIGTH,
                )
            )
        sv_structure.behavior.append(last_prototcol)


def modf2AplanImpl(
    self: SV2aplan,
    source_interval: Tuple[int, int],
    sv_structure: Structure | None = None,
    destination_node_array: NodeArray | None = None,
    input_params: ParametrArray = ParametrArray(),
    inside_method: bool = True,
):
    action_name = "modf"
    action = Action(action_name, (0, 0), element_type=ElementsTypes.ASSIGN_ELEMENT)

    action.parametrs.addElement(
        Parametr(
            "x",
            "var",
        )
    )

    action.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )
    action.description_end.append(f"integral_part = x - (x - (x / 1))")
    action.description_end.append(f"fractional_part = x - integral_part")
    action.description_action_name = action_name

    action.precondition.addElement(Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT))

    node = Node(
        "integral_part",
        (0, 0),
        ElementsTypes.IDENTIFIER_ELEMENT,
    )
    node.module_name = self.module.ident_uniq_name
    action.postcondition.addElement(node.copy())
    action.postcondition.addElement(Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
    action.postcondition.addElement(Node("x", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT))
    action.postcondition.addElement(Node("-", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
    action.postcondition.addElement(Node("(", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
    action.postcondition.addElement(Node("x", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT))
    action.postcondition.addElement(Node("-", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
    action.postcondition.addElement(Node("(", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
    action.postcondition.addElement(Node("x", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT))
    action.postcondition.addElement(Node("/", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
    action.postcondition.addElement(Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT))
    action.postcondition.addElement(Node(")", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
    action.postcondition.addElement(Node(")", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
    action.postcondition.addElement(Node(";", (0, 0), ElementsTypes.SEMICOLON_ELEMENT))

    node = Node(
        "fractional_part",
        (0, 0),
        ElementsTypes.IDENTIFIER_ELEMENT,
    )
    node.module_name = self.module.ident_uniq_name
    action.postcondition.addElement(node.copy())
    action.postcondition.addElement(Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
    action.postcondition.addElement(Node("x", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT))
    action.postcondition.addElement(Node("-", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
    node = Node(
        "integral_part",
        (0, 0),
        ElementsTypes.IDENTIFIER_ELEMENT,
    )
    node.module_name = self.module.ident_uniq_name
    action.postcondition.addElement(node.copy())

    self.module.declarations.addElement(
        Declaration(
            DeclTypes.INT,
            "integral_part",
            "",
            "",
            0,
            "",
            0,
            source_interval,
        )
    )

    source_interval = (source_interval[0], source_interval[1] + 1)
    self.module.declarations.addElement(
        Declaration(
            DeclTypes.REAL,
            "fractional_part",
            "",
            "",
            0,
            "",
            0,
            source_interval,
        )
    )

    if destination_node_array and not inside_method:
        node = Node("fractional_part", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
        node.module_name = self.module.ident_uniq_name
        destination_node_array.addElement(node.copy())

    fractional_name = f"{self.module.ident_uniq_name}.fractional_part"
    integral_name = f"{self.module.ident_uniq_name}.integral_part"
    body = f"{action_name}"

    action_pointer: Action = action
    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action)

    if action_check_result is None:
        action_pointer: Action = action
        self.module.actions.addElement(action)

    createProtocol(self, action_pointer, body, action_name, input_params, sv_structure)
