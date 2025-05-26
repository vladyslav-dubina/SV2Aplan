import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.element_types import ElementsTypes
from classes.parametrs import Parametr
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import parallelAssignment2Assignment


class ReturnTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

       from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.ExpressionContext,
        sv_structure: Structure | None = None,
    ) -> None:

        action_pointer, action_name, source_interval, uniq_action = (
            self._translator_ptr.translate(
                "expr", ctx, ElementsTypes.ASSIGN_ELEMENT, sv_structure=sv_structure
            )
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

        beh_index = sv_structure.getLastBehaviorIndex()
        sv_structure.behavior[beh_index].addBody(
            BodyElement(action_name, action_pointer, ElementsTypes.ACTION_ELEMENT)
        )
