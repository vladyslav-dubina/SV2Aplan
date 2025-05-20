from antlr4_verilog.systemverilog import SystemVerilogParser

from classes.actions import Action
from classes.case_stmt import CaseStmt
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.node import Node
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import valuesToAplanStandart
from utils.utils import Color, Counters_Object, printWithColor


class CaseItemExprTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Case_item_expressionContext) -> None:
        case_stmt: Structure | None = self.structure_pointer_list.getLastElement()
        if not isinstance(case_stmt, CaseStmt):
            printWithColor(
                f"WARNING: case_stmt is not CaseStmt ({type(case_stmt)}) in caseItemExpr2AplanImpl.",
                Color.YELLOW,
            )
            return

        beh_index = case_stmt.getLastBehaviorIndex()
        if beh_index is None:
            printWithColor(
                f"WARNING: beh_index is None in caseItemExpr2AplanImpl.",
                Color.YELLOW,
            )
            return

        condition_txt = "({0}) == ({1})".format(
            case_stmt.expression.getText(), ctx.getText()
        )

        Counters_Object.incrieseCounter(CounterTypes.CASE_COUNTER)

        action_name = "case_{0}".format(
            Counters_Object.getCounter(CounterTypes.CASE_COUNTER)
        )
        case_action = Action(
            "case_{0}".format(
                Counters_Object.getCounter(CounterTypes.CASE_COUNTER),
            ),
            ctx.getSourceInterval(),
            element_type=ElementsTypes.CASE_ELEMENT,
        )

        case_action.precondition.addElement(
            Node("(", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        self.body2Aplan(
            case_stmt.expression, destination_node_array=case_action.precondition
        )
        case_action.precondition.addElement(
            Node(")", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        case_action.precondition.addElement(
            Node("==", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        case_action.precondition.addElement(
            Node("(", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        self.body2Aplan(
            ctx,
            destination_node_array=case_action.precondition,
        )
        case_action.precondition.addElement(
            Node(")", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )

        condition_txt = valuesToAplanStandart(condition_txt)

        case_action.description_start.append(
            f"{self.module.identifier}#{self.module.ident_uniq_name}"
        )
        case_action.description_action_name = "case"
        case_action.description_end.append(f"{condition_txt}")

        case_action.postcondition.addElement(
            Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT)
        )

        (
            action_pointer,
            case_check_result,
            source_interval,
        ) = self.module.actions.isUniqAction(case_action)
        if case_check_result is None:
            self.module.actions.addElement(case_action)
        else:
            action_name = case_check_result

        protocol_params = self.getProtocolParams()

        body = "{0}.CASE_BODY_{1}".format(
            action_name,
            Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
        )

        if case_stmt.case_count != case_stmt.init_case_count:
            beh_index = case_stmt.addProtocol(
                "ELSE_BODY_{0}".format(
                    Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER)
                ),
                element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
                parametrs=protocol_params,
                inside_the_task=(self.inside_the_task or self.inside_the_function),
            )
            Counters_Object.incrieseCounter(CounterTypes.ELSE_BODY_COUNTER)

        case_stmt.behavior[beh_index].addBody(
            BodyElement(
                body,
                action_pointer,
                ElementsTypes.IF_CONDITION_LEFT,
                parametrs=protocol_params,
            )
        )

        continuation_flag = False
        if case_stmt.case_count - 2 >= 0:
            continuation_flag = True

        if continuation_flag == True:
            body = "!{0}.ELSE_BODY_{1}".format(
                action_name,
                Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER),
            )
            case_stmt.behavior[beh_index].addBody(
                BodyElement(
                    body,
                    action_pointer,
                    ElementsTypes.IF_CONDITION_RIGTH,
                    parametrs=protocol_params,
                )
            )
        else:
            case_stmt.behavior[beh_index].addBody(
                BodyElement(
                    f"!{action_name}",
                    action_pointer,
                    ElementsTypes.IF_CONDITION_RIGTH,
                    parametrs=protocol_params,
                )
            )

        case_stmt.addProtocol(
            "CASE_BODY_{0}".format(
                Counters_Object.getCounter(CounterTypes.BODY_COUNTER)
            ),
            element_type=ElementsTypes.CASE_STATEMENT_ELEMENT,
            parametrs=protocol_params,
            inside_the_task=(self.inside_the_task or self.inside_the_function),
        )

        Counters_Object.incrieseCounter(CounterTypes.BODY_COUNTER)
        Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)

        case_stmt.case_count -= 1
        return


class CaseItemTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Case_itemContext) -> None:
        case_stmt: Structure | None = self.structure_pointer_list.getLastElement()
        if isinstance(case_stmt, CaseStmt):
            if case_stmt.case_count == 1 and case_stmt.init_case_count > 1:
                protocol_params = self.getProtocolParams()
                case_stmt.addProtocol(
                    "ELSE_BODY_{0}".format(
                        Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER)
                    ),
                    element_type=ElementsTypes.CASE_STATEMENT_ELEMENT,
                    parametrs=protocol_params,
                    inside_the_task=(self.inside_the_task or self.inside_the_function),
                )
                Counters_Object.incrieseCounter(CounterTypes.ELSE_BODY_COUNTER)
                case_stmt.case_count -= 1


class CaseStmtTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Case_statementContext) -> None:
        self.createStatement("CASE_STATEMENT", ElementsTypes.CASE_STATEMENT_ELEMENT)
        case_stmt: Structure | None = self.structure_pointer_list.getLastElement()
        if not isinstance(case_stmt, CaseStmt):
            return
        case_item_list = ctx.case_item()
        case_stmt.setCaseCount(len(case_item_list))
        case_stmt.expression = ctx.case_expression()
