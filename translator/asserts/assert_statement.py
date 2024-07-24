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
        (
            action_pointer,
            assert_name,
            source_interval,
            uniq_action,
        ) = self.expression2Aplan(
            expression.getText(),
            ElementsTypes.ASSERT_ELEMENT,
            ctx.getSourceInterval(),
        )
        if assert_name is not None:
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
    action_pointer, assert_name, source_interval, uniq_action = self.expression2Aplan(
        ctx.expression().getText(),
        ElementsTypes.ASSERT_ELEMENT,
        ctx.expression().getSourceInterval(),
        sv_structure=sv_structure,
    )
    if assert_name is not None:
        Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
        protocol_params = ""
        if self.inside_the_task == True:
            task = self.module.tasks.getLastTask()
            if task is not None:
                protocol_params = "({0})".format(task.parametrs)
        assert_b = "ASSERT_B_{0}{1}".format(
            Counters_Object.getCounter(CounterTypes.B_COUNTER), protocol_params
        )
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
