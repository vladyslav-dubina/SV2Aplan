import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from translator.classes.base_translator import BaseTranslator


class MethodCallTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    # TODO Change sv_structure to get struct from list and similar for dest_node
    def translate(
        self,
        ctx: SystemVerilogParser.Method_call_bodyContext,
    ) -> None:
        task_identifier = ctx.method_identifier().getText()
        self.last_node_array.removeElementByIndex(len(self.last_node_array) - 1)
        node = self.last_node_array.getElementByIndex(len(self.last_node_array) - 1)
        object_identifier = node.identifier
        self.last_node_array.removeElementByIndex(len(self.last_node_array) - 1)
        argument_list = ctx.list_of_arguments().getText()

        (
            argument_list,
            argument_list_with_replaced_names,
        ) = self._translator_ptr.getTranslator("expr").prepareExpressionString(
            argument_list
        )

        argument_list_with_replaced_names = (
            self.module.findAndChangeNamesToAgentAttrCall(
                argument_list_with_replaced_names
            )
        )

        object = self.module.packages_and_objects.findModuleByUniqIdentifier(
            object_identifier
        )

        task = object.tasks.getElement(task_identifier)

        self._translator_ptr.getTranslator("task_call").createCall(
            task,
            object_identifier,
            argument_list_with_replaced_names,
            ctx.getSourceInterval(),
        )
