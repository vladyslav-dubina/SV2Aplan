import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.parametrs import Parametr
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import parallelAssignment2Assignment


class OperatorTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    _unused_operators = "inputoutputbeginend[];intwirereg"

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self, ctx
    ) -> None:
        self.findStruct()
        
        if self.last_node_array is not None:
            operator = ctx.getText()
            
            if self.isNotUsedOperator(operator):
                return

            operator_type = ElementsTypes.OPERATOR_ELEMENT
            if "." in operator:
                operator_type = ElementsTypes.DOT_ELEMENT

            if self.last_node_array.node_type == ElementsTypes.POSTCONDITION_ELEMENT:
                operator = parallelAssignment2Assignment(operator)

            index = self.last_node_array.addElement(
                Node(operator, ctx.getSourceInterval(), operator_type)
            )
            node = self.last_node_array.getElementByIndex(index)
            decl = self.module.declarations.getElement(node.identifier)
            if decl:
                node.module_name = self.module.ident_uniq_name
            if "=" in operator:
                if self.inside_the_task:
                    previus_node = self.last_node_array.getElementByIndex(index - 1)
                    task = self.module.tasks.getLastTask()
                    if previus_node.identifier == task.identifier:
                        return_var_name = f"return_{task.identifier}"
                        previus_node.identifier = return_var_name
                        task.parametrs.addElement(
                            Parametr(
                                f"{return_var_name}",
                                "var",
                            )
                        )

    def isNotUsedOperator(self, operator: str):
        if operator in self._unused_operators:
            return True
        else:
            return False
