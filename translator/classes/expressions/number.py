import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.node import Node
from translator.classes.base_translator import BaseTranslator


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

        value = self.str_formater.valuesToAplanStandart(ctx.getText())

        index = self.last_node_array.addElement(
            Node(value, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
        )
        node = self.last_node_array.getElementByIndex(index)
        decl = self.module.declarations.getElement(node.identifier)
        if decl:
            node.module_name = self.module.ident_uniq_name

        node.identifier = self._translator_ptr.translate("param_call", node.identifier)
