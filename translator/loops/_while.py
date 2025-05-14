from antlr4.tree import Tree
from antlr4_verilog.systemverilog import SystemVerilogParser

from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.loop_stmt import WhileStmt
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def while2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Loop_statementContext,
):
    self.createStatementToSvStruct(
        "WHILE_LOOP", ElementsTypes.WHILE_ELEMENT, None, CounterTypes.LOOP_COUNTER
    )
    while_stmt: Structure | None = self.structure_pointer_list.getLastElement()
    if not isinstance(while_stmt, WhileStmt):
        return
    print(while_stmt)
    protocol_params = self.getProtocolParams()

    while_loop_identifier = "{0}_{1}".format(
        while_stmt.identifier,
        Counters_Object.getCounter(CounterTypes.LOOP_COUNTER) - 1,
    )
    while_iteration_name = "{0}_ITERATION".format(while_loop_identifier)

    while_body_name = "{0}_BODY".format(while_loop_identifier)

    while_stmt.behavior[0].addBody(
        BodyElement(
            identifier=while_iteration_name,
            element_type=ElementsTypes.PROTOCOL_ELEMENT,
            parametrs=protocol_params,
        )
    )

    beh_index = while_stmt.addProtocol(
        while_iteration_name,
        inside_the_task=(self.inside_the_task or self.inside_the_function),
    )

    condition = ctx.expression()
    (
        action_pointer,
        condition_name,
        source_interval,
        uniq_action,
    ) = self.expression2Aplan(condition, ElementsTypes.CONDITION_ELEMENT, while_stmt)

    while_stmt.behavior[beh_index].addBody(
        BodyElement(
            "{0}.({2}{1};{3}) + !{0}".format(
                condition_name,
                protocol_params if protocol_params is not None else "",
                while_body_name,
                while_iteration_name,
            ),
            action_pointer,
            ElementsTypes.ACTION_ELEMENT,
        )
    )

    beh_index = while_stmt.addProtocol(
        while_body_name,
        inside_the_task=(self.inside_the_task or self.inside_the_function),
    )

    self.body2Aplan(ctx.statement_or_null(), while_stmt)
