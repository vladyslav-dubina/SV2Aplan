from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from translator.expression.expression import actionFromNodeStr
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

    assing_expr = "{0} = {1}".format(identifier, 0)

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
            None,
        )
    )

    action_pointer, assign_name, source_interval, uniq_action = actionFromNodeStr(
        self,
        assing_expr,
        ctx.getSourceInterval(),
        ElementsTypes.ASSIGN_ELEMENT,
        sv_structure=sv_structure,
    )

    decl = self.module.declarations.getElementByIndex(decl_index)

    decl.action = action_pointer

    sv_structure.elements.addElement(decl)

    beh_index = sv_structure.getLastBehaviorIndex()
    if beh_index is not None:
        sv_structure.behavior[beh_index].addBody(
            BodyElement(assign_name, action_pointer, ElementsTypes.ACTION_ELEMENT)
        )
    else:
        raise ValueError("sv_structure is empty")

    sensetive = self.extractSensetive(ctx.statement_or_null())

    increase_expr = "{0} = {0} + 1".format(identifier)
    action_pointer, assign_name, source_interval, uniq_action = actionFromNodeStr(
        self,
        increase_expr,
        ctx.getSourceInterval(),
        ElementsTypes.REPEAT_ELEMENT,
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
            BodyElement(
                identifier=repeat_loop, element_type=ElementsTypes.ACTION_ELEMENT
            )
        )
    else:
        raise ValueError("sv_structure is empty")

    protocol_call = "Sensetive({0}, {1})".format(repeat_loop, sensetive)

    beh_index = sv_structure.addProtocol(repeat_iteration)
    sv_structure.behavior[beh_index].addBody(
        BodyElement(
            "{0}.{1}".format(assign_name, protocol_call),
            action_pointer,
            ElementsTypes.ACTION_ELEMENT,
        )
    )

    condition_expr = "{0} < {1}".format(decl.identifier, expression)
    action_pointer, assign_name, source_interval, uniq_action = actionFromNodeStr(
        self,
        condition_expr,
        expression_source_interval,
        ElementsTypes.CONDITION_ELEMENT,
        sv_structure=sv_structure,
    )

    beh_index = sv_structure.addProtocol(repeat_loop)
    sv_structure.behavior[beh_index].addBody(
        BodyElement(
            "{0}.{1} + !{0}".format(assign_name, repeat_iteration),
            action_pointer,
            ElementsTypes.ACTION_ELEMENT,
        )
    )

    Counters_Object.incrieseCounter(CounterTypes.REPEAT_COUNTER)
