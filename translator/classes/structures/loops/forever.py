from antlr4.tree import Tree

from antlr4_verilog.systemverilog import SystemVerilogParser

from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.loop_stmt import ForeverStmt
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator
from utils.utils import Counters_Object


def extractCondition(self, ctx: SystemVerilogParser.Statement_or_nullContext):
    for child in ctx.getChildren():
        if type(child) is SystemVerilogParser.Event_controlContext:
            return child
        elif type(child) is Tree.TerminalNodeImpl:
            pass
        else:
            return extractCondition(child)


class ForeverStructTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Loop_statementContext,
    ) -> None:
        condition = extractCondition(ctx.statement_or_null())
        sensetive = self.extractSensetive(condition)
        self.createStatement("FOREVER_LOOP", ElementsTypes.FOREVER_ELEMENT, sensetive)
        forever_stmt: Structure | None = self.structure_pointer_list.getLastElement()
        if not isinstance(forever_stmt, ForeverStmt):
            return

        self.body2Aplan(ctx.statement_or_null(), forever_stmt)


class ForeverIterationTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Loop_statementContext,
    ) -> None:
        forever_stmt: Structure | None = self.structure_pointer_list.getLastElement()
        if not isinstance(forever_stmt, ForeverStmt):
            return
        condition = extractCondition(ctx.statement_or_null())
        sensetive = self.extractSensetive(condition)

        protocol_params = self.getProtocolParams()

        forever_iteration = "FOREVER_ITERATION_{0}".format(
            Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER),
        )

        forever_stmt.behavior[0].addBody(
            BodyElement(
                identifier=forever_iteration,
                element_type=ElementsTypes.PROTOCOL_ELEMENT,
                parametrs=protocol_params,
            )
        )

        beh_index = forever_stmt.addProtocol(
            forever_iteration,
            inside_the_task=(self.inside_the_task or self.inside_the_function),
        )

        forever_sensetive_name = "Sensetive({0}, {1})".format(
            forever_stmt.behavior[0].getName(),
            sensetive,
        )

        forever_stmt.behavior[beh_index].addBody(
            BodyElement(
                identifier=forever_sensetive_name,
                element_type=ElementsTypes.PROTOCOL_ELEMENT,
            )
        )

        Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
