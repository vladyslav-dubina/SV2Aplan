from antlr4_verilog.systemverilog import SystemVerilogParser

from classes.always import Always
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def always2AplanImpl(self: SV2aplan, ctx: SystemVerilogParser.Always_constructContext):

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
    Counters_Object.incrieseCounter(CounterTypes.ALWAYS_COUNTER)
    always_name = (
        always_keyword.upper()
        + "_"
        + str(Counters_Object.getCounter(CounterTypes.ALWAYS_COUNTER))
    )
    always = Always(
        always_name,
        sensetive,
        ctx.getSourceInterval(),
    )
    if self.module.input_parametrs is not None:
        always.parametrs += self.module.input_parametrs
    always.addProtocol(always_name)
    names_for_change = self.body2Aplan(
        always_body, always, ElementsTypes.ALWAYS_ELEMENT
    )
    for element in names_for_change:
        self.module.name_change.deleteElement(element)
    self.module.structures.addElement(always)
