import re
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from translator.classes.base_translator import BaseTranslator


class UnpackedDimentionTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Unpacked_dimensionContext,
        destination_node_array: NodeArray,
    ) -> None:

        expression = ctx.constant_expression()
        if expression:
            expression = expression.getText()

            index = destination_node_array.addElement(
                Node(expression, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
            )
            node = destination_node_array.getElementByIndex(index)
            node.bit_selection = True

            expression, decl = self.module.declarations.replaceDeclName(expression)
            if isinstance(decl, Declaration):
                node.identifier = expression
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
