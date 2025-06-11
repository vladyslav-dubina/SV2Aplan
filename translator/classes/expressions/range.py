import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray, RangeTypes
from translator.classes.base_translator import BaseTranslator


class ConstantRangeSelectionTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Constant_rangeContext,
    ) -> None:
        if not self.last_node_array:
            return

        expressions: typing.List[SystemVerilogParser.Constant_expressionContext] = (
            ctx.constant_expression()
        )
        expressions_len = len(ctx.constant_expression())

        for index, element in enumerate(expressions):

            if index != 0:
                coma = ","
                self.last_node_array.addElement(
                    Node(
                        coma,
                        (0, 0),
                        ElementsTypes.OPERATOR_ELEMENT,
                    )
                )
            
            range = element.getText()
            node_index = self.last_node_array.addElement(
                Node(range, element.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
            )
            node = self.last_node_array.getElementByIndex(node_index)
            if expressions_len == 1:
                node.range_selection = RangeTypes.START_END
            else:
                if index == 0:
                    node.range_selection = RangeTypes.START
                if index == expressions_len - 1:
                    node.range_selection = RangeTypes.END

            node.identifier = self._translator_ptr.translate(
                "param_call", node.identifier
            )
