import typing
from antlr4.tree import Tree

from antlr4_verilog.systemverilog import SystemVerilogParser

from Core.src.classes.element_types import ElementsTypes
from Core.src.classes.loop_stmt import ForeverStmt
from Core.src.classes.protocols import BodyElement
from translator.classes.base_translator import BaseTranslator


def extractCondition(self, ctx: SystemVerilogParser.Statement_or_nullContext):
    for child in ctx.getChildren():
        if type(child) is SystemVerilogParser.Event_controlContext:
            return child
        elif type(child) is Tree.TerminalNodeImpl:
            pass
        else:
            return extractCondition(child)


class ForeverStructTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Loop_statementContext,
    ) -> None:
        condition = extractCondition(ctx.statement_or_null())
        sensetive = self.extractSensetive(condition)
        self.createStatement("FOREVER_LOOP", ElementsTypes.FOREVER_ELEMENT, sensetive)
        self.findStruct()
        if not isinstance(self.last_struct, ForeverStmt):
            return

        self._translator_ptr.body2Aplan(ctx.statement_or_null(), self.last_struct)


class ForeverIterationTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Loop_statementContext,
    ) -> None:
        self.findStruct()
        if not isinstance(self.last_struct, ForeverStmt):
            return
        condition = extractCondition(ctx.statement_or_null())
        sensetive = self.extractSensetive(condition)

        protocol_params = self.getProtocolParams()

        forever_iteration = "FOREVER_ITERATION_{0}".format(
            self.counters.get(self.counters.types.STRUCT_COUNTER),
        )

        self.last_struct.behavior[0].addBodyElement(
            BodyElement(
                identifier=forever_iteration,
                element_type=ElementsTypes.PROTOCOL_ELEMENT,
                parametrs=protocol_params,
            )
        )

        beh_index = self.last_struct.addProtocol(
            forever_iteration,
            inside_the_task=self.inside_the_task,
        )

        forever_sensetive_name = "Sensetive({0}, {1})".format(
            self.last_struct.behavior[0].getName(),
            sensetive,
        )

        self.last_struct.behavior[beh_index].addBodyElement(
            BodyElement(
                identifier=forever_sensetive_name,
                element_type=ElementsTypes.PROTOCOL_ELEMENT,
            )
        )

        self.counters.incriese(self.counters.types.STRUCT_COUNTER)
