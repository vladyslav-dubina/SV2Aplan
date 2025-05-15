from antlr4_verilog.systemverilog import SystemVerilogParser

from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.loop_stmt import WhileStmt
from classes.structure import Structure
from translator.loops.loops_utils import createLoopBeh
from translator.translator import Translator


def while2AplanImpl(
    self: Translator,
    ctx: SystemVerilogParser.Loop_statementContext,
):
    self.createStatementToSvStruct(
        "WHILE_LOOP", ElementsTypes.WHILE_ELEMENT, None, CounterTypes.LOOP_COUNTER
    )
    while_stmt: Structure | None = self.structure_pointer_list.getLastElement()
    if not isinstance(while_stmt, WhileStmt):
        return

    createLoopBeh(self, while_stmt, ctx.expression())

    self.body2Aplan(ctx.statement_or_null(), while_stmt)
