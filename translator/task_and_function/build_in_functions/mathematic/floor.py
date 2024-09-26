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
from translator.utils import createDeclaration, createParametrArray, createTypedef
from utils.utils import isNumericString


def createFloorAction(self: SV2aplan, type: int, protocol_params: ParametrArray):

    if type == 0:
        name_part = "check"
    elif type == 1:
        name_part = "body_gtz"
    elif type == 2:
        name_part = "body_ltz"
    elif type == 3:
        name_part = "check_int_part"
    elif type == 4:
        name_part = "body_fp"
    elif type == 5:
        name_part = "result"

    action = Action(
        f"floor_{name_part}", (0, 0), element_type=ElementsTypes.ASSIGN_ELEMENT
    )

    action.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )

    parametrs = ParametrArray()
    action.parametrs = protocol_params
    if type == 0:
        parametrs.addElement(protocol_params.getElementByIndex(0))
        action.description_end.append("x >= 0")
        action.description_action_name = f"floor check input"
        action.parametrs = parametrs
    elif type == 1:
        action.description_end.append("int_part = x - (x - (x / 1))")
        action.description_action_name = f"floor int_part if x >= 0"
    elif type == 2:
        action.description_end.append("int_part = x - (x - (x / 1)) - 1")
        action.description_action_name = f"floor int_part if x < 0"
    elif type == 3:
        action.description_end.append("x != int_part")
        action.description_action_name = f"floor check fractional part"
    elif type == 4:
        action.description_end.append("int_part -= 1")
        action.description_action_name = f"floor fractional part"
    elif type == 5:
        parametrs.addElement(protocol_params.getElementByIndex(1))
        action.description_end.append("result = int_part")
        action.description_action_name = f"floor result"
        action.parametrs = parametrs

    if type == 0:
        action.precondition.addElement(
            Node(
                protocol_params.getElementByIndex(0).identifier,
                (0, 0),
                ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.precondition.addElement(
            Node(
                ">=",
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
        action.postcondition.addElement(
            Node(
                "1",
                (0, 0),
                ElementsTypes.NUMBER_ELEMENT,
            )
        )
    elif type == 3:
        action.precondition.addElement(
            Node(
                protocol_params.getElementByIndex(0).identifier,
                (0, 0),
                ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.precondition.addElement(
            Node(
                "!=",
                (0, 0),
                ElementsTypes.OPERATOR_ELEMENT,
            )
        )
        action.precondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.int_part",
                (0, 0),
                ElementsTypes.INITIAL_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node(
                "1",
                (0, 0),
                ElementsTypes.NUMBER_ELEMENT,
            )
        )
    elif type == 4:
        action.precondition.addElement(
            Node(
                "1",
                (0, 0),
                ElementsTypes.NUMBER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.int_part",
                (0, 0),
                ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.int_part",
                (0, 0),
                ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("-", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                "1",
                (0, 0),
                ElementsTypes.NUMBER_ELEMENT,
            )
        )
    elif type == 5:
        action.precondition.addElement(
            Node(
                "1",
                (0, 0),
                ElementsTypes.NUMBER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.result",
                (0, 0),
                ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.int_part",
                (0, 0),
                ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
    else:
        action.precondition.addElement(
            Node(
                "1",
                (0, 0),
                ElementsTypes.NUMBER_ELEMENT,
            )
        )

        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.int_part",
                (0, 0),
                ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                protocol_params.getElementByIndex(0).identifier,
                (0, 0),
                ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("-", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node("(", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                protocol_params.getElementByIndex(0).identifier,
                (0, 0),
                ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("-", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node("(", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                protocol_params.getElementByIndex(0).identifier,
                (0, 0),
                ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("/", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT))
        action.postcondition.addElement(
            Node(")", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(")", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )

        if type == 2:
            action.postcondition.addElement(
                Node("-", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
            )
            action.postcondition.addElement(
                Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT)
            )

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

    # PREPARE INPUT VAR
    input_var = ctx.list_of_arguments().getText()
    decl = None
    input_value_type = DeclTypes.INT

    if isNumericString(input_var) is None:
        decl = self.module.declarations.findElement(input_var)
        if decl:
            input_var = f"{self.module.ident_uniq_name}.{decl.identifier}"
            input_value_type = decl.data_type

    # DECLARE VARS

    createTypedef(
        self,
        "floor_struct",
        ctx.getSourceInterval(),
        [
            ("result", input_value_type),
            ("int_part", input_value_type),
        ],
    )

    result_floor = createDeclaration(
        self,
        "floor_obj",
        DeclTypes.STRUCT,
        CounterTypes.UNIQ_NAMES_COUNTER,
        ctx.getSourceInterval(),
        "floor_struct",
    )

    # SET RESULT VAR TO ACTION NODE ARRAY
    if destination_node_array:
        node = Node(
            result_floor.identifier + ".result",
            (0, 0),
            ElementsTypes.IDENTIFIER_ELEMENT,
        )
        node.module_name = self.module.ident_uniq_name
        destination_node_array.addElement(node.copy())

    # PARAMETRS
    protocol_params_input: ParametrArray = createParametrArray(
        self,
        [
            input_var,
            self.module.ident_uniq_name + "." + result_floor.identifier,
        ],
    )

    protocol_params: ParametrArray = createParametrArray(self, ["x", "obj"])

    # PROTOCOLS
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

    action_floor_check = createFloorAction(self, 0, protocol_params)
    action_floor_body_gtz = createFloorAction(self, 1, protocol_params)
    action_floor_body_ltz = createFloorAction(self, 2, protocol_params)
    action_floor_check_fp = createFloorAction(self, 3, protocol_params)
    action_floor_body_fp = createFloorAction(self, 4, protocol_params)
    action_floor_result = createFloorAction(self, 5, protocol_params)

    floor_civ_protocol = Protocol(
        "FLOOR_BODY",
        (0, 0),
        ElementsTypes.PROTOCOL_ELEMENT,
        parametrs=protocol_params,
    )

    floor_structure.behavior[0].addBody(
        BodyElement(
            floor_civ_protocol.identifier,
            floor_civ_protocol,
            ElementsTypes.PROTOCOL_ELEMENT,
        )
    )

    floor_structure.behavior[0].addBody(
        BodyElement(
            action_floor_result.getNameWithParams(),
            action_floor_result,
            ElementsTypes.ACTION_ELEMENT,
        )
    )

    floor_structure.behavior.append(floor_civ_protocol)

    floor_civ_protocol.addBody(
        BodyElement(
            identifier="{0}.{1}".format(
                action_floor_check.getNameWithParams(),
                action_floor_body_gtz.getNameWithParams(),
            ),
            pointer_to_related=action_floor_check,
            element_type=ElementsTypes.IF_CONDITION_LEFT,
        )
    )

    floor_fp_protocol = Protocol(
        "FLOOR_F_BODY",
        (0, 0),
        ElementsTypes.PROTOCOL_ELEMENT,
        parametrs=protocol_params,
    )

    floor_civ_protocol.addBody(
        BodyElement(
            identifier="!{0}.{1}.{2}".format(
                action_floor_check.getNameWithParams(),
                action_floor_body_ltz.getNameWithParams(),
                floor_fp_protocol.getName(),
            ),
            pointer_to_related=action_floor_check,
            element_type=ElementsTypes.IF_CONDITION_RIGTH,
        )
    )

    floor_fp_protocol.addBody(
        BodyElement(
            action_floor_check_fp.getNameWithParams(),
            pointer_to_related=action_floor_check_fp,
            element_type=ElementsTypes.ACTION_ELEMENT,
        )
    )

    floor_fp_protocol.addBody(
        BodyElement(
            action_floor_body_fp.getNameWithParams(),
            pointer_to_related=action_floor_check_fp,
            element_type=ElementsTypes.ACTION_ELEMENT,
        )
    )

    floor_structure.behavior.append(
        floor_fp_protocol,
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
