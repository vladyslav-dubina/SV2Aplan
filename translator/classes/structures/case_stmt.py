import typing
from antlr4_verilog.systemverilog import SystemVerilogParser

from AppModule.app.classes.actions import Action
from AppModule.app.classes.case_stmt import CaseStmt
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.node import Node
from AppModule.app.classes.protocols import BodyElement
from translator.classes.base_translator import BaseTranslator


class CaseItemExprTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Case_item_expressionContext) -> None:
        self.findStruct()
        if not isinstance(self.last_struct, CaseStmt):
            self.logger.warning(
                "case_stmt is not CaseStmt ({type(self.last_struct)}) in caseItemExpr2AplanImpl."
            )
            return
        protocol_params = self.getProtocolParams()
        beh_index = self.last_struct.getLastBehaviorIndex()
        if beh_index is None:
            self.logger.warning(" beh_index is None in caseItemExpr2AplanImpl.")
            return

        condition_txt = "({0}) == ({1})".format(
            self.last_struct.expression.getText(), ctx.getText()
        )

        action_name = "case_{0}_{1}".format(
            self.last_struct.number,
            self.last_struct.init_case_count - self.last_struct.case_count,
        )

        case_action = Action(
            action_name,
            ctx.getSourceInterval(),
            element_type=ElementsTypes.CASE_ELEMENT,
        )

        if self.last_struct.parametrs:
            case_action.parametrs = protocol_params

        case_action.precondition.addElement(
            Node("(", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )
        self._translator_ptr.body2Aplan(
            self.last_struct.expression, destination_node_array=case_action.precondition
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
        self._translator_ptr.body2Aplan(
            ctx,
            destination_node_array=case_action.precondition,
        )
        case_action.precondition.addElement(
            Node(")", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
        )

        condition_txt = self.str_formater.valuesToAplanStandart(condition_txt)

        case_action.description_start.append(
            f"{self.design_unit.identifier}#{self.design_unit.ident_uniq_name}"
        )
        case_action.description_action_name = "case"
        case_action.description_end.append(f"{condition_txt}")

        case_action.postcondition.addElement(
            Node("1", (0, 0), ElementsTypes.NUMBER_ELEMENT)
        )

        (
            action_pointer,
            case_check_result,
            source_interval,
        ) = self.design_unit.actions.isUniqAction(case_action)
        if case_check_result is None:
            self.design_unit.actions.addElement(case_action)
        else:
            action_name = case_check_result

        protocol_params = self.getProtocolParams()

        body = "{0}.CASE_BODY_{1}_{2}".format(
            action_name,
            self.last_struct.number,
            self.last_struct.init_case_count - self.last_struct.case_count,
        )

        if self.last_struct.case_count != self.last_struct.init_case_count:
            beh_index = self.last_struct.addProtocol(
                "ELSE_BODY_{0}_{1}".format(
                    self.last_struct.number,
                    self.last_struct.init_case_count - self.last_struct.case_count,
                ),
                element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
                parametrs=protocol_params,
                inside_the_task=self.inside_the_task,
            )

        self.last_struct.behavior[beh_index].addBodyElement(
            BodyElement(
                body,
                action_pointer,
                ElementsTypes.IF_CONDITION_LEFT,
                parametrs=protocol_params,
            )
        )

        continuation_flag = False
        if self.last_struct.case_count - 2 >= 0:
            continuation_flag = True

        if continuation_flag == True:
            body = "!{0}.ELSE_BODY_{1}_{2}".format(
                action_name,
                self.last_struct.number,
                self.last_struct.init_case_count - self.last_struct.case_count + 1,
            )
            self.last_struct.behavior[beh_index].addBodyElement(
                BodyElement(
                    body,
                    action_pointer,
                    ElementsTypes.IF_CONDITION_RIGTH,
                    parametrs=protocol_params,
                )
            )
        else:
            self.last_struct.behavior[beh_index].addBodyElement(
                BodyElement(
                    f"!{action_name}",
                    action_pointer,
                    ElementsTypes.IF_CONDITION_RIGTH,
                    parametrs=protocol_params,
                )
            )

        self.last_struct.addProtocol(
            "CASE_BODY_{0}_{1}".format(
                self.last_struct.number,
                self.last_struct.init_case_count - self.last_struct.case_count,
            ),
            element_type=ElementsTypes.CASE_STATEMENT_ELEMENT,
            parametrs=protocol_params,
            inside_the_task=self.inside_the_task,
        )

        self.last_struct.case_count -= 1
        return


class CaseItemTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Case_itemContext) -> None:
        self.findStruct()
        if isinstance(self.last_struct, CaseStmt):
            if (
                self.last_struct.case_count == 1
                and self.last_struct.init_case_count > 1
            ):
                protocol_params = self.getProtocolParams()
                self.last_struct.addProtocol(
                    "ELSE_BODY_{0}_{1}".format(
                        self.last_struct.number,
                        self.last_struct.init_case_count - self.last_struct.case_count,
                    ),
                    element_type=ElementsTypes.CASE_STATEMENT_ELEMENT,
                    parametrs=protocol_params,
                    inside_the_task=self.inside_the_task,
                )

                self.last_struct.case_count -= 1


class CaseStmtTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Case_statementContext) -> None:
        self.createStatement("CASE_STATEMENT", ElementsTypes.CASE_STATEMENT_ELEMENT)
        self.findStruct()
        if not isinstance(self.last_struct, CaseStmt):
            return
        case_item_list = ctx.case_item()
        self.last_struct.setCaseCount(len(case_item_list))
        self.last_struct.expression = ctx.case_expression()
