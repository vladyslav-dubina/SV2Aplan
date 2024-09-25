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
from translator.utils import createDeclaration, createParametrArray
from utils.utils import Counters_Object, isNumericString


def createPowAction(
    self: SV2aplan, type: int = 0, protocol_params: ParametrArray = ParametrArray()
):

    name_part = "init"
    if type == 1:
        name_part = "inc"
    elif type == 2:
        name_part = "body"
    elif type == 3:
        name_part = "main"

    protocol = Protocol(f"POW_{name_part.upper()}", (0, 0), None, protocol_params)

    action_name = f"pow_{name_part}"
    if type == 3:
        action_name = f"pow_cond"

    action = Action(action_name, (0, 0), element_type=ElementsTypes.ASSIGN_ELEMENT)

    if type == 3:
        parametrs = ParametrArray()
        parametrs.addElement(protocol_params.getElementByIndex(1))
        parametrs.addElement(protocol_params.getElementByIndex(2))
        action.parametrs = parametrs
    else:
        action.parametrs = protocol_params
    action.description_action_name = action_name
    action.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )

    if protocol_params.getLen() > 1:
        second_param = protocol_params.getElementByIndex(1).identifier
    else:
        second_param = "1"

    if type == 0:
        action.description_end.append("counter = 0")
    elif type == 1:
        action.description_end.append("counter += 1")
    elif type == 2:
        action.description_end.append("counter = counter * counter")
    elif type == 3:
        action.description_end.append("counter < {0}".format(second_param))

    if type == 3:
        action.precondition.addElement(
            Node("counter", element_type=ElementsTypes.IDENTIFIER_ELEMENT)
        )
        action.precondition.addElement(
            Node("<", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.precondition.addElement(
            Node(second_param, element_type=ElementsTypes.IDENTIFIER_ELEMENT)
        )
    else:
        action.precondition.addElement(
            Node("1", element_type=ElementsTypes.NUMBER_ELEMENT)
        )

    if type == 3:
        action.postcondition.addElement(
            Node("1", element_type=ElementsTypes.NUMBER_ELEMENT)
        )
    else:

        if type == 0:
            action.postcondition.addElement(
                Node("counter", element_type=ElementsTypes.IDENTIFIER_ELEMENT)
            )
            action.postcondition.addElement(
                Node("=", element_type=ElementsTypes.OPERATOR_ELEMENT)
            )
            action.postcondition.addElement(
                Node("0", element_type=ElementsTypes.NUMBER_ELEMENT)
            )
        elif type == 1:
            action.postcondition.addElement(
                Node("counter", element_type=ElementsTypes.IDENTIFIER_ELEMENT)
            )
            action.postcondition.addElement(
                Node("=", element_type=ElementsTypes.OPERATOR_ELEMENT)
            )
            action.postcondition.addElement(
                Node("counter", element_type=ElementsTypes.IDENTIFIER_ELEMENT)
            )
            action.postcondition.addElement(
                Node("+", element_type=ElementsTypes.OPERATOR_ELEMENT)
            )
            action.postcondition.addElement(
                Node("1", element_type=ElementsTypes.NUMBER_ELEMENT)
            )
        elif type == 2:
            action.postcondition.addElement(
                Node("result", element_type=ElementsTypes.IDENTIFIER_ELEMENT)
            )
            action.postcondition.addElement(
                Node("=", element_type=ElementsTypes.OPERATOR_ELEMENT)
            )
            action.postcondition.addElement(
                Node("result", element_type=ElementsTypes.IDENTIFIER_ELEMENT)
            )
            action.postcondition.addElement(
                Node("*", element_type=ElementsTypes.OPERATOR_ELEMENT)
            )
            action.postcondition.addElement(
                Node("x", element_type=ElementsTypes.IDENTIFIER_ELEMENT)
            )

    if type == 3:
        protocol.addBody(
            BodyElement(
                action_name,
                action,
                ElementsTypes.IF_CONDITION_LEFT,
                parametrs=action.parametrs,
            )
        )
    else:
        protocol.addBody(
            BodyElement(
                action_name,
                action,
                ElementsTypes.ACTION_ELEMENT,
                parametrs=protocol_params,
            )
        )

    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action)

    if action_check_result is None:
        action_pointer: Action = action
        self.module.actions.addElement(action)

    return (action_pointer, protocol)


def pow2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.System_tf_callContext,
    sv_structure: Structure | None = None,
    destination_node_array: NodeArray | None = None,
):
    # PREPARE INPUT VAR
    inputs: str = ctx.list_of_arguments().getText()
    inputs = inputs.split(",")

    input_value_element_type = ElementsTypes.NUMBER_ELEMENT
    input_value_type = DeclTypes.INT

    input_var = inputs[0]
    if isNumericString(inputs[0]) is None:
        decl: Declaration = self.module.declarations.findElement(inputs[0])
        if decl:
            input_var = f"{self.module.ident_uniq_name}.{decl.identifier}"
            input_value_element_type = ElementsTypes.IDENTIFIER_ELEMENT
            input_value_type = decl.data_type

    # DECLARE VARS
    source_interval = ctx.list_of_arguments().getSourceInterval()

    result_pow = createDeclaration(
        self,
        "result_pow",
        input_value_type,
        CounterTypes.UNIQ_NAMES_COUNTER,
        source_interval,
    )

    source_interval = (source_interval[0], source_interval[1] + 1)
    counter = createDeclaration(
        self,
        "pow_counter",
        DeclTypes.INT,
        CounterTypes.UNIQ_NAMES_COUNTER,
        source_interval,
    )

    # SET RESULT VAR TO ACTION NODE ARRAY
    if destination_node_array:
        node = Node(result_pow.identifier, (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
        node.module_name = self.module.ident_uniq_name
        destination_node_array.addElement(node.copy())

    # PARAMETRS
    protocol_params_input: ParametrArray = createParametrArray(
        self, [input_var, inputs[1], counter.identifier, result_pow.identifier]
    )

    protocol_params: ParametrArray = createParametrArray(
        self, ["x", "y", "counter", "result"]
    )

    # PROTOCOLS
    beh_protocol_name = "POW"

    pow_structure = Structure(beh_protocol_name, (0, 0), ElementsTypes.TASK_ELEMENT)
    pow_protocol = Protocol(
        beh_protocol_name,
        (0, 0),
        ElementsTypes.TASK_ELEMENT,
        parametrs=protocol_params,
    )
    pow_structure.behavior.append(pow_protocol)

    parametrs = ParametrArray()
    parametrs.addElement(protocol_params.getElementByIndex(2))
    pow_init_action, pow_init_protocol = createPowAction(self, 0, parametrs)

    pow_cond_action, pow_main_protocol = createPowAction(self, 3, protocol_params)

    left_if = pow_main_protocol.body[0]
    pow_main_protocol.body[0] = BodyElement(
        left_if.pointer_to_related.getNameWithParams(),
        pow_cond_action,
        ElementsTypes.IF_CONDITION_LEFT,
    )

    parametrs = ParametrArray()
    parametrs.addElement(protocol_params.getElementByIndex(0))
    parametrs.addElement(protocol_params.getElementByIndex(3))
    pow_body_action, pow_body_protocol = createPowAction(self, 2, parametrs)
    pow_main_protocol.body[0].identifier += "." + pow_body_action.getNameWithParams()

    parametrs = ParametrArray()
    parametrs.addElement(protocol_params.getElementByIndex(2))
    pow_inc_action, pow_inc_protocol = createPowAction(self, 1, parametrs)
    pow_main_protocol.body[0].identifier += "." + pow_inc_action.getNameWithParams()

    pow_main_protocol.body[0].identifier += "." + pow_main_protocol.getName()

    parametrs = ParametrArray()
    parametrs.addElement(protocol_params.getElementByIndex(1))
    parametrs.addElement(protocol_params.getElementByIndex(2))
    pow_main_protocol.addBody(
        BodyElement(
            "!pow_cond",
            pow_cond_action,
            ElementsTypes.IF_CONDITION_RIGTH,
            parametrs=parametrs,
        )
    )

    beh_index = pow_structure.getLastBehaviorIndex()
    if beh_index is not None:
        pow_structure.behavior[beh_index].addBody(
            BodyElement(
                pow_init_action.identifier,
                pow_init_action,
                ElementsTypes.ACTION_ELEMENT,
                parametrs=protocol_params,
            )
        )

        pow_structure.behavior[beh_index].addBody(
            BodyElement(
                pow_main_protocol.identifier,
                pow_main_protocol,
                ElementsTypes.PROTOCOL_ELEMENT,
                # parametrs=protocol_params,
            )
        )
        pow_structure.behavior.append(pow_init_protocol)
        pow_structure.behavior.append(pow_main_protocol)

    uniq, index = self.module.structures.addElement(pow_structure)

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
