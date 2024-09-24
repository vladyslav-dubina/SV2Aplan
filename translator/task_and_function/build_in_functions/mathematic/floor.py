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
from utils.utils import Counters_Object, isNumericString


def createFloorAction(self: SV2aplan, grater_than_zero: bool, node_type: ElementsTypes):
    name_part = "_ltz"
    if grater_than_zero:
        name_part = "_gtz"

    action = Action(
        f"floor{name_part}", (0, 0), element_type=ElementsTypes.ASSIGN_ELEMENT
    )

    action.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )

    if grater_than_zero:
        action.description_end.append(f"return integral_part + 1")
    else:
        action.description_end.append(f"return integral_part")

    action.description_action_name = f"floor{name_part}"

    action.precondition.addElement(
        Node(
            "x",
            (0, 0),
            ElementsTypes.IDENTIFIER_ELEMENT,
        )
    )

    if grater_than_zero:
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
            "0",
            (0, 0),
            ElementsTypes.NUMBER_ELEMENT,
        )
    )

    node = Node(
        "integral_part",
        (0, 0),
        node_type,
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
    if not grater_than_zero:
        action.postcondition.addElement(
            Node("-", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT))
    action.postcondition.addElement(Node(";", (0, 0), ElementsTypes.SEMICOLON_ELEMENT))

    node = Node("result_floor", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
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

    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action)

    if action_check_result is None:
        action_pointer: Action = action
        self.module.actions.addElement(action)

    return action_pointer


def floor2AplanImpl(
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
            "result_floor",
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

    action_floor_gtz = createFloorAction(self, True, node_type)
    action_floor_ltz = createFloorAction(self, False, node_type)

    if destination_node_array:
        node = Node("result_floor", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
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

    beh_protocol_name = "FLOOR"

    floor_structure = Structure(
        beh_protocol_name, ctx.getSourceInterval(), ElementsTypes.TASK_ELEMENT
    )
    floor_protocol = Protocol(
        beh_protocol_name,
        ctx.getSourceInterval(),
        ElementsTypes.TASK_ELEMENT,
        parametrs=protocol_params,
    )
    floor_structure.behavior.append(floor_protocol)

    beh_index = floor_structure.getLastBehaviorIndex()
    if beh_index is not None:
        body = f"{action_floor_gtz.identifier}"
        floor_structure.behavior[beh_index].addBody(
            BodyElement(
                body,
                action_floor_gtz,
                ElementsTypes.IF_CONDITION_LEFT,
            )
        )
        body = f"{action_floor_ltz.identifier}"
        floor_structure.behavior[beh_index].addBody(
            BodyElement(
                body,
                action_floor_ltz,
                ElementsTypes.IF_CONDITION_RIGTH,
            )
        )

    self.module.structures.addElement(floor_structure)

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
