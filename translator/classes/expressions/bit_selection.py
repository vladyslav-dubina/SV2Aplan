import re
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from Core.src.classes.declarations import Declaration
from Core.src.classes.element_types import ElementsTypes
from Core.src.classes.node import Node
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

            self._translator_ptr.getTranslator("expr").removeLastDote()

            self.last_node_array.addElement(
                Node(bit, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
            )
            node: Node = self.last_node_array.getLastElement()
            node.bit_selection = True

            bit, decl = self.design_unit.declarations.replaceDeclName(bit)

            if isinstance(decl, Declaration):
                node.identifier = bit
                node.design_unit_name = self.design_unit.ident_uniq_name

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
