import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from Core.src.classes.element_types import ElementsTypes
from Core.src.classes.node import Node
from translator.classes.base_translator import BaseTranslator


class OperatorTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    _unused_operators = "inputoutputbeginend[];intwirereg"

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx) -> None:
        if self.last_node_array is not None:
            operator = ctx.getText()

            if self.isNotUsedOperator(operator):
                return

            operator_type = ElementsTypes.OPERATOR_ELEMENT
            if "." in operator:
                operator_type = ElementsTypes.DOT_ELEMENT

            if self.last_node_array.node_type == ElementsTypes.POSTCONDITION_ELEMENT:
                operator = self.str_formater.parallelAssignment2Assignment(operator)

            index = self.last_node_array.addElement(
                Node(operator, ctx.getSourceInterval(), operator_type)
            )
            node = self.last_node_array.getElementByIndex(index)
            decl = self.design_unit.declarations.getElement(node.identifier)
            if decl:
                node.design_unit_name = self.design_unit.ident_uniq_name

    def isNotUsedOperator(self, operator: str):
        if operator in self._unused_operators:
            return True
        else:
            return False
