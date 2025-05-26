from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import valuesToAplanStandart


class NumberTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.NumberContext,
        destination_node_array: NodeArray,
    ) -> None:

        if destination_node_array is not None:
            value = valuesToAplanStandart(ctx.getText())
            index = destination_node_array.addElement(
                Node(value, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
            )
            node = destination_node_array.getElementByIndex(index)
            decl = self.module.declarations.getElement(node.identifier)
            if decl:
                node.module_name = self.module.ident_uniq_name

            node.identifier = self._translator_ptr.translate(
                    "param_call", node.identifier
                )
