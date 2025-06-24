import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.protocols import BodyElement, Protocol
from translator.classes.base_translator import BaseTranslator


class NetAssignmentTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Net_assignmentContext) -> None:
        if not self.design_unit.processed_elements.isInProcessedElementAlready(
            ctx.getSourceInterval()
        ):
            self.last_element_type = ElementsTypes.ASSIGN_SENSETIVE_ELEMENT
            self._translator_ptr.translate("expr", ctx)

    def exit(self, ctx: SystemVerilogParser.Net_assignmentContext) -> None:
        if not self.design_unit.processed_elements.isInProcessedElementAlready(
            ctx.getSourceInterval()
        ):
            (
                action_pointer,
                action_name,
                source_interval,
                uniq_action,
            ) = self._translator_ptr.getTranslator("expr").exit()

            if action_name is None:
                return

            if source_interval == ctx.getSourceInterval():
                return

            assign_b = "{}_B".format(action_pointer.getName(to_upper=True))
            self.counters.incriese(self.counters.types.ASSIGNMENT_COUNTER)
            struct_assign = Protocol(
                assign_b,
                ctx.getSourceInterval(),
                ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT,
            )
            struct_assign.addBodyElement(
                BodyElement(action_name, action_pointer, ElementsTypes.ACTION_ELEMENT)
            )
            self.design_unit.out_of_block_elements.addElement(struct_assign)
