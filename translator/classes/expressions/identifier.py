import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from Core.src.classes.declarations import DeclTypes, Declaration
from Core.src.classes.element_types import ElementsTypes
from Core.src.classes.node import Node, NodeArray
from Core.src.classes.parametrs import Parametr
from translator.classes.base_translator import BaseTranslator


class IdentifierTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.IdentifierContext,
    ) -> None:
        if self.last_node_array is None:
            return

        identifier = ctx.getText()
        if self.last_node_array.isAssign():
            self.findStruct()
            if self.inside_the_task:
                task = self.design_unit.tasks.getLastTask()
                if task and identifier == task.identifier:
                    return_var_name = f"return_{task.identifier}"
                    identifier = return_var_name
                    task.parametrs.addElement(
                        Parametr(
                            f"{return_var_name}",
                            "var",
                        )
                    )

        index = self.last_node_array.addElement(
            Node(
                identifier,
                ctx.getSourceInterval(),
                ElementsTypes.IDENTIFIER_ELEMENT,
            )
        )
        node = self.last_node_array.getElementByIndex(index)

        if self.last_dot_operator:
            self.last_node_array.addElement(
                Node(
                    self.last_dot_operator,
                    (0, 0),
                    ElementsTypes.DOT_ELEMENT,
                )
            )

        const_value = self.findEnumConst(identifier)
        if const_value:
            node.identifier = const_value
        else:
            identifier, decl = self.design_unit.declarations.replaceDeclName(identifier)
            if isinstance(decl, Declaration):
                node.identifier = identifier
                if self.design_unit.element_type == ElementsTypes.CLASS_ELEMENT:
                    node.design_unit_name = "object_pointer"
                else:
                    node.design_unit_name = self.design_unit.ident_uniq_name

                if decl.data_type == DeclTypes.ARRAY:
                    node.element_type = ElementsTypes.ARRAY_ELEMENT

        node.identifier = self._translator_ptr.translate("param_call", node.identifier)
