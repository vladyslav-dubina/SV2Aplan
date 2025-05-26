from typing import List
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.parametrs import Parametr, ParametrArray
from translator.classes.base_translator import BaseTranslator


class SizeTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.System_tf_callContext,
        parametrs: ParametrArray,
        description_start: List[str],
        description_end: List[str],
        precondition: NodeArray,
        postcondition: NodeArray,
    ):
        name_part = "size"
        element_type = ElementsTypes.ASSIGN_ELEMENT
        self.module.declarations.addElement(
            Declaration(
                DeclTypes.INT,
                "return_size",
                "",
                "",
                0,
                "",
                0,
                ctx.getSourceInterval(),
            )
        )

        parametrs.addElement(
            Parametr(
                "result",
                "var",
            )
        )

        array = ctx.list_of_arguments().getText()
        decl = self.module.declarations.findElement(array)
        if decl is None:
            return

        node = Node(
            array,
            ctx.list_of_arguments().getSourceInterval(),
            ElementsTypes.ARRAY_SIZE_ELEMENT,
        )

        action_name = f"size_{array}"
        node.module_name = self.module.ident_uniq_name
        description_start.append(
            f"{self.module.identifier}#{self.module.ident_uniq_name}"
        )
        description_end.append(f"result = {array}.size")
        description_action_name = name_part

        precondition.addElement(Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT))
        postcondition.addElement(
            Node("result", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
        )
        postcondition.addElement(Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
        postcondition.addElement(node.copy())
        body = f"{action_name}(return_size)"

        return (
            name_part,
            element_type,
            action_name,
            parametrs,
            description_start,
            description_end,
            description_action_name,
            precondition,
            postcondition,
            body,
        )
