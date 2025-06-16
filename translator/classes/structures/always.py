import typing
from antlr4_verilog.systemverilog import SystemVerilogParser

from classes.always import Always
from classes.counters import CounterTypes
from translator.classes.base_translator import BaseTranslator
from utils.utils import Counters_Object


class AlwaysStructureTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Always_constructContext) -> None:
        sensetive = None

        always_keyword = ctx.always_keyword().getText()
        statement_item = ctx.statement().statement_item()
        if statement_item.procedural_timing_control_statement() is not None:
            event_expression = (
                statement_item.procedural_timing_control_statement()
                .procedural_timing_control()
                .event_control()
                .event_expression()
            )
            if event_expression is not None:
                sensetive = self.extractSensetive(event_expression)
            always_body = (
                statement_item.procedural_timing_control_statement().statement_or_null()
            )
        else:
            always_body = statement_item

        always_name = (
            always_keyword.upper()
            + "_"
            + str(Counters_Object.getCounter(CounterTypes.STRUCT_COUNTER))
        )
        always = Always(
            always_keyword.upper(),
            sensetive,
            ctx.getSourceInterval(),
            Counters_Object.getCounter(CounterTypes.STRUCT_COUNTER),
        )
        if self.module.input_parametrs is not None:
            always.parametrs += self.module.input_parametrs
        always.addProtocol(
            always_name,
            inside_the_task=self.inside_the_task,
        )

        self.module.structures.addElement(always)
        self.structure_pointer_list.addElement(always)
        Counters_Object.incriese(CounterTypes.STRUCT_COUNTER)
