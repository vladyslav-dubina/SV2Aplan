from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.protocols import Protocol
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def netAssignment2AplanImpl(
    self: SV2aplan, ctx: SystemVerilogParser.Net_assignmentContext
):
    if not self.module.processed_elements.isInProcessedElementAlready(
        ctx.getSourceInterval()
    ):
        (
            action_pointer,
            assign_name,
            source_interval,
            uniq_action,
        ) = self.expression2Aplan(
            ctx.getText(), ElementsTypes.ASSIGN_ELEMENT, ctx.getSourceInterval()
        )
        if assign_name is not None:
            if source_interval != ctx.getSourceInterval():
                Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                assign_b = "ASSIGN_B_{}".format(
                    Counters_Object.getCounter(CounterTypes.B_COUNTER)
                )
                struct_assign = Protocol(
                    assign_b,
                    ctx.getSourceInterval(),
                    ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT,
                )
                assign_name = f"Sensetive({assign_name})"
                struct_assign.addBody((assign_name, ElementsTypes.ACTION_ELEMENT))
                self.module.out_of_block_elements.addElement(struct_assign)
