from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.loop_stmt import LoopStmt
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.expression.expression import actionFromNodeStr
from translator.translator import Module_Translator
from utils.string_formating import replaceValueParametrsCalls
from utils.utils import Counters_Object


def repeat2AplanImpl(
    self: Module_Translator,
    ctx: SystemVerilogParser.Loop_statementContext,
):
    stmt: Structure | None = self.structure_pointer_list.getLastElement()
    if not isinstance(stmt, Structure):
        return
    identifier = "repeat_var_{0}".format(
        Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER)
    )
    expression = ctx.expression().getText()
    expression_source_interval = ctx.expression().getSourceInterval()
    expression = replaceValueParametrsCalls(self.module.value_parametrs, expression)

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
            source_interval=ctx.getSourceInterval(),
            element_type=ElementsTypes.NONE_ELEMENT,
            name_space_level=self.getLastNameSpaceLevel(),
        )
    )

    action_pointer, assign_name, source_interval, uniq_action = actionFromNodeStr(
        self,
        assing_expr,
        ctx.getSourceInterval(),
        ElementsTypes.ASSIGN_ELEMENT,
        sv_structure=stmt,
    )

    decl = self.module.declarations.getElementByIndex(decl_index)

    decl.action = action_pointer

    stmt.elements.addElement(decl)

    beh_index = stmt.getLastBehaviorIndex()
    if beh_index is not None:
        stmt.behavior[beh_index].addBody(
            BodyElement(assign_name, action_pointer, ElementsTypes.ACTION_ELEMENT)
        )
    else:
        raise ValueError("sv_structure is empty")

    self.createStatementToSvStruct("REPEAT_LOOP", ElementsTypes.LOOP_ELEMENT)
    repeat_stmt: Structure | None = self.structure_pointer_list.getLastElement()
    if not isinstance(repeat_stmt, LoopStmt):
        return

    repeat_iteration = "REPEAT_ITERATION_{}".format(
        Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER)
    )

    condition_expr = "{0} < {1}".format(decl.identifier, expression)
    action_pointer, assign_name, source_interval, uniq_action = actionFromNodeStr(
        self,
        condition_expr,
        expression_source_interval,
        ElementsTypes.CONDITION_ELEMENT,
        sv_structure=repeat_stmt,
    )

    beh_index = repeat_stmt.getLastBehaviorIndex()
    repeat_stmt.behavior[beh_index].addBody(
        BodyElement(
            "{0}.{1} + !{0}".format(assign_name, repeat_iteration),
            action_pointer,
            ElementsTypes.ACTION_ELEMENT,
        )
    )

    repeat_iteration = "REPEAT_ITERATION_{}".format(
        Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER)
    )

    increase_expr = "{0} = {0} + 1".format(identifier)
    action_pointer, assign_name, source_interval, uniq_action = actionFromNodeStr(
        self,
        increase_expr,
        ctx.getSourceInterval(),
        ElementsTypes.REPEAT_ELEMENT,
        sv_structure=repeat_stmt,
    )

    sensetive = self.extractSensetive(ctx.statement_or_null())
    protocol_call = "Sensetive({0}, {1})".format(repeat_stmt.getName(), sensetive)

    beh_index = repeat_stmt.addProtocol(
        repeat_iteration,
        inside_the_task=(self.inside_the_task or self.inside_the_function),
    )

    repeat_stmt.behavior[beh_index].addBody(
        BodyElement(
            "{0}.{1}".format(assign_name, protocol_call),
            action_pointer,
            ElementsTypes.ACTION_ELEMENT,
        )
    )
    
    copy = repeat_stmt.behavior[beh_index].copy()
    repeat_stmt.behavior[beh_index] = repeat_stmt.behavior[beh_index-1].copy()
    repeat_stmt.behavior[beh_index-1]= copy
   
    self.body2Aplan(ctx.statement_or_null(), repeat_stmt)
