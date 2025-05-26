import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.loop_stmt import WhileStmt
from classes.structure import Structure
from antlr4_verilog.systemverilog import SystemVerilogParser
from translator.classes.base_translator import BaseTranslator


class WhileStructTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

       from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Loop_statementContext,
    ) -> None:

        self.createStatement(
            "WHILE_LOOP", ElementsTypes.WHILE_ELEMENT, None, CounterTypes.LOOP_COUNTER
        )
        while_stmt: Structure | None = self.structure_pointer_list.getLastElement()
        if not isinstance(while_stmt, WhileStmt):
            return

        self._translator_ptr.getTranslator("loop").createBeh(
            while_stmt, ctx.expression()
        )

        self._translator_ptr.body2Aplan(ctx.statement_or_null(), while_stmt)
