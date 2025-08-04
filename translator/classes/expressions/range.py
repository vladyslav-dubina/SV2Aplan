import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.node import Node, RangeTypes
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

        expressions: typing.List[
            SystemVerilogParser.Constant_expressionContext
        ] = ctx.constant_expression()
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

            self._translator_ptr.getTranslator("expr").removeLastDote()

            range = element.getText()
            self.last_node_array.addElement(
                Node(range, element.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
            )
            node: Node = self.last_node_array.getLastElement()
            if expressions_len == 1:
                node.range_selection = RangeTypes.START_END
            else:
                if index == 0:
                    node.range_selection = RangeTypes.START
                if index == 1:
                    node.range_selection = RangeTypes.END

            node.identifier = self._translator_ptr.translate(
                "param_call", node.identifier
            )
