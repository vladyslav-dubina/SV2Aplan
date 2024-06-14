from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from antlr4_verilog.systemverilog import SystemVerilogParser
from structures.aplan import Module, Action, Always, ElementsTypes, Structure, DeclTypes
from structures.counters import CounterTypes
from utils import (
    addSpacesAroundOperators,
    valuesToAplanStandart,
    addBracketsAfterTilda,
    parallelAssignment2Assignment,
    vectorSizes2AplanStandart,
    notConcreteIndex2AplanStandart,
    Counters_Object,
)
import re


def extractVectorSize(s):
    matches = re.findall(r"\[(\d+):(\d+)\]", s)
    if matches:
        return matches[0]


def vectorSize2Aplan(left, right):
    if right == "0":
        left = int(left) + 1
        return [left, 0]
    else:
        right = int(right)
        left = int(left)
        return [left - right, right]


class SV2aplan:
    global Counters_Object

    def __init__(self, module: Module):
        self.module = module
        self.actionList = []

    def addCommaAndNeLines(self, input):
        if len(input) > 0:
            input = ",\n\n" + input
        return input

    def findAndChangeNamesToAplanNames(self, input: str):
        for elem in self.module.declarations:
            input = re.sub(
                r"\b{}\b".format(re.escape(elem.identifier)),
                "{}.{}".format(self.module.ident_uniq_name, elem.identifier),
                input,
            )
        return input

    def extractSensetive(self, ctx):
        res = ""
        for child in ctx.getChildren():
            if type(child) is SystemVerilogParser.Edge_identifierContext:
                index = child.getText().find("negedge")
                if index != -1:
                    res += "!"
            elif type(child) is Tree.TerminalNodeImpl:
                index = child.getText().find("or")
                if index != -1:
                    res += " || "
                index = child.getText().find("and")
                if index != -1:
                    res += " && "
            elif type(child) is SystemVerilogParser.IdentifierContext:
                res += self.findAndChangeNamesToAplanNames(child.getText())
            else:
                res += self.extractSensetive(child)
        return res

    def prepareExpressionString(self, expression: str, expr_type: ElementsTypes):
        expression = valuesToAplanStandart(expression)
        expression = addSpacesAroundOperators(expression)
        expression_with_replaced_names = self.findAndChangeNamesToAplanNames(expression)
        expression_with_replaced_names = addBracketsAfterTilda(
            expression_with_replaced_names
        )
        expression_with_replaced_names = vectorSizes2AplanStandart(
            expression_with_replaced_names
        )
        if ElementsTypes.ASSIGN_ELEMENT == expr_type:
            expression_with_replaced_names = parallelAssignment2Assignment(
                expression_with_replaced_names
            )
        expression_with_replaced_names = notConcreteIndex2AplanStandart(
            expression_with_replaced_names
        )
        return (expression, expression_with_replaced_names)

    def assign2Aplan(self, input: str):
        Counters_Object.incrieseCounter(CounterTypes.ASSIGNMENT_COUNTER)
        assign, assign_with_replaced_names = self.prepareExpressionString(
            input, ElementsTypes.ASSIGN_ELEMENT
        )
        action_name = "assign_{0}".format(
            Counters_Object.getCounter(CounterTypes.ASSIGNMENT_COUNTER)
        )

        assign_action = Action(
            "assign",
            Counters_Object.getCounter(CounterTypes.ASSIGNMENT_COUNTER),
        )
        assign_action.precondition.body.append("1")
        assign_action.description.body.append(
            f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{assign}'"
        )
        assign_action.postcondition.body.append(assign_with_replaced_names)

        action_check_result = self.module.isUniqAction(assign_action)
        if action_check_result is None:
            self.module.actions.append(assign_action)
        else:
            Counters_Object.decrieseCounter(CounterTypes.ASSIGNMENT_COUNTER)
            action_name = action_check_result
        return action_name

    def assert2Aplan(self, input: str):
        Counters_Object.incrieseCounter(CounterTypes.ASSERT_COUNTER)
        condition, condition_with_replaced_names = self.prepareExpressionString(
            input, ElementsTypes.ASSERT_ELEMENT
        )
        assert_name = "assert_{0}".format(
            Counters_Object.getCounter(CounterTypes.ASSERT_COUNTER)
        )
        assert_action = Action(
            "assert",
            Counters_Object.getCounter(CounterTypes.ASSERT_COUNTER),
        )
        assert_action.precondition.body.append(condition_with_replaced_names)
        assert_action.description.body.append(
            f"{self.module.identifier}#{self.module.ident_uniq_name}:action 'assert ({condition})'"
        )
        assert_action.postcondition.body.append("1")

        assert_check_result = self.module.isUniqAction(assert_action)
        if assert_check_result is None:
            self.module.actions.append(assert_action)
        else:
            Counters_Object.decrieseCounter(CounterTypes.ASSERT_COUNTER)
            assert_name = assert_check_result

        return assert_name

    def loop2Aplan(self, ctx, sv_structure: Structure):
        pass

    def body2Aplan(self, ctx, sv_structure: Structure):
        if ctx.getChildCount() == 0:
            return
        for child in ctx.getChildren():
            # Assert handler
            if (
                type(child)
                is SystemVerilogParser.Simple_immediate_assert_statementContext
            ):
                assert_name = self.assert2Aplan(child.expression().getText())
                Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                assert_b = "assert_B_{}".format(
                    Counters_Object.getCounter(CounterTypes.B_COUNTER)
                )
                beh_index = sv_structure.addProtocol(assert_b)
                sv_structure.behavior[beh_index].addBody(
                    "{0}.Delta + !{0}.0".format(assert_name)
                )
                if beh_index != 0:
                    sv_structure.behavior[beh_index - 1].addBody(assert_b)
            # Assign handler
            elif (
                type(child) is SystemVerilogParser.Variable_decl_assignmentContext
                or type(child) is SystemVerilogParser.Nonblocking_assignmentContext
            ):
                action_name = self.assign2Aplan(child.getText())
                beh_index = sv_structure.getLastBehaviorIndex()

                if type(child) is SystemVerilogParser.Nonblocking_assignmentContext:
                    action_name = "Sensetive(" + action_name + ")"

                if beh_index is not None:
                    sv_structure.behavior[beh_index].addBody(action_name)
                else:
                    Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                    b_index = sv_structure.addProtocol(
                        "B_{}".format(
                            Counters_Object.getCounter(CounterTypes.B_COUNTER)
                        )
                    )
                    sv_structure.behavior[b_index].addBody(action_name)
            elif type(child) is SystemVerilogParser.Conditional_statementContext:
                predicate = child.cond_predicate()
                statements = child.statement_or_null()

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
                            "if",
                            Counters_Object.getCounter(CounterTypes.IF_COUNTER),
                        )
                        predicate_string, predicate_with_replaced_names = (
                            self.prepareExpressionString(
                                element["predicate"].getText(),
                                ElementsTypes.IF_STATEMENT_ELEMENT,
                            )
                        )
                        if_action.precondition.body.append(
                            predicate_with_replaced_names
                        )
                        if_action.description.body.append(
                            f"{self.module.identifier}#{self.module.ident_uniq_name}:action 'if ({predicate_string})'"
                        )
                        if_action.postcondition.body.append("1")

                        if_check_result = self.module.isUniqAction(if_action)
                        if if_check_result is None:
                            self.module.actions.append(if_action)
                        else:
                            Counters_Object.decrieseCounter(CounterTypes.IF_COUNTER)
                            action_name = if_check_result

                    local_if_counter = Counters_Object.getCounter(
                        CounterTypes.IF_COUNTER
                    )
                    if element["predicate"] is None:
                        local_if_counter -= 1
                    if index == 0:
                        Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                        beh_index = sv_structure.getLastBehaviorIndex()
                        if beh_index is not None:
                            sv_structure.behavior[beh_index].addBody(
                                "B_{0}".format(
                                    Counters_Object.getCounter(CounterTypes.B_COUNTER)
                                )
                            )
                        sv_structure.addProtocol(
                            "B_{0}".format(
                                Counters_Object.getCounter(CounterTypes.B_COUNTER)
                            )
                        )
                    else:
                        sv_structure.addProtocol(
                            "else_body_{0}".format(
                                Counters_Object.getCounter(
                                    CounterTypes.ELSE_BODY_COUNTER
                                )
                            )
                        )
                        Counters_Object.incrieseCounter(CounterTypes.ELSE_BODY_COUNTER)

                    beh_index = sv_structure.getLastBehaviorIndex()
                    if beh_index is not None:
                        if element["predicate"] is None:
                            body = "body_{0}".format(
                                Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                            )
                        elif index == len(predicate_statements_list) - 1:
                            body = "{0}.body_{1} + !{0}".format(
                                action_name,
                                Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                            )
                        else:

                            body = "{0}.body_{1} + !{0}.else_body_{2}".format(
                                action_name,
                                Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                                Counters_Object.getCounter(
                                    CounterTypes.ELSE_BODY_COUNTER
                                ),
                            )

                        sv_structure.behavior[beh_index].addBody(body)

                    sv_structure.addProtocol(
                        "body_{0}".format(
                            Counters_Object.getCounter(CounterTypes.BODY_COUNTER)
                        )
                    )
                    Counters_Object.incrieseCounter(CounterTypes.BODY_COUNTER)
                    self.body2Aplan(element["statement"], sv_structure)

            else:
                self.body2Aplan(child, sv_structure)

    def generate2Aplan(self, ctx):
        generate_name = (
            "generate"
            + "_"
            + str(Counters_Object.getCounter(CounterTypes.LOOP_COUNTER))
        )
        struct = Structure(generate_name)
        struct.addProtocol(generate_name)
        self.body2Aplan(ctx, struct)
        self.module.structures.append(struct)
        Counters_Object.incrieseCounter(CounterTypes.LOOP_COUNTER)
        return

    def always2Aplan(self, ctx):
        sensetive = None

        always_keyword = ctx.always_keyword().getText()
        statement_item = ctx.statement().statement_item()
        if statement_item.procedural_timing_control_statement() is not None:
            event_expression = (
                statement_item.procedural_timing_control_statement()
                .procedural_timing_control()
                .event_control()
                .event_expression()
            )
            if event_expression is not None:
                sensetive = self.extractSensetive(event_expression)
            always_body = (
                statement_item.procedural_timing_control_statement().statement_or_null()
            )
        else:
            always_body = statement_item

        Counters_Object.incrieseCounter(CounterTypes.ALWAYS_COUNTER)
        always_name = (
            always_keyword
            + "_"
            + str(Counters_Object.getCounter(CounterTypes.ALWAYS_COUNTER))
        )
        always = Always(always_name, sensetive)
        always.addProtocol(always_name)
        # always.addProtocol(always_name)
        self.body2Aplan(always_body, always)
        self.module.structures.append(always)

        return

    def declaration2Aplan(self, ctx):
        assign_name = self.assign2Aplan(ctx.getText())
        return assign_name
