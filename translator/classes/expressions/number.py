import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import valuesToAplanStandart
from utils.utils import is_interval_contained


class NumberTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: (
            SystemVerilogParser.NumberContext
            | SystemVerilogParser.Constant_expressionContext
        ),
        #  destination_node_array: NodeArray,
    ) -> None:
        if not self.last_node_array:
            return

        value = valuesToAplanStandart(ctx.getText())
        len = self.last_node_array.getLen()

        # checking if it is not a number from unpacked dimension
        # if len > 0:
        #     prev_element = self.last_node_array.getElementByIndex(len - 1)
        #     if is_interval_contained(
        #         ctx.getSourceInterval(), prev_element.source_interval
        #     ):
        #         return

        # if len == 1:
        #     prev_element = self.last_node_array.getElementByIndex(len - 2)

        #     if is_interval_contained(
        #         ctx.getSourceInterval(), prev_element.source_interval
        #     ):
        #         return
        index = self.last_node_array.addElement(
            Node(value, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
        )
        node = self.last_node_array.getElementByIndex(index)
        decl = self.module.declarations.getElement(node.identifier)
        if decl:
            node.module_name = self.module.ident_uniq_name

        node.identifier = self._translator_ptr.translate("param_call", node.identifier)
