import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from Core.src.classes.declarations import Declaration
from Core.src.classes.element_types import ElementsTypes
from Core.src.classes.node import Node
from translator.classes.base_translator import BaseTranslator


class DynamicArrayNewTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Dynamic_array_newContext,
    ) -> None:
        size: str = ctx.getText()
        size = size.replace("new[", "[")
        size_expression = size
        size = self.str_formater.replaceValueParametrsCalls(
            self.design_unit.value_parametrs, size
        )
        size = self.utils.extractDimentionSize(size)
        if size == None:
            size = 0

        if not self.last_node_array:
            return

        elements = self.last_node_array.getElements()
        node_array_len = len(self.last_node_array)
        if node_array_len >= 2:
            decl = self.design_unit.declarations.getElement(
                elements[node_array_len - 2].identifier
            )

            if isinstance(decl, Declaration):
                decl.dimension_size = size
                decl.dimension_expression = size_expression
                while True:
                    node_array_len -= 1
                    if node_array_len < 0:
                        break
                    self.last_node_array.removeElementByIndex(node_array_len)

                node = Node(
                    decl.identifier,
                    ctx.getSourceInterval(),
                    ElementsTypes.ARRAY_SIZE_ELEMENT,
                )
                node.design_unit_name = self.design_unit.ident_uniq_name
                self.last_node_array.addElement(node)
                self.last_node_array.addElement(
                    Node(
                        "=",
                        ctx.getSourceInterval(),
                        ElementsTypes.OPERATOR_ELEMENT,
                    )
                )
                self.last_node_array.addElement(
                    Node(
                        str(size),
                        ctx.getSourceInterval(),
                        ElementsTypes.NUMBER_ELEMENT,
                    )
                )
