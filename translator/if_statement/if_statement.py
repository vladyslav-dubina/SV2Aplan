from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.basic import BasicArray
from classes.cond_predicate import CondPredicate
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.node import Node
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import valuesToAplanStandart
from utils.utils import Color, Counters_Object, printWithColor


def conditionalPredecate2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Cond_predicateContext,
):
    sv_structure: Structure | None = self.structure_pointer_list.getLastElement()
    if sv_structure is None:
        printWithColor(
            f"WARNING: sv_structure is None in conditionalPredecate2AplanImpl.",
            Color.YELLOW,
        )
        return

    beh_index = sv_structure.getLastBehaviorIndex()
    if beh_index is None:
        printWithColor(
            f"WARNING: beh_index is None in conditionalPredecate2AplanImpl.",
            Color.YELLOW,
        )
        return

    element = self.condPredicate_pointer_list.getLastElement()

    if isinstance(element, CondPredicate):
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

        protocol_params = self.getProtocolParams()

        body = "{0}.IF_BODY_{1}".format(
            action_name,
            Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
        )

        if element.element_type == ElementsTypes.IF_ELSE_PREDICATE:
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

        pointer_list_len = self.condPredicate_pointer_list.getLen()
        continuation_flag = False
        if pointer_list_len - 2 >= 0:
            next_element = self.condPredicate_pointer_list.getElementByIndex(
                pointer_list_len - 2
            )
            if isinstance(next_element, CondPredicate):
                if next_element.name_space_level == element.name_space_level:
                    continuation_flag = True

        if continuation_flag == True:
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
            "IF_BODY_{0}".format(Counters_Object.getCounter(CounterTypes.BODY_COUNTER)),
            element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
            parametrs=protocol_params,
            inside_the_task=(self.inside_the_task or self.inside_the_function),
        )
        Counters_Object.incrieseCounter(CounterTypes.BODY_COUNTER)
    else:
        printWithColor(
            f"WARNING: Element is not condition predicate in conditionalPredecate2AplanImpl.",
            Color.YELLOW,
        )


def ifStatement2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Conditional_statementContext,
):
    statements = ctx.statement_or_null()
    predicate = ctx.cond_predicate()
    predicate_statements_list: BasicArray = BasicArray(CondPredicate)
    if len(predicate) == 1:
        predicate_statements_list.addElement(
            CondPredicate(
                "Single",
                predicate[0].getSourceInterval(),
                ElementsTypes.SINGLE_IF_PREDICATE,
                Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER),
            )
        )
    else:
        for i in range(len(statements)):

            if i <= len(predicate) - 1:

                predicate_source_inderval = predicate[i].getSourceInterval()

                if i == 0:
                    predicate_name = "If"
                    predicate_type = ElementsTypes.IF_PREDICATE
                else:
                    predicate_name = "If else"
                    predicate_type = ElementsTypes.IF_ELSE_PREDICATE

            else:

                predicate_name = "None"
                predicate_source_inderval = (0, 0)
                predicate_type = ElementsTypes.ELSE_PREDICATE

            predicate_statements_list.addElement(
                CondPredicate(
                    predicate_name,
                    predicate_source_inderval,
                    predicate_type,
                    Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER),
                )
            )
    Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)

    self.condPredicate_pointer_list += predicate_statements_list.reverse()
    sv_structure: Structure | None = self.structure_pointer_list.getLastElement()

    protocol_params = self.getProtocolParams()

    if sv_structure:
        beh_index = sv_structure.getLastBehaviorIndex()
        Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
        if beh_index is not None:
            sv_structure.behavior[beh_index].addBody(
                BodyElement(
                    identifier="IF_STATEMENT_{0}".format(
                        Counters_Object.getCounter(CounterTypes.B_COUNTER),
                    ),
                    element_type=ElementsTypes.PROTOCOL_ELEMENT,
                    parametrs=protocol_params,
                )
            )
        sv_structure.addProtocol(
            "IF_STATEMENT_{0}".format(
                Counters_Object.getCounter(CounterTypes.B_COUNTER)
            ),
            element_type=ElementsTypes.IF_STATEMENT_ELEMENT,
            parametrs=protocol_params,
            inside_the_task=(self.inside_the_task or self.inside_the_function),
        )
