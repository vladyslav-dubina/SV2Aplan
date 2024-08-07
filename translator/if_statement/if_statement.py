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
            predicate_ctx = element["predicate"]

            condition_txt = valuesToAplanStandart(predicate_ctx.getText())

            self.body2Aplan(
                predicate_ctx, destination_node_array=if_action.precondition
            )
            if_action.description = f"{self.module.identifier}#{self.module.ident_uniq_name}:action 'if ({condition_txt})'"

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

        protocol_params = None
        if self.inside_the_task == True:
            task = self.module.tasks.getLastTask()
            if task is not None:
                protocol_params = task.parametrs

        local_if_counter = Counters_Object.getCounter(CounterTypes.IF_COUNTER)

        if element["predicate"] is None:
            local_if_counter -= 1
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
                "B_{0}".format(Counters_Object.getCounter(CounterTypes.B_COUNTER)),
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
            if element["predicate"] is None:
                body = "IF_BODY_{0}".format(
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
            elif index == len(predicate_statements_list) - 1:
                body = "{0}.IF_BODY_{1}".format(
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
                    BodyElement(body, action_pointer, ElementsTypes.IF_CONDITION_RIGTH)
                )
            else:
                body = "{0}.IF_BODY_{1}".format(
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
            "IF_BODY_{0}".format(Counters_Object.getCounter(CounterTypes.BODY_COUNTER)),
            parametrs=protocol_params,
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
