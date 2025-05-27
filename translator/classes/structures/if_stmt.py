import typing
from antlr4_verilog.systemverilog import SystemVerilogParser

from classes.actions import Action
from classes.always import Always
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.if_stmt import IfStmt
from classes.node import Node
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import valuesToAplanStandart
from utils.utils import Color, Counters_Object, printWithColor


class IfSequenceBlockTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Seq_blockContext) -> None:
        if_stmt: Structure | None = self.structure_pointer_list.getLastElement()

        if isinstance(if_stmt, IfStmt):
            if if_stmt.if_count > 1 and if_stmt.step == if_stmt.if_count:
                protocol_params = self.getProtocolParams()

                if_stmt.addProtocol(
                    "ELSE_BODY_{0}_{1}".format(if_stmt.number, if_stmt.step),
                    element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
                    parametrs=protocol_params,
                    inside_the_task=(self.inside_the_task or self.inside_the_function),
                )

                return


class IfStmtTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Conditional_statementContext) -> None:
        self.createStatement(
            "IF_STATEMENT",
            ElementsTypes.IF_STATEMENT_ELEMENT,
        )
        if_stmt: Structure | None = self.structure_pointer_list.getLastElement()
        if not isinstance(if_stmt, IfStmt):
            return

        if_stmt.setCondCount(len(ctx.IF()), len(ctx.ELSE()))


class IfCondPredicateTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Cond_predicateContext) -> None:
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

        action_name = "if_{0}_{1}".format(
            if_stmt.number,
            if_stmt.step,
        )
        if_action = Action(
            action_name,
            ctx.getSourceInterval(),
            element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
        )
        self._translator_ptr.body2Aplan(
            ctx, destination_node_array=if_action.precondition
        )

        if_action.description_start.append(
            f"{self.module.identifier}#{self.module.ident_uniq_name}"
        )
        if_action.description_action_name = "if"
        if_action.description_end.append(f"{valuesToAplanStandart(ctx.getText())}")

        if_action.postcondition.addElement(
            Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT)
        )

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

        body = "{0}.IF_BODY_{1}_{2}".format(
            action_name,
            if_stmt.number,
            if_stmt.step,
        )

        if if_stmt.step != 1 and if_stmt.step != if_stmt.if_count:
            beh_index = if_stmt.addProtocol(
                "ELSE_BODY_{0}_{1}".format(if_stmt.number, if_stmt.step),
                element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
                parametrs=protocol_params,
                inside_the_task=(self.inside_the_task or self.inside_the_function),
            )

        if_stmt.behavior[beh_index].addBody(
            BodyElement(
                body,
                action_pointer,
                ElementsTypes.IF_CONDITION_LEFT,
                parametrs=protocol_params,
            )
        )

        continuation_flag = False
        if if_stmt.step != if_stmt.if_count:
            continuation_flag = True

        if continuation_flag == True:
            body = "!{0}.ELSE_BODY_{1}_{2}".format(
                action_name,
                if_stmt.number,
                if_stmt.step + 1,
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
            "IF_BODY_{0}_{1}".format(if_stmt.number, if_stmt.step),
            element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
            parametrs=protocol_params,
            inside_the_task=(self.inside_the_task or self.inside_the_function),
        )

        if_stmt.step += 1
