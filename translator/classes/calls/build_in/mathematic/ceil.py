import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from Core.src.classes.declarations import DeclTypes, Declaration
from Core.src.classes.node import Node, NodeArray
from Core.src.classes.actions import Action
from Core.src.classes.element_types import ElementsTypes
from Core.src.classes.parametrs import Parametr, ParametrArray
from Core.src.classes.protocols import BodyElement, Protocol
from Core.src.classes.structure import Structure
from translator.classes.base_translator import BaseTranslator


class CeilTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.System_tf_callContext,
        sv_structure: Structure | None = None,
        destination_node_array: NodeArray | None = None,
    ):
        input_var = ctx.list_of_arguments().getText()
        decl = None
        node_type = ElementsTypes.NUMBER_ELEMENT

        self.design_unit.declarations.addElement(
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

        if self.utils.isNumericString(input_var) is None:
            decl = self.design_unit.declarations.getElement(input_var)
            if decl:
                input_var = f"{self.design_unit.ident_uniq_name}.{decl.identifier}"
            node_type = ElementsTypes.IDENTIFIER_ELEMENT

        action_ceil_rtwp = self.createAction(True, node_type)
        action_ceil_rtfp = self.createAction(False, node_type)

        if destination_node_array:
            node = Node("result_ceil", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
            node.design_unit_name = self.design_unit.ident_uniq_name
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

        beh_protocol_name = "CEIL"

        ceil_structure = Structure(
            beh_protocol_name, ctx.getSourceInterval(), ElementsTypes.TASK_ELEMENT
        )
        ceil_protocol = Protocol(
            beh_protocol_name,
            ctx.getSourceInterval(),
            ElementsTypes.TASK_ELEMENT,
        )
        ceil_structure.behavior.append(ceil_protocol)

        beh_index = ceil_structure.getLastBehaviorIndex()
        if beh_index is not None:
            body = f"{action_ceil_rtwp.identifier}"
            ceil_structure.behavior[beh_index].addBodyElement(
                BodyElement(
                    body,
                    action_ceil_rtwp,
                    ElementsTypes.IF_CONDITION_LEFT,
                )
            )
            body = f"{action_ceil_rtfp.identifier}"
            ceil_structure.behavior[beh_index].addBodyElement(
                BodyElement(
                    body,
                    action_ceil_rtfp,
                    ElementsTypes.IF_CONDITION_RIGTH,
                )
            )

        self.design_unit.structures.addElement(ceil_structure)

        if sv_structure:
            self._translator_ptr.translate(
                "modf",
                ctx.getSourceInterval(),
                sv_structure,
                destination_node_array,
                protocol_params_input,
            )
            beh_index = sv_structure.getLastBehaviorIndex()
            if beh_index is not None:
                sv_structure.behavior[beh_index].addBodyElement(
                    BodyElement(
                        identifier=beh_protocol_name,
                        element_type=ElementsTypes.PROTOCOL_ELEMENT,
                    )
                )

    def createAction(self, return_the_wlole_part: bool, node_type: ElementsTypes):
        name_part = "_rtfp"
        if return_the_wlole_part:
            name_part = "_rtwp"

        action = Action(
            f"ceil{name_part}", (0, 0), element_type=ElementsTypes.ASSIGN_ELEMENT
        )

        action.description_start.append(
            f"{self.design_unit.identifier}#{self.design_unit.ident_uniq_name}"
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
        node.design_unit_name = self.design_unit.identifier
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
        node.design_unit_name = self.design_unit.ident_uniq_name
        action.postcondition.addElement(node.copy())
        action.postcondition.addElement(
            Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        node = Node(
            "integral_part",
            (0, 0),
            node_type,
        )
        node.design_unit_name = self.design_unit.ident_uniq_name
        action.postcondition.addElement(node.copy())
        if return_the_wlole_part:
            action.postcondition.addElement(
                Node("+", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
            )
            action.postcondition.addElement(
                Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT)
            )

        (
            action_pointer,
            action_check_result,
            source_interval,
        ) = self.design_unit.actions.isUniqAction(action)

        if action_check_result is None:
            action_pointer: Action = action
            self.design_unit.actions.addElement(action)

        return action_pointer
