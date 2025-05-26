import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray, RangeTypes
from translator.classes.base_translator import BaseTranslator


class RangeSelectionTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

       from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Part_select_rangeContext,
        destination_node_array: NodeArray,
    ) -> None:
        if destination_node_array is not None:
            expressions = ctx.constant_range().constant_expression()
            for index, element in enumerate(expressions):
                if index != 0:
                    range = ","
                    destination_node_array.addElement(
                        Node(
                            range,
                            ctx.getSourceInterval(),
                            ElementsTypes.OPERATOR_ELEMENT,
                        )
                    )

                range = element.getText()
                node_index = destination_node_array.addElement(
                    Node(range, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
                )
                node = destination_node_array.getElementByIndex(node_index)
                if len(ctx.constant_range().constant_expression()) == 1:
                    node.range_selection = RangeTypes.START_END
                else:
                    if index == 0:
                        node.range_selection = RangeTypes.START
                    if index == len(ctx.constant_range().constant_expression()) - 1:
                        node.range_selection = RangeTypes.END

                node.identifier = self._translator_ptr.translate(
                    "param_call", node.identifier
                )
