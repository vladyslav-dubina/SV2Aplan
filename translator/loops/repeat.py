from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
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
            assign_name,
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

    sensetive = self.extractSensetive(ctx.statement_or_null())

    sensetive = sensetive + " && ({0}.{1} < {2})".format(
        self.module.ident_uniq_name, decl.identifier, expression
    )

    increase_expr = "{0}={0}+1".format(identifier)
    action_pointer, assign_name, source_interval, uniq_action = self.expression2Aplan(
        increase_expr,
        ElementsTypes.REPEAT_ELEMENT,
        ctx.getSourceInterval(),
        sv_structure=sv_structure,
    )

    protocol_call = "Sensetive({0}, {1})".format(assign_name, sensetive)
    beh_index = sv_structure.getLastBehaviorIndex()
    if beh_index is not None:
        sv_structure.behavior[beh_index].addBody(
            (action_pointer, protocol_call, ElementsTypes.ACTION_ELEMENT)
        )
    else:
        Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
        b_index = sv_structure.addProtocol(
            "B_{}".format(Counters_Object.getCounter(CounterTypes.B_COUNTER))
        )
        sv_structure.behavior[b_index].addBody(
            (action_pointer, protocol_call, ElementsTypes.ACTION_ELEMENT)
        )
