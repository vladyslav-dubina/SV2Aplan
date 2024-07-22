from typing import List
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import addEqueToBGET
from utils.utils import Counters_Object


def caseStatement2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Case_statementContext,
    sv_structure: Structure,
    names_for_change: List[str],
):
    case_expression = ctx.case_expression().getText()
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
                    case_expression, case_item_expression.getText()
                )
                action_name = "case_{0}".format(
                    Counters_Object.getCounter(CounterTypes.CASE_COUNTER)
                )
                case_action = Action(
                    "case",
                    Counters_Object.getCounter(CounterTypes.CASE_COUNTER),
                    case_item_expression.getSourceInterval(),
                )

                condition_txt = self.module.name_change.changeNamesInStr(condition_txt)
                (
                    condition_string,
                    condition_with_replaced_names,
                ) = self.prepareExpressionString(
                    condition_txt,
                    ElementsTypes.CASE_ELEMENT,
                )

                predicate_with_replaced_names = addEqueToBGET(
                    condition_with_replaced_names
                )
                case_action.precondition.body.append(predicate_with_replaced_names)
                case_action.description.body.append(
                    f"{self.module.identifier}#{self.module.ident_uniq_name}:action 'case ({condition_string})'"
                )
                case_action.postcondition.body.append("1")

                (
                    case_check_result,
                    source_interval,
                ) = self.module.actions.isUniqAction(case_action)
                if case_check_result is None:
                    self.module.actions.addElement(case_action)
                else:
                    action_name = case_check_result

            protocol_params = ""
            if self.inside_the_task == True:
                task = self.module.tasks.getLastTask()
                if task is not None:
                    protocol_params = "({0})".format(task.parametrs)

            if index == 0:
                Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                beh_index = sv_structure.getLastBehaviorIndex()
                if beh_index is not None:
                    sv_structure.behavior[beh_index].addBody(
                        (
                            "B_{0}{1}".format(
                                Counters_Object.getCounter(CounterTypes.B_COUNTER),
                                protocol_params,
                            ),
                            ElementsTypes.PROTOCOL_ELEMENT,
                        )
                    )
                sv_structure.addProtocol(
                    "B_{0}{1}".format(
                        Counters_Object.getCounter(CounterTypes.B_COUNTER),
                        protocol_params,
                    )
                )
            else:
                sv_structure.addProtocol(
                    "ELSE_BODY_{0}{1}".format(
                        Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER),
                        protocol_params,
                    )
                )
                Counters_Object.incrieseCounter(CounterTypes.ELSE_BODY_COUNTER)

            beh_index = sv_structure.getLastBehaviorIndex()
            if beh_index is not None:
                if case_item.DEFAULT():
                    body = "CASE_BODY_{0}{1}".format(
                        Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                        protocol_params,
                    )
                elif index == len(case_item_list) - 1:
                    body = "{0}.CASE_BODY_{1}{2} + !{0}".format(
                        action_name,
                        Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                        protocol_params,
                    )
                else:
                    body = "{0}.CASE_BODY_{1}{3} + !{0}.ELSE_BODY_{2}{3}".format(
                        action_name,
                        Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                        Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER),
                        protocol_params,
                    )

                sv_structure.behavior[beh_index].addBody(
                    (body, ElementsTypes.ACTION_ELEMENT)
                )

            sv_structure.addProtocol(
                "CASE_BODY_{0}{1}".format(
                    Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                    protocol_params,
                )
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
