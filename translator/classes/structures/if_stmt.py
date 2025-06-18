import typing
from antlr4_verilog.systemverilog import SystemVerilogParser

from AppModule.app.classes.actions import Action
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.if_stmt import IfStmt
from AppModule.app.classes.node import Node
from AppModule.app.classes.protocols import BodyElement, BodyElementArray
from translator.classes.base_translator import BaseTranslator


class IfSequenceBlockTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def generateElseBodyProtocol(self):
        protocol_params = self.getProtocolParams()
        self.last_struct.addProtocol(
            "ELSE_BODY_{0}_{1}".format(self.last_struct.number, self.last_struct.step),
            element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
            parametrs=protocol_params,
            inside_the_task=self.inside_the_task,
        )

    def isLastStep(self, else_count, if_count, last_step, crnt_step):
        if else_count > 1 and crnt_step > if_count and crnt_step == last_step:
            return True

    def translate(self, ctx: SystemVerilogParser.Seq_blockContext) -> None:
        self.findStruct()
        if isinstance(self.last_struct, IfStmt):
            if self.last_struct.if_count > 1 and (
                self.last_struct.step == self.last_struct.if_count
            ):
                self.generateElseBodyProtocol()
            elif self.isLastStep(
                self.last_struct.else_count,
                self.last_struct.if_count,
                self.last_struct.last_step,
                self.last_struct.step,
            ):
                self.generateElseBodyProtocol()
                self.last_struct.step += 1


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
        self.findStruct()
        if not isinstance(self.last_struct, IfStmt):
            return
        if_cnt = len(ctx.IF())
        else_cnt = len(ctx.ELSE())
        self.last_struct.setCondCount(if_cnt, else_cnt)


class IfCondPredicateTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Cond_predicateContext) -> None:
        self.findStruct()
        if not isinstance(self.last_struct, IfStmt):
            self.logger.warning(
                "if_stmt is not IfStmt ({type(self.last_struct)}) in conditionalPredecate2AplanImpl."
            )
            return

        beh_index = self.last_struct.getLastBehaviorIndex()
        if beh_index is None:
            self.logger.warning("beh_index is None in conditionalPredecate2AplanImpl.")
            return

        protocol_params = self.getProtocolParams()

        action_name = "if_{0}_{1}".format(
            self.last_struct.number, self.last_struct.step
        )
        if_action = Action(
            action_name,
            ctx.getSourceInterval(),
            element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
        )
        if self.last_struct.parametrs:
            if_action.parametrs = protocol_params

        self.last_node_array = if_action.precondition

        if_action.description_start.append(
            f"{self.module.identifier}#{self.module.ident_uniq_name}"
        )
        if_action.description_action_name = "if"
        if_action.description_end.append(
            f"{self.str_formater.valuesToAplanStandart(ctx.getText())}"
        )

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
            action_name = if_check_result

        if (
            self.last_struct.step != 1
            and self.last_struct.step != self.last_struct.if_count
        ):
            beh_index = self.last_struct.addProtocol(
                "ELSE_BODY_{0}_{1}".format(
                    self.last_struct.number, self.last_struct.step
                ),
                element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
                parametrs=protocol_params,
                inside_the_task=self.inside_the_task,
            )

        left_cond = BodyElementArray()

        left_cond.addElement(
            BodyElement(
                if_action.identifier,
                action_pointer,
                ElementsTypes.ACTION_ELEMENT,
                parametrs=protocol_params,
            )
        )

        body = "IF_BODY_{0}_{1}".format(
            self.last_struct.number,
            self.last_struct.step,
        )
        left_cond.addElement(
            BodyElement(
                body,
                action_pointer,
                ElementsTypes.PROTOCOL_ELEMENT,
                parametrs=protocol_params,
            )
        )

        self.last_struct.behavior[beh_index].addBodyElement(
            BodyElement(
                "",
                left_cond,
                ElementsTypes.IF_CONDITION_LEFT,
            )
        )
        continuation_flag = False
        else_protocol_flag = False
        if self.last_struct.step != self.last_struct.if_count:
            continuation_flag = True
        elif (
            self.last_struct.last_step > 0
            and self.last_struct.step == self.last_struct.else_count
        ):
            continuation_flag = True

        if continuation_flag == True:
            right_cond = BodyElementArray()
            right_cond.addElement(
                BodyElement(
                    f"!{if_action.identifier}",
                    action_pointer,
                    ElementsTypes.ACTION_ELEMENT,
                    parametrs=protocol_params,
                )
            )
            body = "ELSE_BODY_{0}_{1}".format(
                self.last_struct.number,
                self.last_struct.step + 1,
            )
            right_cond.addElement(
                BodyElement(
                    body,
                    action_pointer,
                    ElementsTypes.PROTOCOL_ELEMENT,
                    parametrs=protocol_params,
                )
            )
            self.last_struct.behavior[beh_index].addBodyElement(
                BodyElement(
                    "",
                    right_cond,
                    ElementsTypes.IF_CONDITION_RIGTH,
                )
            )
        else:
            self.last_struct.behavior[beh_index].addBodyElement(
                BodyElement(
                    f"!{if_action.identifier}",
                    action_pointer,
                    ElementsTypes.IF_CONDITION_RIGTH,
                    parametrs=protocol_params,
                )
            )

        self.last_struct.addProtocol(
            "IF_BODY_{0}_{1}".format(self.last_struct.number, self.last_struct.step),
            element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
            parametrs=protocol_params,
            inside_the_task=self.inside_the_task,
        )

        self.last_struct.step += 1

    def exit(self, ctx: SystemVerilogParser.Cond_predicateContext) -> None:
        self.last_node_array = None
