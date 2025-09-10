import re
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from Core.src.classes.declarations import Declaration
from Core.src.classes.element_types import ElementsTypes
from Core.src.classes.node import Node
from translator.classes.base_translator import BaseTranslator


class UnpackedDimentionTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Unpacked_dimensionContext,
    ) -> None:
        expression = ctx.constant_expression()
        if not expression:
            return

        expression = expression.getText()
        if not self.last_node_array:
            return
        index = self.last_node_array.addElement(
            Node(expression, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
        )
        node = self.last_node_array.getElementByIndex(index)
        node.bit_selection = True

        expression, decl = self.design_unit.declarations.replaceDeclName(expression)
        if isinstance(decl, Declaration):
            node.identifier = expression
            node.design_unit_name = self.design_unit.ident_uniq_name

        if self.current_genvar_value is not None:
            (genvar, value) = self.current_genvar_value
            node.identifier = re.sub(
                r"\b{}\b".format(re.escape(genvar)),
                f"{value}",
                node.identifier,
            )

        node.identifier = self._translator_ptr.translate("param_call", node.identifier)
