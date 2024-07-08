from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.protocols import Protocol
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def assertPropertyStatement2AplanImpl(
    self: SV2aplan, ctx: SystemVerilogParser.Assert_property_statementContext
):
    expression = ctx.property_spec()
    if expression is not None:
        assert_name, source_interval, uniq_action = self.expression2Aplan(
            expression.getText(),
            ElementsTypes.ASSERT_ELEMENT,
            ctx.getSourceInterval(),
        )
        Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
        assert_b = "ASSERT_B_{}".format(
            Counters_Object.getCounter(CounterTypes.B_COUNTER)
        )
        struct_assert = Protocol(
            assert_b,
            ctx.getSourceInterval(),
        )
        struct_assert.addBody(
            ("{0}.Delta + !{0}.0".format(assert_name), ElementsTypes.ACTION_ELEMENT)
        )
        self.module.out_of_block_elements.addElement(struct_assert)


def assertInBlock2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Simple_immediate_assert_statementContext,
    sv_structure: Structure,
):
    assert_name, source_interval, uniq_action = self.expression2Aplan(
        ctx.expression().getText(),
        ElementsTypes.ASSERT_ELEMENT,
        ctx.expression().getSourceInterval(),
    )
    Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
    assert_b = "ASSERT_B_{}".format(Counters_Object.getCounter(CounterTypes.B_COUNTER))
    beh_index = sv_structure.addProtocol(assert_b)
    sv_structure.behavior[beh_index].addBody(
        (
            "{0}.Delta + !{0}.0".format(assert_name),
            ElementsTypes.ACTION_ELEMENT,
        )
    )
    if beh_index != 0:
        sv_structure.behavior[beh_index - 1].addBody(
            (assert_b, ElementsTypes.PROTOCOL_ELEMENT)
        )
