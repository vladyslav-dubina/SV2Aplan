from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.module import Module
from classes.protocols import Protocol
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def netAssignment2Aplan(ctx: SystemVerilogParser.Net_assignmentContext, module: Module):
    sv2aplan = SV2aplan(module)
    if not module.processed_elements.isInProcessedElementAlready(
        ctx.getSourceInterval()
    ):
        assign_name, source_interval = sv2aplan.expression2Aplan(
            ctx.getText(), ElementsTypes.ASSIGN_ELEMENT, ctx.getSourceInterval()
        )
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
            module.out_of_block_elements.addElement(struct_assign)
