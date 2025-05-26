from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import replaceValueParametrsCalls
from utils.utils import extractDimentionSize


class DynamicArrayNewTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    # TODO Change sv_structure to get struct from list and similar for dest_node
    def translate(
        self,
        ctx: SystemVerilogParser.Dynamic_array_newContext,
        sv_structure: Structure,
        destination_node_array: NodeArray | None = None,
    ) -> None:
        size: str = ctx.getText()
        size = size.replace("new[", "[")
        size_expression = size
        size = replaceValueParametrsCalls(self.module.value_parametrs, size)
        size = extractDimentionSize(size)
        if size == None:
            size = 0

        if destination_node_array:
            elements = destination_node_array.getElements()
            node_array_len = destination_node_array.getLen()
            if node_array_len >= 2:
                decl = self.module.declarations.findElement(
                    elements[node_array_len - 2].identifier
                )

                if isinstance(decl, Declaration):
                    decl.dimension_size = size
                    decl.dimension_expression = size_expression
                    while True:
                        node_array_len -= 1
                        if node_array_len < 0:
                            break
                        destination_node_array.removeElementByIndex(node_array_len)

                    node = Node(
                        decl.identifier,
                        ctx.getSourceInterval(),
                        ElementsTypes.ARRAY_SIZE_ELEMENT,
                    )
                    node.module_name = self.module.ident_uniq_name
                    destination_node_array.addElement(node)
                    destination_node_array.addElement(
                        Node(
                            "=",
                            ctx.getSourceInterval(),
                            ElementsTypes.OPERATOR_ELEMENT,
                        )
                    )
                    destination_node_array.addElement(
                        Node(
                            str(size),
                            ctx.getSourceInterval(),
                            ElementsTypes.NUMBER_ELEMENT,
                        )
                    )
