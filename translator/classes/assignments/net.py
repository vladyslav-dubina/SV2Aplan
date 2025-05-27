import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.protocols import BodyElement, Protocol
from translator.classes.base_translator import BaseTranslator
from utils.utils import Counters_Object


class NetAssignmentTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Net_assignmentContext) -> None:
        if not self.module.processed_elements.isInProcessedElementAlready(
            ctx.getSourceInterval()
        ):
            (
                action_pointer,
                assign_name,
                source_interval,
                uniq_action,
            ) = self._translator_ptr.translate(
                "expr", ctx, ElementsTypes.ASSIGN_SENSETIVE_ELEMENT
            )
            if assign_name is not None:
                if source_interval != ctx.getSourceInterval():
                    assign_b = "ASSIGN_B_{}".format(
                        Counters_Object.getCounter(CounterTypes.STRUCT_COUNTER)
                    )
                    Counters_Object.incrieseCounter(CounterTypes.STRUCT_COUNTER)
                    struct_assign = Protocol(
                        assign_b,
                        ctx.getSourceInterval(),
                        ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT,
                    )
                    struct_assign.addBody(
                        BodyElement(
                            assign_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                        )
                    )
                    self.module.out_of_block_elements.addElement(struct_assign)
