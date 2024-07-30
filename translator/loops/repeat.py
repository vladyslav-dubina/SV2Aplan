from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.protocols import Protocol
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import replaceParametrsCalls
from utils.utils import Counters_Object


def repeat2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Loop_statementContext,
    sv_structure: Structure,
):
    identifier = "repeat_var_{0}".format(
        Counters_Object.getCounter(CounterTypes.REPEAT_COUNTER)
    )
    expression = ctx.expression().getText()
    expression_source_interval = ctx.expression().getSourceInterval()
    expression = replaceParametrsCalls(self.module.parametrs, expression)

    assing_expr = "{0}={1}".format(identifier, 0)

    action_pointer, assign_name, source_interval, uniq_action = self.expression2Aplan(
        assing_expr,
        ElementsTypes.ASSIGN_ELEMENT,
        ctx.getSourceInterval(),
        sv_structure=sv_structure,
    )

    uniq, decl_index = self.module.declarations.addElement(
        Declaration(
            DeclTypes.INT,
            identifier,
            "",
            "",
            0,
            "",
            0,
            ctx.getSourceInterval(),
            ElementsTypes.NONE_ELEMENT,
            action_pointer,
        )
    )

    decl = self.module.declarations.getElementByIndex(decl_index)

    sv_structure.elements.addElement(decl)

    beh_index = sv_structure.getLastBehaviorIndex()
    if beh_index is not None:
        sv_structure.behavior[beh_index].addBody(
            (action_pointer, assign_name, ElementsTypes.ACTION_ELEMENT)
        )
    else:
        raise ValueError("sv_structure is empty")

    sensetive = self.extractSensetive(ctx.statement_or_null())

    increase_expr = "{0}={0}+1".format(identifier)
    action_pointer, assign_name, source_interval, uniq_action = self.expression2Aplan(
        increase_expr,
        ElementsTypes.REPEAT_ELEMENT,
        ctx.getSourceInterval(),
        sv_structure=sv_structure,
    )

    repeat_loop = "REPEAT_LOOP_{}".format(
        Counters_Object.getCounter(CounterTypes.REPEAT_COUNTER)
    )
    repeat_iteration = "REPEAT_ITERATION_{}".format(
        Counters_Object.getCounter(CounterTypes.REPEAT_COUNTER)
    )
    beh_index = sv_structure.getLastBehaviorIndex()
    if beh_index is not None:
        sv_structure.behavior[beh_index].addBody(
            (None, repeat_loop, ElementsTypes.ACTION_ELEMENT)
        )
    else:
        raise ValueError("sv_structure is empty")

    protocol_call = "Sensetive({0}, {1})".format(repeat_loop, sensetive)

    beh_index = sv_structure.addProtocol(repeat_iteration)
    sv_structure.behavior[beh_index].addBody(
        (
            action_pointer,
            "{0}.{1}".format(assign_name, protocol_call),
            ElementsTypes.ACTION_ELEMENT,
        )
    )

    condition_expr = "{0}.{1} < {2}".format(
        self.module.ident_uniq_name, decl.identifier, expression
    )
    action_pointer, assign_name, source_interval, uniq_action = self.expression2Aplan(
        condition_expr,
        ElementsTypes.CONDITION_ELEMENT,
        expression_source_interval,
        sv_structure=sv_structure,
    )

    beh_index = sv_structure.addProtocol(repeat_loop)
    sv_structure.behavior[beh_index].addBody(
        (
            action_pointer,
            "{0}.{1} + !{0}.{1}".format(assign_name, repeat_iteration),
            ElementsTypes.PROTOCOL_ELEMENT,
        )
    )

    Counters_Object.incrieseCounter(CounterTypes.REPEAT_COUNTER)
