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

    action_pointer, action_name, source_interval, uniq_action = self.expression2Aplan(
        ctx,
        ElementsTypes.ASSIGN_ELEMENT,
        sv_structure=sv_structure,
    )
    if action_name is not None:
        beh_index = sv_structure.getLastBehaviorIndex()

        if type(ctx) is SystemVerilogParser.Nonblocking_assignmentContext:
            action_name = "Sensetive(" + action_name + ")"
        if beh_index is not None:
            sv_structure.behavior[beh_index].addBody(
                (action_pointer, action_name, ElementsTypes.ACTION_ELEMENT)
            )
        else:
            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
            protocol_params = ""
            if self.inside_the_task == True:
                task = self.module.tasks.getLastTask()
                if task is not None:
                    protocol_params = "({0})".format(task.parametrs)
            b_index = sv_structure.addProtocol("B_{0}".format(action_pointer.getName()))
            sv_structure.behavior[b_index].addBody(
                (action_pointer, action_name, ElementsTypes.ACTION_ELEMENT)
            )
