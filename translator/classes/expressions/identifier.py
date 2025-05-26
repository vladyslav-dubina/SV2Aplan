from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from translator.classes.base_translator import BaseTranslator


class IdentifierTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.IdentifierContext,
        destination_node_array: NodeArray,
    ) -> None:
        if destination_node_array is not None:

            identifier = ctx.getText()
            index = destination_node_array.addElement(
                Node(
                    identifier,
                    ctx.getSourceInterval(),
                    ElementsTypes.IDENTIFIER_ELEMENT,
                )
            )
            node = destination_node_array.getElementByIndex(index)

            identifier, decl = self.module.declarations.replaceDeclName(identifier)

            if isinstance(decl, Declaration):
                node.identifier = identifier
                if self.module.element_type == ElementsTypes.CLASS_ELEMENT:
                    node.module_name = "object_pointer"
                else:
                    node.module_name = self.module.ident_uniq_name

                if decl.data_type == DeclTypes.ARRAY:
                    node.element_type = ElementsTypes.ARRAY_ELEMENT

            node.identifier = self._translator_ptr.translate(
                "param_call", node.identifier
            )
