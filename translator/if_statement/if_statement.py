from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.if_stmt import IfStmt
from classes.node import Node
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.translator import Translator
from utils.string_formating import valuesToAplanStandart
from utils.utils import Color, Counters_Object, printWithColor


def ifSeqBlock2AplanImpl(self: Translator, ctx: SystemVerilogParser.Seq_blockContext):
    sv_structure: Structure | None = self.structure_pointer_list.getLastElement()
    if isinstance(sv_structure, IfStmt):
        if (
            sv_structure.cond_predicate_count == 1
            and sv_structure.init_predicate_count > 1
        ):
            protocol_params = self.getProtocolParams()
            sv_structure.addProtocol(
                "ELSE_BODY_{0}".format(
                    Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER)
                ),
                element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
                parametrs=protocol_params,
                inside_the_task=(self.inside_the_task or self.inside_the_function),
            )
            Counters_Object.incrieseCounter(CounterTypes.ELSE_BODY_COUNTER)
            sv_structure.cond_predicate_count -= 1
            return True

    return False


def conditionalPredecate2AplanImpl(
    self: Translator,
    ctx: SystemVerilogParser.Cond_predicateContext,
):
    if_stmt: Structure | None = self.structure_pointer_list.getLastElement()
    if not isinstance(if_stmt, IfStmt):
        printWithColor(
            f"WARNING: if_stmt is not IfStmt ({type(if_stmt)}) in conditionalPredecate2AplanImpl.",
            Color.YELLOW,
        )
        return

    beh_index = if_stmt.getLastBehaviorIndex()
    if beh_index is None:
        printWithColor(
            f"WARNING: beh_index is None in conditionalPredecate2AplanImpl.",
            Color.YELLOW,
        )
        return

    Counters_Object.incrieseCounter(CounterTypes.IF_COUNTER)
    action_name = "if_{0}".format(Counters_Object.getCounter(CounterTypes.IF_COUNTER))
    if_action = Action(
        action_name,
        ctx.getSourceInterval(),
        element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
    )
    self.body2Aplan(ctx, destination_node_array=if_action.precondition)

    if_action.description_start.append(
        f"{self.module.identifier}#{self.module.ident_uniq_name}"
    )
    if_action.description_action_name = "if"
    if_action.description_end.append(f"{valuesToAplanStandart(ctx.getText())}")

    if_action.postcondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))

    (
        action_pointer,
        if_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(if_action)
    if if_check_result is None:
        self.module.actions.addElement(if_action)
    else:
        Counters_Object.decrieseCounter(CounterTypes.IF_COUNTER)
        action_name = if_check_result

    protocol_params = self.getProtocolParams()

    body = "{0}.IF_BODY_{1}".format(
        action_name,
        Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
    )

    if if_stmt.cond_predicate_count != if_stmt.init_predicate_count:
        beh_index = if_stmt.addProtocol(
            "ELSE_BODY_{0}".format(
                Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER)
            ),
            element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
            parametrs=protocol_params,
            inside_the_task=(self.inside_the_task or self.inside_the_function),
        )
        Counters_Object.incrieseCounter(CounterTypes.ELSE_BODY_COUNTER)

    if_stmt.behavior[beh_index].addBody(
        BodyElement(
            body,
            action_pointer,
            ElementsTypes.IF_CONDITION_LEFT,
            parametrs=protocol_params,
        )
    )

    continuation_flag = False
    if if_stmt.cond_predicate_count - 2 >= 0:
        continuation_flag = True

    if continuation_flag == True:
        body = "!{0}.ELSE_BODY_{1}".format(
            action_name,
            Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER),
        )
        if_stmt.behavior[beh_index].addBody(
            BodyElement(
                body,
                action_pointer,
                ElementsTypes.IF_CONDITION_RIGTH,
                parametrs=protocol_params,
            )
        )
    else:
        if_stmt.behavior[beh_index].addBody(
            BodyElement(
                f"!{action_name}",
                action_pointer,
                ElementsTypes.IF_CONDITION_RIGTH,
                parametrs=protocol_params,
            )
        )

    if_stmt.addProtocol(
        "IF_BODY_{0}".format(Counters_Object.getCounter(CounterTypes.BODY_COUNTER)),
        element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
        parametrs=protocol_params,
        inside_the_task=(self.inside_the_task or self.inside_the_function),
    )
    Counters_Object.incrieseCounter(CounterTypes.BODY_COUNTER)
    Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)

    if_stmt.cond_predicate_count -= 1


def ifStatement2AplanImpl(
    self: Translator,
    ctx: SystemVerilogParser.Conditional_statementContext,
):

    self.createStatementToSvStruct("IF_STATEMENT", ElementsTypes.IF_STATEMENT_ELEMENT)
    if_stmt: Structure | None = self.structure_pointer_list.getLastElement()
    if not isinstance(if_stmt, IfStmt):
        return

    statements = ctx.statement_or_null()
    if_stmt.setCondPredicateCount(len(statements))
