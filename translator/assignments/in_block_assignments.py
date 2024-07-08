from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.module import Module
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def blockAssignment2AplanImpl(
    self: SV2aplan, ctx, module: Module, sv_structure: Structure
):
    action_name, source_interval, uniq_action = self.expression2Aplan(
        ctx.getText(),
        ElementsTypes.ASSIGN_ELEMENT,
        ctx.getSourceInterval(),
    )
    beh_index = sv_structure.getLastBehaviorIndex()

    if type(ctx) is SystemVerilogParser.Nonblocking_assignmentContext:
        action_name = "Sensetive(" + action_name + ")"
    if beh_index is not None:
        sv_structure.behavior[beh_index].addBody(
            (action_name, ElementsTypes.ACTION_ELEMENT)
        )
    else:
        Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
        b_index = sv_structure.addProtocol(
            "B_{}".format(Counters_Object.getCounter(CounterTypes.B_COUNTER))
        )
        sv_structure.behavior[b_index].addBody(
            (action_name, ElementsTypes.ACTION_ELEMENT)
        )
