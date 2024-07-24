from typing import List
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import addEqueToBGET
from utils.utils import Counters_Object


def ifStatement2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Conditional_statementContext,
    sv_structure: Structure,
    names_for_change: List[str],
):
    predicate = ctx.cond_predicate()
    statements = ctx.statement_or_null()

    predicate_statements_list = []
    for i in range(len(statements)):
        if i <= len(predicate) - 1:
            predicate_statements_list.append(
                {"predicate": predicate[i], "statement": statements[i]}
            )
        else:
            predicate_statements_list.append(
                {"predicate": None, "statement": statements[i]}
            )

    for index, element in enumerate(predicate_statements_list):
        action_name = "if_{0}".format(
            Counters_Object.getCounter(CounterTypes.IF_COUNTER)
        )
        if element["predicate"] is not None:
            Counters_Object.incrieseCounter(CounterTypes.IF_COUNTER)
            action_name = "if_{0}".format(
                Counters_Object.getCounter(CounterTypes.IF_COUNTER)
            )
            if_action = Action(
                "if_{0}".format(
                    Counters_Object.getCounter(CounterTypes.IF_COUNTER),
                ),
                ctx.getSourceInterval(),
            )
            predicate_txt = element["predicate"].getText()
            predicate_txt = self.module.name_change.changeNamesInStr(predicate_txt)
            (
                predicate_string,
                predicate_with_replaced_names,
            ) = self.prepareExpressionString(
                predicate_txt,
                ElementsTypes.IF_STATEMENT_ELEMENT,
            )
            predicate_with_replaced_names = addEqueToBGET(predicate_with_replaced_names)
            if_action.precondition.body.append(predicate_with_replaced_names)
            if_action.description.body.append(
                f"{self.module.identifier}#{self.module.ident_uniq_name}:action 'if ({predicate_string})'"
            )
            if_action.postcondition.body.append("1")

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

        protocol_params = ""
        if self.inside_the_task == True:
            task = self.module.tasks.getLastTask()
            if task is not None:
                protocol_params = "({0})".format(task.parametrs)

        local_if_counter = Counters_Object.getCounter(CounterTypes.IF_COUNTER)
        if element["predicate"] is None:
            local_if_counter -= 1
        if index == 0:
            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
            beh_index = sv_structure.getLastBehaviorIndex()
            if beh_index is not None:
                sv_structure.behavior[beh_index].addBody(
                    (
                        None,
                        "B_{0}".format(
                            Counters_Object.getCounter(CounterTypes.B_COUNTER)
                        ),
                        ElementsTypes.PROTOCOL_ELEMENT,
                    )
                )
            sv_structure.addProtocol(
                "B_{0}{1}".format(
                    Counters_Object.getCounter(CounterTypes.B_COUNTER), protocol_params
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
            if element["predicate"] is None:
                body = "IF_BODY_{0}{1}".format(
                    Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                    protocol_params,
                )
            elif index == len(predicate_statements_list) - 1:
                body = "{0}.IF_BODY_{1}{2} + !{0}".format(
                    action_name,
                    Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                    protocol_params,
                )
            else:
                body = "{0}.IF_BODY_{1}{3} + !{0}.ELSE_BODY_{2}{3}".format(
                    action_name,
                    Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                    Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER),
                    protocol_params,
                )

            sv_structure.behavior[beh_index].addBody(
                (action_pointer, body, ElementsTypes.ACTION_ELEMENT)
            )

        sv_structure.addProtocol(
            "IF_BODY_{0}{1}".format(
                Counters_Object.getCounter(CounterTypes.BODY_COUNTER), protocol_params
            )
        )
        Counters_Object.incrieseCounter(CounterTypes.BODY_COUNTER)
        if index == 0:
            names_for_change += self.body2Aplan(
                element["statement"],
                sv_structure,
                ElementsTypes.IF_STATEMENT_ELEMENT,
            )
        else:
            names_for_change += self.body2Aplan(
                element["statement"],
                sv_structure,
                ElementsTypes.ELSE_BODY_ELEMENT,
            )
        for element in names_for_change:
            self.module.name_change.deleteElement(element)
