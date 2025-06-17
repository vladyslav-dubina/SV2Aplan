import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.parametrs import Parametr
from AppModule.app.classes.protocols import BodyElement
from translator.classes.base_translator import BaseTranslator


class ReturnTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.ExpressionContext,
        # sv_structure: Structure | None = None,
    ) -> None:

        self.last_element_type = ElementsTypes.ASSIGN_ELEMENT
        self.last_operator = "="
        self._translator_ptr.translate("expr", ctx)

    def exit(
        self,
        ctx: SystemVerilogParser.ExpressionContext,
        # sv_structure: Structure | None = None,
    ) -> None:
        self.findStruct()
        action_pointer, action_name, source_interval, uniq_action = (
            self._translator_ptr.getTranslator("expr").exit()
        )

        task = self.module.tasks.getLastTask()

        return_var_name = f"return_{task.identifier}"
        task.parametrs.addElement(
            Parametr(
                f"{return_var_name}",
                "var",
            )
        )

        node = action_pointer.postcondition.getElementByIndex(0)
        node.identifier = return_var_name

        action_pointer.parametrs.addElement(
            Parametr(
                f"{return_var_name}",
                "var",
            )
        )

        action_pointer.findParametrInBodyAndSetParametrs(task.parametrs)
        action_parametrs_count = action_pointer.parametrs.getLen()
        action_name = f"{action_pointer.identifier}{action_pointer.parametrs.getIdentifiersListString(action_parametrs_count)}"

        beh_index = self.last_struct.getLastBehaviorIndex()
        self.last_struct.behavior[beh_index].addBody(
            BodyElement(action_name, action_pointer, ElementsTypes.ACTION_ELEMENT)
        )
