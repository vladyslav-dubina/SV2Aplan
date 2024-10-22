from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.node import Node
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from translator.utils import getProtocolParams
from utils.string_formating import valuesToAplanStandart
from utils.utils import Counters_Object


def getLastCondPredicateList(self: SV2aplan):
    cond_predicate_lists_len = len(self.condPredicate_List)
    predicate_list = None
    initial_len = 0
    if cond_predicate_lists_len > 0:
        predicate_list, initial_len = self.condPredicate_List[
            cond_predicate_lists_len - 1
        ]
    return predicate_list, initial_len


def removeFirstCondPredicate(self: SV2aplan):
    predicate_list, initial_len = getLastCondPredicateList(self)
    if predicate_list:
        predicate_list = predicate_list[1:]
        if len(predicate_list) == 0:
            predicate_list = []

        cond_predicate_lists_len = len(self.condPredicate_List)
        self.condPredicate_List[cond_predicate_lists_len - 1] = (
            predicate_list,
            initial_len,
        )
    return predicate_list, initial_len


def findPredicate(self: SV2aplan, predicate):
    predicate_list, initial_len = getLastCondPredicateList(self)
    if predicate_list:
        for index, element in enumerate(predicate_list):
            if element:
                if (
                    element.getText() == predicate.getText()
                    and element.getSourceInterval() == predicate.getSourceInterval()
                ):
                    return index

    return len(predicate_list)


def conditionalPredecate2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Cond_predicateContext,
):
    sv_structure: Structure | None = self.structure_pointer_list.getLastElement()
    beh_index = sv_structure.getLastBehaviorIndex()
    if beh_index is not None:
        if (
            sv_structure.behavior[beh_index].element_type
            != ElementsTypes.IF_STATEMENT_ELEMENT
        ):
            return
    else:
        return

    predicate_list, initial_len = getLastCondPredicateList(self)
    if predicate_list != None:
        predicate_list_len = len(predicate_list)
        predicate_index = findPredicate(self, ctx)
        if predicate_index < predicate_list_len:
            Counters_Object.incrieseCounter(CounterTypes.IF_COUNTER)
            action_name = "if_{0}".format(
                Counters_Object.getCounter(CounterTypes.IF_COUNTER)
            )
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

            protocol_params = getProtocolParams(self)

            body = "{0}.IF_BODY_{1}".format(
                action_name,
                Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
            )

            if predicate_list_len != initial_len:
                beh_index = sv_structure.addProtocol(
                    "ELSE_BODY_{0}".format(
                        Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER)
                    ),
                    element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
                    parametrs=protocol_params,
                    inside_the_task=(self.inside_the_task or self.inside_the_function),
                )
                Counters_Object.incrieseCounter(CounterTypes.ELSE_BODY_COUNTER)

            sv_structure.behavior[beh_index].addBody(
                BodyElement(
                    body,
                    action_pointer,
                    ElementsTypes.IF_CONDITION_LEFT,
                    parametrs=protocol_params,
                )
            )

            if predicate_index < predicate_list_len - 1:

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
            else:
                sv_structure.behavior[beh_index].addBody(
                    BodyElement(
                        f"!{action_name}",
                        action_pointer,
                        ElementsTypes.IF_CONDITION_RIGTH,
                        parametrs=protocol_params,
                    )
                )

            sv_structure.addProtocol(
                "IF_BODY_{0}".format(
                    Counters_Object.getCounter(CounterTypes.BODY_COUNTER)
                ),
                element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
                parametrs=protocol_params,
                inside_the_task=(self.inside_the_task or self.inside_the_function),
            )
            Counters_Object.incrieseCounter(CounterTypes.BODY_COUNTER)


def ifStatement2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Conditional_statementContext,
):
    statements = ctx.statement_or_null()
    predicate = ctx.cond_predicate()
    predicate_statements_list = []
    for i in range(len(statements)):
        if i <= len(predicate) - 1:
            predicate_statements_list.append(predicate[i])
        else:
            predicate_statements_list.append(None)
    self.condPredicate_List.append(
        (predicate_statements_list, len(predicate_statements_list))
    )

    sv_structure: Structure | None = self.structure_pointer_list.getLastElement()

    protocol_params = getProtocolParams(self)

    if sv_structure:
        beh_index = sv_structure.getLastBehaviorIndex()
        if beh_index is not None:
            sv_structure.behavior[beh_index].addBody(
                BodyElement(
                    identifier="IF_STATEMENT_{0}".format(
                        Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER),
                    ),
                    element_type=ElementsTypes.PROTOCOL_ELEMENT,
                    parametrs=protocol_params,
                )
            )
        sv_structure.addProtocol(
            "IF_STATEMENT_{0}".format(
                Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER)
            ),
            element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
            parametrs=protocol_params,
            inside_the_task=(self.inside_the_task or self.inside_the_function),
        )
        Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
    return
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
                element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
            )
            predicate_ctx = element["predicate"]

            condition_txt = valuesToAplanStandart(predicate_ctx.getText())

            self.body2Aplan(
                predicate_ctx, destination_node_array=if_action.precondition
            )

            if_action.description_start.append(
                f"{self.module.identifier}#{self.module.ident_uniq_name}"
            )
            if_action.description_action_name = "if"
            if_action.description_end.append(f"{condition_txt}")

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
                inside_the_task=(self.inside_the_task or self.inside_the_function),
            )
        else:
            sv_structure.addProtocol(
                "ELSE_BODY_{0}".format(
                    Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER),
                ),
                parametrs=protocol_params,
                inside_the_task=(self.inside_the_task or self.inside_the_function),
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
            inside_the_task=(self.inside_the_task or self.inside_the_function),
        )
        Counters_Object.incrieseCounter(CounterTypes.BODY_COUNTER)

        if index == 0:
            self.name_space_list.append(ElementsTypes.IF_STATEMENT_ELEMENT)
        else:
            self.name_space_list.append(ElementsTypes.ELSE_BODY_ELEMENT)
