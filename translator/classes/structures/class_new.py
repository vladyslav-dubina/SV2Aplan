from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.element_types import ElementsTypes
from classes.node import NodeArray
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator


class ClassNewTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    # TODO Change sv_structure to get struct from list and similar for dest_node
    def translate(
        self,
        ctx: SystemVerilogParser.Class_newContext,
        sv_structure: Structure,
        destination_node_array: NodeArray | None = None,
    ) -> None:
        destination_node_array.removeElementByIndex(destination_node_array.getLen() - 1)
        node = destination_node_array.getElementByIndex(
            destination_node_array.getLen() - 1
        )
        object_identifier = node.identifier
        destination_node_array.removeElementByIndex(destination_node_array.getLen() - 1)
        task_identifier = "new"

        argument_list = ctx.list_of_arguments().getText()
        (
            argument_list,
            argument_list_with_replaced_names,
        ) = self._translator_ptr.getTranslator("expr").prepareExpressionString(
            argument_list, ElementsTypes.TASK_ELEMENT
        )

        argument_list_with_replaced_names = self.module.declarations.replaseDeclNames(
            argument_list_with_replaced_names
        )

        argument_list_with_replaced_names = (
            self.module.findAndChangeNamesToAgentAttrCall(
                argument_list_with_replaced_names
            )
        )

        object = self.module.packages_and_objects.findModuleByUniqIdentifier(
            object_identifier
        )

        task = object.tasks.findElement(task_identifier)
        self._translator_ptr.getTranslator("task_call").createCall(
            task,
            sv_structure,
            destination_node_array,
            object_identifier,
            argument_list_with_replaced_names,
            ctx.getSourceInterval(),
        )
