import re
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from translator.classes.base_translator import BaseTranslator


class BitSelectionTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: (
            SystemVerilogParser.Bit_selectContext
            | SystemVerilogParser.Constant_bit_selectContext
        ),
    ) -> None:

        if not self.last_node_array:
            return

        if isinstance(ctx, SystemVerilogParser.Bit_selectContext):
            expression = ctx.expression()
        elif isinstance(ctx, SystemVerilogParser.Constant_bit_selectContext):
            expression = ctx.constant_expression()

        for element in expression:

            bit = element.getText()

            index = self.last_node_array.addElement(
                Node(bit, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
            )
            node = self.last_node_array.getElementByIndex(index)
            node.bit_selection = True

            bit, decl = self.module.declarations.replaceDeclName(bit)

            if isinstance(decl, Declaration):
                node.identifier = bit
                node.module_name = self.module.ident_uniq_name

            if self.current_genvar_value is not None:
                (genvar, value) = self.current_genvar_value
                node.identifier = re.sub(
                    r"\b{}\b".format(re.escape(genvar)),
                    f"{value}",
                    node.identifier,
                )

            node.identifier = self._translator_ptr.translate(
                "param_call", node.identifier
            )
