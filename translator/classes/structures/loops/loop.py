import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator
from utils.utils import Counters_Object


class LoopStructTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: (
            SystemVerilogParser.Loop_generate_constructContext
            | SystemVerilogParser.Loop_statementContext
        ),
    ) -> None:
        if ctx.REPEAT():
            self._translator_ptr.translate("repeat", ctx)
        elif ctx.FOREVER():
            self._translator_ptr.translate("forever", ctx)
        elif ctx.WHILE():
            self._translator_ptr.translate("while", ctx)
        else:
            loop2AplanImpl(self, ctx)

    def createBeh(self, loop_stmt: Structure, condition):

        protocol_params = self.getProtocolParams()

        loop_identifier = "{0}_{1}".format(
            loop_stmt.identifier,
            Counters_Object.getCounter(CounterTypes.LOOP_COUNTER) - 1,
        )
        iteration_name = "{0}_ITERATION".format(loop_identifier)

        body_name = "{0}_BODY".format(loop_identifier)

        loop_stmt.behavior[0].addBody(
            BodyElement(
                identifier=iteration_name,
                element_type=ElementsTypes.PROTOCOL_ELEMENT,
                parametrs=protocol_params,
            )
        )

        beh_index = loop_stmt.addProtocol(
            iteration_name,
            inside_the_task=self.inside_the_task,
        )

        (
            action_pointer,
            condition_name,
            source_interval,
            uniq_action,
        ) = self._translator_ptr.translate(
            "expr", condition, ElementsTypes.CONDITION_ELEMENT, loop_stmt
        )

        loop_stmt.behavior[beh_index].addBody(
            BodyElement(
                "{0}.({2}{1};{3}) + !{0}".format(
                    condition_name,
                    protocol_params if protocol_params is not None else "",
                    body_name,
                    iteration_name,
                ),
                action_pointer,
                ElementsTypes.ACTION_ELEMENT,
            )
        )

        beh_index = loop_stmt.addProtocol(
            body_name,
            inside_the_task=self.inside_the_task,
        )


class LoopIterationTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: (
            SystemVerilogParser.Loop_generate_constructContext
            | SystemVerilogParser.Loop_statementContext
        ),
    ) -> None:
        if ctx.FOREVER():
            self._translator_ptr.translate("forever_iteration", ctx)
        elif ctx.REPEAT():
            return
