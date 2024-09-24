from typing import Tuple
from classes.actions import Action
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.parametrs import Parametr, ParametrArray
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan


def createModfAction(self: SV2aplan, grater_than_zero: bool):
    name_part = "_ltz"
    if grater_than_zero:
        name_part = "_gtz"
    action = Action(
        f"modf{name_part}", (0, 0), element_type=ElementsTypes.ASSIGN_ELEMENT
    )  # modf x grater than 0 case

    action.parametrs.addElement(
        Parametr(
            "x",
            "var",
        )
    )

    action.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )
    if grater_than_zero:
        action.description_end.append(f"integral_part = x - (x - (x / 1))")
    else:
        action.description_end.append(f"integral_part = x - (x - (x / 1)) - 1")

    action.description_end.append(f"fractional_part = x - integral_part")

    if grater_than_zero:
        action.description_action_name = "modf the case when greater than zero"
    else:
        action.description_action_name = "modf the case when less than zero"

    action.precondition.addElement(Node("x", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT))
    if grater_than_zero:
        action.precondition.addElement(
            Node(">=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
    else:
        action.precondition.addElement(
            Node("<", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
    action.precondition.addElement(Node("0", (0, 0), ElementsTypes.NUMBER_ELEMENT))

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
    if not grater_than_zero:
        action.postcondition.addElement(
            Node("-", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        action.postcondition.addElement(Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT))
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

    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action)

    if action_check_result is None:
        action_pointer: Action = action
        self.module.actions.addElement(action)

    return action_pointer


def modf2AplanImpl(
    self: SV2aplan,
    source_interval: Tuple[int, int],
    sv_structure: Structure | None = None,
    destination_node_array: NodeArray | None = None,
    input_params: ParametrArray = ParametrArray(),
    inside_method: bool = True,
):
    action_name = "modf"

    action_gtz: Action = createModfAction(self, True)
    action_ltz: Action = createModfAction(self, False)

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

    protocol_params: ParametrArray = ParametrArray()
    protocol_params.addElement(
        Parametr(
            "x",
            "var",
        )
    )

    beh_protocol_name = "MODF".format()

    modf_structure = Structure(beh_protocol_name, (0, 0), ElementsTypes.TASK_ELEMENT)
    modf_protocol = Protocol(
        beh_protocol_name,
        (0, 0),
        ElementsTypes.TASK_ELEMENT,
        parametrs=protocol_params,
    )
    modf_structure.behavior.append(modf_protocol)

    beh_index = modf_structure.getLastBehaviorIndex()
    if beh_index is not None:
        body = f"{action_gtz.identifier}"
        modf_structure.behavior[beh_index].addBody(
            BodyElement(
                body,
                action_gtz,
                ElementsTypes.IF_CONDITION_LEFT,
                parametrs=protocol_params,
            )
        )
        body = f"{action_ltz.identifier}"
        modf_structure.behavior[beh_index].addBody(
            BodyElement(
                body,
                action_ltz,
                ElementsTypes.IF_CONDITION_RIGTH,
                parametrs=protocol_params,
            )
        )

    self.module.structures.addElement(modf_structure)

    if sv_structure:
        beh_index = sv_structure.getLastBehaviorIndex()
        if beh_index is not None:
            sv_structure.behavior[beh_index].addBody(
                BodyElement(
                    identifier=beh_protocol_name,
                    element_type=ElementsTypes.PROTOCOL_ELEMENT,
                    parametrs=input_params,
                )
            )
