from antlr4.tree import Tree

from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def extractCondition(ctx: SystemVerilogParser.Statement_or_nullContext):
    for child in ctx.getChildren():
        if type(child) is SystemVerilogParser.Event_controlContext:
            return child
        elif type(child) is Tree.TerminalNodeImpl:
            pass
        else:
            return extractCondition(child)


def forever2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Loop_statementContext,
    sv_structure: Structure,
):
    # Event_controlContext
    condition = extractCondition(ctx.statement_or_null())
    sensetive = self.extractSensetive(condition)

    protocol_params = ""
    if self.inside_the_task == True:
        task = self.module.tasks.getLastTask()
        if task is not None:
            protocol_params = "({0})".format(task.parametrs)

    forever_loop = "FOREVER_LOOP_{0}{1}".format(
        Counters_Object.getCounter(CounterTypes.FOREVER_COUNTER), protocol_params
    )
    beh_index = sv_structure.getLastBehaviorIndex()
    if beh_index is not None:
        sv_structure.behavior[beh_index].addBody(
            BodyElement(
                identifier=forever_loop,
                element_type=ElementsTypes.PROTOCOL_ELEMENT,
            )
        )

    beh_index = sv_structure.addProtocol(forever_loop)

    names_for_change = self.body2Aplan(
        ctx.statement_or_null(), sv_structure, ElementsTypes.FOREVER_ELEMENT
    )
    for element in names_for_change:
        self.module.name_change.deleteElement(element)

    forever_iteration = "FOREVER_ITERATION_{0}{1}".format(
        Counters_Object.getCounter(CounterTypes.FOREVER_COUNTER), protocol_params
    )

    sv_structure.behavior[beh_index].addBody(
        BodyElement(
            identifier=forever_iteration,
            element_type=ElementsTypes.PROTOCOL_ELEMENT,
        )
    )

    beh_index = sv_structure.addProtocol(forever_iteration)
    forever_sensetive_name = "Sensetive({0}, {1})".format(forever_loop, sensetive)
    sv_structure.behavior[beh_index].addBody(
        BodyElement(
            identifier=forever_sensetive_name,
            element_type=ElementsTypes.PROTOCOL_ELEMENT,
        )
    )

    Counters_Object.incrieseCounter(CounterTypes.FOREVER_COUNTER)
