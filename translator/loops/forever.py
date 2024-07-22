from antlr4.tree import Tree

from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
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
    forever_name = "FOREVER_{0}".format(
        Counters_Object.getCounter(CounterTypes.FOREVER_COUNTER)
    )

    forever_sensetive_name = "Sensetive({0}, {1})".format(forever_name, sensetive)

    beh_index = sv_structure.getLastBehaviorIndex()
    if beh_index is not None:
        sv_structure.behavior[beh_index].addBody(
            (
                forever_sensetive_name,
                ElementsTypes.FOREVER_ELEMENT,
            )
        )

    protocol_params = ""
    if self.inside_the_task == True:
        task = self.module.tasks.getLastTask()
        if task is not None:
            protocol_params = "({0})".format(task.parametrs)

    beh_index = sv_structure.addProtocol("{0}{1}".format(forever_name, protocol_params))

    names_for_change = self.body2Aplan(
        ctx.statement_or_null(), sv_structure, ElementsTypes.FOREVER_ELEMENT
    )
    for element in names_for_change:
        self.module.name_change.deleteElement(element)
