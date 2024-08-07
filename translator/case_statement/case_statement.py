from typing import List
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.node import Node
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import addEqueToBGET, valuesToAplanStandart
from utils.utils import Counters_Object


def caseStatement2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Case_statementContext,
    sv_structure: Structure,
    names_for_change: List[str],
):
    case_expression = ctx.case_expression()
    case_item_list = ctx.case_item()
    for index, case_item in enumerate(case_item_list):
        statement = case_item.statement_or_null().statement()
        case_item_expressions = []
        for case_item_expression in case_item.case_item_expression():
            case_item_expressions.append(case_item_expression)

        if case_item.DEFAULT():
            case_item_expressions.append(None)

        for case_item_expression in case_item_expressions:
            if case_item_expression is not None:
                condition_txt = "({0}) == ({1})".format(
                    case_expression.getText(), case_item_expression.getText()
                )
                action_name = "case_{0}".format(
                    Counters_Object.getCounter(CounterTypes.CASE_COUNTER)
                )
                case_action = Action(
                    "case_{0}".format(
                        Counters_Object.getCounter(CounterTypes.CASE_COUNTER),
                    ),
                    case_item_expression.getSourceInterval(),
                )

                case_action.precondition.addElement(
                    Node("(", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
                )
                self.body2Aplan(
                    case_expression, destination_node_array=case_action.precondition
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
                    case_item_expression,
                    destination_node_array=case_action.precondition,
                )
                case_action.precondition.addElement(
                    Node(")", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
                )

                condition_txt = valuesToAplanStandart(condition_txt)

                case_action.description = f"{self.module.identifier}#{self.module.ident_uniq_name}:action 'case ({condition_txt})'"

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

            protocol_params = None
            if self.inside_the_task == True:
                task = self.module.tasks.getLastTask()
                if task is not None:
                    protocol_params = task.parametrs

            if index == 0:
                Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                beh_index = sv_structure.getLastBehaviorIndex()
                if beh_index is not None:
                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(
                            identifier="B_{0}".format(
                                Counters_Object.getCounter(CounterTypes.B_COUNTER),
                            ),
                            element_type=ElementsTypes.PROTOCOL_ELEMENT,
                            parametrs=protocol_params,
                        )
                    )
                sv_structure.addProtocol(
                    "B_{0}".format(
                        Counters_Object.getCounter(CounterTypes.B_COUNTER),
                    ),
                    parametrs=protocol_params,
                )
            else:
                sv_structure.addProtocol(
                    "ELSE_BODY_{0}".format(
                        Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER),
                    ),
                    parametrs=protocol_params,
                )
                Counters_Object.incrieseCounter(CounterTypes.ELSE_BODY_COUNTER)

            beh_index = sv_structure.getLastBehaviorIndex()
            if beh_index is not None:
                if case_item.DEFAULT():
                    body = "CASE_BODY_{0}".format(
                        Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                    )

                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(
                            body,
                            action_pointer,
                            ElementsTypes.ACTION_ELEMENT,
                            parametrs=protocol_params,
                        )
                    )

                elif index == len(case_item_list) - 1:
                    body = "{0}.CASE_BODY_{1}".format(
                        action_name,
                        Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                    )

                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(
                            body,
                            action_pointer,
                            ElementsTypes.IF_CONDITION_LEFT,
                            parametrs=protocol_params,
                        )
                    )

                    body = "!{0}".format(
                        action_name,
                    )

                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(
                            body,
                            action_pointer,
                            ElementsTypes.IF_CONDITION_RIGTH,
                            parametrs=protocol_params,
                        )
                    )

                else:
                    body = "{0}.CASE_BODY_{1}".format(
                        action_name,
                        Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                    )

                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(
                            body,
                            action_pointer,
                            ElementsTypes.IF_CONDITION_LEFT,
                            parametrs=protocol_params,
                        )
                    )

                    body = "!{0}.ELSE_BODY_{1}".format(
                        action_name,
                        Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER),
                    )

                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(
                            body,
                            action_pointer,
                            ElementsTypes.IF_CONDITION_RIGTH,
                            parametrs=protocol_params,
                        )
                    )

            sv_structure.addProtocol(
                "CASE_BODY_{0}".format(
                    Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                ),
                parametrs=protocol_params,
            )

            Counters_Object.incrieseCounter(CounterTypes.BODY_COUNTER)
            if index == 0:
                names_for_change += self.body2Aplan(
                    statement,
                    sv_structure,
                    ElementsTypes.CASE_ELEMENT,
                )
            else:
                names_for_change += self.body2Aplan(
                    statement,
                    sv_structure,
                    ElementsTypes.ELSE_BODY_ELEMENT,
                )
            for element in names_for_change:
                self.module.name_change.deleteElement(element)
            Counters_Object.incrieseCounter(CounterTypes.CASE_COUNTER)
