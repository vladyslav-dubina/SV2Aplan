from typing import List
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from Core.src.classes.declarations import DeclTypes, Declaration
from Core.src.classes.element_types import ElementsTypes
from Core.src.classes.node import Node, NodeArray
from Core.src.classes.parametrs import Parametr, ParametrArray
from translator.classes.base_translator import BaseTranslator


class SizeTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.System_tf_callContext,
        parametrs: ParametrArray,
        description_start: List[str],
        description_end: List[str],
        precondition: NodeArray,
        postcondition: NodeArray,
    ):
        name_part = "size"
        element_type = ElementsTypes.ASSIGN_ELEMENT
        self.design_unit.declarations.addElement(
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
        decl = self.design_unit.declarations.getElement(array)
        if decl is None:
            return

        node = Node(
            array,
            ctx.list_of_arguments().getSourceInterval(),
            ElementsTypes.ARRAY_SIZE_ELEMENT,
        )

        action_name = f"size_{array}"
        node.design_unit_name = self.design_unit.ident_uniq_name
        description_start.append(
            f"{self.design_unit.identifier}#{self.design_unit.ident_uniq_name}"
        )
        description_end.append(f"result = {array}.size")
        description_action_name = name_part

        precondition.addElement(Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT))
        postcondition.addElement(
            Node("result", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
        )
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
