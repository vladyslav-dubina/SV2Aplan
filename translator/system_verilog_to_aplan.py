from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from antlr4_verilog.systemverilog import SystemVerilogParser
from structures.aplan import Module, Action, CounterTypes, Always, Protocol, Structure
from utils import addSpacesAroundOperators, valuesToAplanStandart, isInStrList
import re


def extractVectorSize(s):
    matches = re.findall(r"\[(\d+):(\d+)\]", s)
    if matches:
        return matches[0]


def vectorSize2Aplan(left, right):
    if right == "0":
        # Якщо праве значення дорівнює 0, додаємо 1 до лівого значення
        left = int(left) + 1
        return [left, 0]
    else:
        # Інакше віднімаємо ліве значення від правого
        right = int(right)
        left = int(left)
        return [left - right, right]


class SV2aplan:
    def __init__(self, module: Module):
        self.module = module
        self.actionList = []

    def addCommaAndNeLines(self, input):
        if len(input) > 0:
            input = ",\n\n" + input
        return input

    def findAndChangeNamesToAplanNames(self, input: str):
        for elem in self.module.declarations:
            input = input.replace(
                elem.identifier,
                "{0}.{1}".format(self.module.ident_uniq_name, elem.identifier),
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

    def assert2Aplan(self, input: str):
        self.module.incrieseCounter(CounterTypes.ASSERT)
        expression = addSpacesAroundOperators(input)
        expression_with_replaced_names = self.findAndChangeNamesToAplanNames(expression)
        expression_with_replaced_names = valuesToAplanStandart(
            expression_with_replaced_names
        )
        assert_name = "assert_{0}".format(self.module.assert_counter)
        action = assert_name + " = (\n\t\t({0})->\n".format(
            expression_with_replaced_names
        )
        action += "\t\t(\"{1}#{2}:action 'assert ({0})';\")\n\t\t(1)".format(
            expression, self.module.identifier, self.module.ident_uniq_name
        )
        action += ")"
        self.module.actions.append(Action("assert", self.module.assert_counter, action))
        return assert_name

    def body2Aplan(self, ctx, sv_structure: Structure):
        if ctx.getChildCount() == 0:
            return
        for child in ctx.getChildren():

            if (
                type(child)
                is SystemVerilogParser.Simple_immediate_assert_statementContext
            ):
                assert_name = self.assert2Aplan(child.expression().getText())
                assert_b = "assert_B_{}".format(self.module.assert_counter)
                beh_index = sv_structure.addProtocol(assert_b)
                sv_structure.behavior[beh_index].addBody(
                    "{0}.Delta + !{0}.0".format(assert_name)
                )
                if beh_index != 0:
                    sv_structure.behavior[beh_index - 1].addBody(assert_b)

            if (
                type(child) is SystemVerilogParser.Variable_decl_assignmentContext
                or type(child) is SystemVerilogParser.Nonblocking_assignmentContext
            ):
                self.module.incrieseCounter(CounterTypes.ASSIGNMENT_COUNTER)
                assign = addSpacesAroundOperators(child.getText())
                assign_with_replaced_names = self.findAndChangeNamesToAplanNames(assign)
                assign_with_replaced_names = valuesToAplanStandart(
                    assign_with_replaced_names
                )
                action_name = "assign_{0}".format(self.module.assignment_counter)
                action = action_name + " = (\n\t\t(1)->\n"
                action += "\t\t(\"{2}#{3}:action '{0}';\")\n\t\t({1})".format(
                    assign,
                    assign_with_replaced_names,
                    self.module.identifier,
                    self.module.ident_uniq_name,
                )
                action += ")"
                self.module.actions.append(
                    Action("assign", self.module.assignment_counter, action)
                )
                beh_index = sv_structure.getLastBehaviorIndex()

                if type(child) is SystemVerilogParser.Nonblocking_assignmentContext:
                    action_name = "Sensetive(" + action_name + ")"

                if beh_index is not None:
                    sv_structure.behavior[beh_index].addBody(action_name)
                else:
                    self.module.incrieseCounter(CounterTypes.B_COUNTER)
                    b_index = sv_structure.addProtocol(
                        "B_{}".format(self.module.b_counter)
                    )
                    sv_structure.behavior[b_index].addBody(action_name)

            elif type(child) is SystemVerilogParser.Conditional_statementContext:

                if_index_list = []
                subsiquence = []
                predicate = child.cond_predicate()
                for elem in predicate:
                    predicateString = addSpacesAroundOperators(elem.getText())
                    if len(predicateString) > 0:
                        self.module.incrieseCounter(CounterTypes.IF_COUNTER)
                        if_index_list.append(self.module.if_counter)
                        predicateWithReplacedNames = (
                            self.findAndChangeNamesToAplanNames(predicateString)
                        )
                        predicateWithReplacedNames = valuesToAplanStandart(
                            predicateWithReplacedNames
                        )
                        action = ""
                        action_name = "if_{0}".format(self.module.if_counter)
                        action += """{0} = (\n\t\t({1})->\n\t\t("{2}#{3}:action 'if ({4})';")\n\t\t(1))""".format(
                            action_name,
                            predicateWithReplacedNames,
                            self.module.identifier,
                            self.module.ident_uniq_name,
                            predicateString,
                        )
                        self.module.actions.append(
                            Action("if", self.module.if_counter, action)
                        )
                statements = child.statement_or_null()
                for index, element in enumerate(statements):
                    self.module.incrieseCounter(CounterTypes.B_COUNTER)
                    sv_structure.addProtocol("B_{0}".format(self.module.b_counter))
                    beh_index = sv_structure.getLastBehaviorIndex()
                    if beh_index is not None:
                        body = "if_{0}.body_{0} + !if_{0}.B_{1}".format(
                            if_index_list[index], self.module.b_counter
                        )
                        if index == len(statements) - 1:
                            body = "if_{0}.body_{0} + !if_{0}".format(
                                if_index_list[index]
                            )
                        sv_structure.behavior[beh_index].addBody(body)
                    sv_structure.addProtocol("body_{0}".format(if_index_list[index]))
                    subsiquence.append(0)
                    self.body2Aplan(element, sv_structure)

            else:
                self.body2Aplan(child, sv_structure)

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

        self.module.incrieseCounter(CounterTypes.ALWAYS_COUNTER)
        always_name = always_keyword + "_" + str(self.module.always_counter)
        always = Always(always_name, sensetive)

        # always.addProtocol(always_name)
        self.body2Aplan(always_body, always)
        if always.getBehLen() > 0:
            last_b_name = always.behavior[0].identifier
            always.behavior.insert(0, Protocol(always_name))
            always.behavior[0].body.append(last_b_name)
        self.module.structures.append(always)

        return

    def declaration2Aplan(self, ctx):
        self.module.incrieseCounter(CounterTypes.ASSIGNMENT_COUNTER)
        assign_sv = ctx.getText()
        assign_with_replaced_names = self.findAndChangeNamesToAplanNames(assign_sv)
        action = "assign{0} = (\n\t\t(1)->\n".format(self.module.assignment_counter)
        action += "\t\t(\"{2}#{3}:action '{0}';\")\n\t\t({1})".format(
            assign_sv,
            assign_with_replaced_names,
            self.module.identifier,
            self.module.ident_uniq_name,
        )
        action += ")"

        self.module.actions.append(
            Action("assign", self.module.assignment_counter, action)
        )
        expression = "assign{0}".format(self.module.assignment_counter)
        return expression
