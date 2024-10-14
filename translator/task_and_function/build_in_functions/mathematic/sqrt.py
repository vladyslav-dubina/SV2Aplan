from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.parametrs import ParametrArray
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from translator.utils import createDeclaration, createParametrArray, createTypedef
from utils.utils import isNumericString

"""
double sqrt(double x) {
    if (x < 0) {
        printf("Error: negative input\n");
        return -1;
    }

    double guess = x / 2.0;
    double epsilon = 0.000001;
    
    // Newton's iterative method
    while ((guess * guess - x) > epsilon || (x - guess * guess) > epsilon) {
        guess = (guess + x / guess) / 2.0;
    }

    return guess;
}
"""


def createSqrtStart(self: SV2aplan, protocol_params: ParametrArray = ParametrArray()):
    action_name = f"sqrt_ltz"
    action = Action(action_name, (0, 0), element_type=ElementsTypes.ASSIGN_ELEMENT)

    parametrs = ParametrArray()
    parametrs.addElement(protocol_params.getElementByIndex(0))
    parametrs.addElement(protocol_params.getElementByIndex(1))
    action.parametrs = parametrs

    action.description_action_name = "sqrt input value less than zero"
    action.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )
    action.description_end.append(
        f"{protocol_params.getElementByIndex(0).identifier} < 0"
    )

    action.precondition.addElement(
        Node(
            protocol_params.getElementByIndex(0).identifier,
            element_type=ElementsTypes.IDENTIFIER_ELEMENT,
        )
    )
    action.precondition.addElement(
        Node("<", element_type=ElementsTypes.OPERATOR_ELEMENT)
    )
    action.precondition.addElement(Node("0", element_type=ElementsTypes.NUMBER_ELEMENT))
    action.postcondition.addElement(
        Node("1", element_type=ElementsTypes.NUMBER_ELEMENT)
    )

    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action)

    if action_check_result is None:
        action_pointer: Action = action
        self.module.actions.addElement(action)

    action = action.copy()
    parametrs = ParametrArray()
    parametrs.addElement(protocol_params.getElementByIndex(1))
    action.parametrs = parametrs
    action.identifier = "sqrt_nan"
    action.description_action_name = "sqrt result"
    action.description_end = []
    action.description_end.append("result = -1")

    action.precondition = NodeArray(ElementsTypes.PRECONDITION_ELEMENT)
    action.precondition.addElement(Node("1", element_type=ElementsTypes.NUMBER_ELEMENT))
    action.postcondition = NodeArray(ElementsTypes.POSTCONDITION_ELEMENT)
    action.postcondition.addElement(
        Node(
            f"{protocol_params.getElementByIndex(1).identifier}.result",
            element_type=ElementsTypes.IDENTIFIER_ELEMENT,
        )
    )
    action.postcondition.addElement(
        Node("=", element_type=ElementsTypes.OPERATOR_ELEMENT)
    )

    action.postcondition.addElement(
        Node("-1", element_type=ElementsTypes.NUMBER_ELEMENT)
    )

    (
        action_pointer_2,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action)

    if action_check_result is None:
        action_pointer_2: Action = action
        self.module.actions.addElement(action)

    return (action_pointer, action_pointer_2)


def createSqrtAction(
    self: SV2aplan, type: int = 0, protocol_params: ParametrArray = ParametrArray()
):

    name_part = "init"
    if type == 1:
        name_part = "loop_body"
    elif type == 2:
        name_part = "main"
    elif type == 3:
        name_part = "return"

    protocol = Protocol(f"SQRT_{name_part.upper()}", (0, 0), None, protocol_params)

    action_name = f"sqrt_{name_part}"
    if type == 2:
        action_name = f"sqrt_cond"

    action = Action(action_name, (0, 0), element_type=ElementsTypes.ASSIGN_ELEMENT)

    parametrs = ParametrArray()
    if type == 0:
        parametrs.addElement(protocol_params.getElementByIndex(0))
        parametrs.addElement(protocol_params.getElementByIndex(1))
        action.parametrs = parametrs
    elif type == 1:
        parametrs.addElement(protocol_params.getElementByIndex(0))
        parametrs.addElement(protocol_params.getElementByIndex(1))
        action.parametrs = parametrs
    elif type == 2:
        parametrs.addElement(protocol_params.getElementByIndex(0))
        parametrs.addElement(protocol_params.getElementByIndex(1))
        action.parametrs = parametrs
    elif type == 3:
        parametrs.addElement(protocol_params.getElementByIndex(1))
        action.parametrs = parametrs

    action.description_action_name = action_name
    action.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )

    if type == 0:
        action.description_end.append(
            f"gues = {protocol_params.getElementByIndex(0).identifier} / 2.0"
        )
        action.description_end.append("epsilon  = 0.000001")
    elif type == 1:
        action.description_end.append(
            "gues = (gues + {0} / gues) / 2.0".format(
                protocol_params.getElementByIndex(0).identifier,
            )
        )
    elif type == 2:
        action.description_end.append(
            "(gues * gues - {0} ) > epsilon  || ({0} - gues * gues) > epsilon ".format(
                protocol_params.getElementByIndex(0).identifier,
            )
        )
    elif type == 3:
        action.description_end.append("return = gues")

    if type == 2:
        action.precondition.addElement(
            Node("(", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.precondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.gues",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.precondition.addElement(
            Node("*", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.precondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.gues",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.precondition.addElement(
            Node("-", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.precondition.addElement(
            Node(
                protocol_params.getElementByIndex(0).identifier,
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.precondition.addElement(
            Node(")", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.precondition.addElement(
            Node(">", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.precondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.epsilon",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.precondition.addElement(
            Node("||", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )

        action.precondition.addElement(
            Node("(", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.precondition.addElement(
            Node(
                protocol_params.getElementByIndex(0).identifier,
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.precondition.addElement(
            Node("-", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.precondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.guess",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.precondition.addElement(
            Node("*", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.precondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.guess",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.precondition.addElement(
            Node(")", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.precondition.addElement(
            Node(">", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.precondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.epsilon",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )

        action.postcondition.addElement(
            Node("1", element_type=ElementsTypes.NUMBER_ELEMENT)
        )
    else:
        action.precondition.addElement(
            Node("1", element_type=ElementsTypes.NUMBER_ELEMENT)
        )

    if type == 0:
        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.guess",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("=", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(0).identifier}",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("/", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node("2.0", element_type=ElementsTypes.NUMBER_ELEMENT)
        )
        action.postcondition.addElement(
            Node(";", element_type=ElementsTypes.SEMICOLON_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.epsilon",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("=", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node("0.000001", element_type=ElementsTypes.NUMBER_ELEMENT)
        )
    elif type == 1:
        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.guess",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("=", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node("(", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.guess",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("+", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                protocol_params.getElementByIndex(0).identifier,
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("/", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.guess",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node(")", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node("/", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                "2.0",
                element_type=ElementsTypes.NUMBER_ELEMENT,
            )
        )
    elif type == 3:
        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.return",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        action.postcondition.addElement(
            Node("=", element_type=ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(
            Node(
                f"{protocol_params.getElementByIndex(1).identifier}.guess",
                element_type=ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )

    if type == 2:
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


def sqrt2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.System_tf_callContext,
    sv_structure: Structure | None = None,
    destination_node_array: NodeArray | None = None,
):

    # PREPARE INPUT VAR
    input_var: str = ctx.list_of_arguments().getText()

    input_value_element_type = ElementsTypes.NUMBER_ELEMENT
    input_value_type = DeclTypes.INT

    if isNumericString(input_var) is None:
        decl: Declaration = self.module.declarations.findElement(input_var)
        if decl:
            input_var = f"{self.module.ident_uniq_name}.{decl.identifier}"
            input_value_element_type = ElementsTypes.IDENTIFIER_ELEMENT
            input_value_type = decl.data_type

    # DECLARE VARS

    createTypedef(
        self,
        "sqrt_struct",
        ctx.getSourceInterval(),
        [
            ("result", input_value_type),
            ("gues", DeclTypes.REAL),
            ("epsilon", DeclTypes.REAL),
        ],
    )

    result_sqrt = createDeclaration(
        self,
        "sqrt_obj",
        DeclTypes.STRUCT,
        CounterTypes.UNIQ_NAMES_COUNTER,
        ctx.getSourceInterval(),
        "sqrt_struct",
    )

    # SET RESULT VAR TO ACTION NODE ARRAY
    if destination_node_array:
        node = Node(
            result_sqrt.identifier + ".result", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT
        )
        node.module_name = self.module.ident_uniq_name
        destination_node_array.addElement(node.copy())

    # PARAMETRS
    protocol_params_input: ParametrArray = createParametrArray(
        self,
        [input_var, self.module.ident_uniq_name + "." + result_sqrt.identifier],
    )

    protocol_params: ParametrArray = createParametrArray(
        self,
        [
            "x",
            "obj",
        ],
    )

    # PROTOCOLS
    beh_protocol_name = "SQRT"
    sqrt_structure = Structure(beh_protocol_name, (0, 0), ElementsTypes.TASK_ELEMENT)
    sqrt_protocol = Protocol(
        beh_protocol_name,
        (0, 0),
        ElementsTypes.TASK_ELEMENT,
        parametrs=protocol_params,
    )
    sqrt_structure.behavior.append(sqrt_protocol)

    sqrt_ltz_action, sqrt_nan_action = createSqrtStart(self, protocol_params)

    sqrt_protocol.addBody(
        BodyElement(
            "{0}.{1}".format(
                sqrt_ltz_action.getNameWithParams(), sqrt_nan_action.getNameWithParams()
            ),
            sqrt_ltz_action,
            ElementsTypes.IF_CONDITION_LEFT,
        )
    )

    sqrt_init_action, sqrt_init_protocol = createSqrtAction(self, 0, protocol_params)
    sqrt_body_action, sqrt_body_protocol = createSqrtAction(self, 1, protocol_params)
    sqrt_cond_action, sqrt_main_protocol = createSqrtAction(self, 2, protocol_params)
    sqrt_result_action, sqrt_result_protocol = createSqrtAction(
        self, 3, protocol_params
    )

    sqrt_protocol.addBody(
        BodyElement(
            "!{0}.{1}.{2}".format(
                sqrt_ltz_action.getNameWithParams(),
                sqrt_init_action.getNameWithParams(),
                sqrt_main_protocol.getName(),
            ),
            sqrt_ltz_action,
            ElementsTypes.IF_CONDITION_RIGTH,
        )
    )

    sqrt_main_protocol.body[0].identifier = sqrt_main_protocol.body[
        0
    ].pointer_to_related.getNameWithParams()
    sqrt_main_protocol.body[0].identifier += "." + sqrt_body_action.getNameWithParams()
    sqrt_main_protocol.body[0].identifier += "." + sqrt_main_protocol.getName()
    sqrt_main_protocol.body[0].parametrs = ParametrArray()

    sqrt_main_protocol.addBody(
        BodyElement(
            f"!{sqrt_cond_action.getNameWithParams()}",
            sqrt_cond_action,
            ElementsTypes.IF_CONDITION_RIGTH,
        )
    )
    sqrt_main_protocol.body[1].identifier += (
        "." + sqrt_result_action.getNameWithParams()
    )

    sqrt_structure.behavior.append(sqrt_main_protocol)

    uniq, index = self.module.structures.addElement(sqrt_structure)

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


# beh_index = sqrt_structure.getLastBehaviorIndex()
# if beh_index is not None:
#     sqrt_structure.behavior[beh_index].addBody(
#          BodyElement(
#              pow_init_action.identifier,
#             pow_init_action,
#             ElementsTypes.ACTION_ELEMENT,
#              parametrs=protocol_params,
#         )
#      )
