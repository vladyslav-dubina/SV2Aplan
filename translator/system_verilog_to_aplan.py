from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from classes.declarations import Declaration, DeclTypes
from classes.actions import Action
from classes.structure import Structure
from classes.protocols import Protocol
from classes.always import Always
from classes.module import Module
from classes.element_types import ElementsTypes
from classes.counters import CounterTypes
from classes.name_change import NameChange
from utils.string_formating import (
    addSpacesAroundOperators,
    valuesToAplanStandart,
    addBracketsAfterTilda,
    addBracketsAfterNegation,
    addLeftValueForUnaryOrOperator,
    parallelAssignment2Assignment,
    vectorSizes2AplanStandart,
    notConcreteIndex2AplanStandart,
    doubleOperators2Aplan,
    replaceParametrsCalls,
    addEqueToBGET,
)
from utils.utils import (
    removeTypeFromForInit,
    Counters_Object,
    printWithColor,
    Color,
)
from typing import Tuple, List
import re


class SV2aplan:
    global Counters_Object

    def __init__(self, module: Module):
        self.module = module
        self.actionList = []

    def findAndChangeNamesToAgentAttrCall(self, input: str):
        for elem in self.module.declarations.getElements():
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
                res += self.findAndChangeNamesToAgentAttrCall(child.getText())
            else:
                res += self.extractSensetive(child)
        return res

    def prepareExpressionString(self, expression: str, expr_type: ElementsTypes):
        expression = valuesToAplanStandart(expression)
        expression = doubleOperators2Aplan(expression)
        expression = addLeftValueForUnaryOrOperator(expression)
        expression = addSpacesAroundOperators(expression)
        if ElementsTypes.ASSIGN_FOR_CALL_ELEMENT != expr_type:
            expression_with_replaced_names = self.findAndChangeNamesToAgentAttrCall(
                expression
            )
        else:
            expression_with_replaced_names = expression

        expression_with_replaced_names = addBracketsAfterNegation(
            expression_with_replaced_names
        )
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
            expression_with_replaced_names, self.module
        )
        expression_with_replaced_names = replaceParametrsCalls(
            self.module.parametrs, expression_with_replaced_names
        )
        return (expression, expression_with_replaced_names)

    def moduleCall2Aplan(
        self,
        ctx: SystemVerilogParser.Module_instantiationContext,
        destination_module_name: str,
    ):
        for hierarchical_instance in ctx.hierarchical_instance():
            instance = hierarchical_instance.name_of_instance().getText()
            index = instance.find("core")
            if index != -1:
                Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                call_assign_b = "MODULE_ASSIGN_B_{}".format(
                    Counters_Object.getCounter(CounterTypes.B_COUNTER)
                )
                struct_call_assign = Protocol(
                    call_assign_b,
                    ctx.getSourceInterval(),
                )

                for (
                    order_port_connection
                ) in (
                    hierarchical_instance.list_of_port_connections().ordered_port_connection()
                ):
                    printWithColor(f"Unhandled case for module call", Color.RED)

                assign_str_list: List[str] = []
                for (
                    named_port_connection
                ) in (
                    hierarchical_instance.list_of_port_connections().named_port_connection()
                ):
                    assign_str = "{0}.{1}={2}.{3}".format(
                        destination_module_name,
                        named_port_connection.port_identifier().getText(),
                        self.module.ident_uniq_name,
                        named_port_connection.expression().getText(),
                    )
                    assign_str_list.append(assign_str)

                action_name, source_interval = self.expression2Aplan(
                    assign_str_list,
                    ElementsTypes.ASSIGN_FOR_CALL_ELEMENT,
                    ctx.getSourceInterval(),
                )
                struct_call_assign.addBody((action_name, ElementsTypes.ACTION_ELEMENT))

                self.module.out_of_block_elements.addElement(struct_call_assign)

    def expression2Aplan(
        self,
        input: str | List[str],
        cond_type: ElementsTypes,
        source_interval: Tuple[int, int],
    ):
        name_part = ""
        counter_type = CounterTypes.NONE_COUNTER

        if cond_type == ElementsTypes.ASSERT_ELEMENT:
            name_part = "assert"
            counter_type = CounterTypes.ASSERT_COUNTER
        elif cond_type == ElementsTypes.CONDITION_ELEMENT:
            name_part = "cond"
            counter_type = CounterTypes.CONDITION_COUNTER
        elif (
            cond_type == ElementsTypes.ASSIGN_ELEMENT
            or cond_type == ElementsTypes.ASSIGN_FOR_CALL_ELEMENT
        ):
            name_part = "assign"
            counter_type = CounterTypes.ASSIGNMENT_COUNTER

        action_name = "{0}_{1}".format(
            name_part, Counters_Object.getCounter(counter_type)
        )

        if cond_type != ElementsTypes.ASSIGN_FOR_CALL_ELEMENT:
            input = self.module.name_change.changeNamesInStr(input)
            expression, expression_with_replaced_names = self.prepareExpressionString(
                input, cond_type
            )

        action = Action(
            name_part,
            Counters_Object.getCounter(counter_type),
            source_interval,
        )

        if cond_type == ElementsTypes.ASSIGN_ELEMENT:
            action.precondition.body.append("1")
            action.postcondition.body.append(expression_with_replaced_names)
            action.description.body.append(
                f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({expression})'"
            )
        elif cond_type == ElementsTypes.ASSIGN_FOR_CALL_ELEMENT:
            action.precondition.body.append("1")
            descroption = ""
            for index, input_str in enumerate(input):
                if index != 0:
                    descroption += "; "
                (
                    expression,
                    expression_with_replaced_names,
                ) = self.prepareExpressionString(input_str, cond_type)
                action.postcondition.body.append(expression_with_replaced_names)
                descroption += expression

            action.description.body.append(
                f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({descroption})'"
            )
        else:
            action.precondition.body.append(expression_with_replaced_names)
            action.postcondition.body.append("1")
            action.description.body.append(
                f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({expression})'"
            )

        action_check_result, source_interval = self.module.actions.isUniqAction(action)
        if action_check_result is None:
            self.module.actions.addElement(action)
        else:
            Counters_Object.decrieseCounter(counter_type)
            action_name = action_check_result

        Counters_Object.incrieseCounter(counter_type)
        return (action_name, source_interval)

    def forDeclarationToApan(self, ctx: SystemVerilogParser.For_initializationContext):
        assign_name = ""
        expression = ctx.for_variable_declaration(0)
        if expression is not None:
            original_identifier = expression.variable_identifier(0).getText()
            identifier = (
                original_identifier
                + f"_{Counters_Object.getCounter(CounterTypes.LOOP_COUNTER)}"
            )
            data_type = expression.data_type().getText()
            size_expression = data_type
            data_type = DeclTypes.checkType(data_type)
            decl_index = self.module.declarations.addElement(
                Declaration(
                    data_type,
                    identifier,
                    assign_name,
                    size_expression,
                    0,
                    "",
                    0,
                    expression.getSourceInterval(),
                )
            )
            self.module.name_change.addElement(
                NameChange(
                    identifier, expression.getSourceInterval(), original_identifier
                )
            )
            sv2aplan = SV2aplan(self.module)
            if expression.expression(0) is not None:
                action_txt = f"{identifier}={expression.expression(0).getText()}"
                assign_name, source_interval = sv2aplan.expression2Aplan(
                    action_txt, ElementsTypes.ASSIGN_ELEMENT, ctx.getSourceInterval()
                )
            declaration = self.module.declarations.getElementByIndex(decl_index)
            declaration.expression = assign_name

            return identifier
        return None

    def loop2Aplan(
        self,
        ctx: (
            SystemVerilogParser.Loop_generate_constructContext
            | SystemVerilogParser.Loop_statementContext
        ),
        sv_structure: Structure,
    ):
        for_decl_identifier: str | None = None
        if type(ctx) is SystemVerilogParser.Loop_statementContext:
            for_decl_identifier = self.forDeclarationToApan(ctx.for_initialization())

        beh_index = sv_structure.getLastBehaviorIndex()
        if beh_index is not None:
            sv_structure.behavior[beh_index].addBody(
                (
                    "LOOP_{0}".format(
                        Counters_Object.getCounter(CounterTypes.LOOP_COUNTER)
                    ),
                    ElementsTypes.PROTOCOL_ELEMENT,
                )
            )

        # LOOP
        beh_index = sv_structure.addProtocol(
            "LOOP_{0}".format(Counters_Object.getCounter(CounterTypes.LOOP_COUNTER))
        )
        sv_structure.behavior[beh_index].addBody(
            (
                "(LOOP_INIT_{0};LOOP_MAIN_{0})".format(
                    Counters_Object.getCounter(CounterTypes.LOOP_COUNTER),
                ),
                ElementsTypes.PROTOCOL_ELEMENT,
            )
        )

        # LOOP MAIN
        beh_index = sv_structure.addProtocol(
            "LOOP_MAIN_{0}".format(
                Counters_Object.getCounter(CounterTypes.LOOP_COUNTER)
            )
        )

        # LOOP CONDITION
        condition_name = ""
        if type(ctx) is SystemVerilogParser.Loop_generate_constructContext:
            condition = ctx.genvar_expression().getText()
            condition_name, source_interval = self.expression2Aplan(
                condition,
                ElementsTypes.CONDITION_ELEMENT,
                ctx.genvar_expression().getSourceInterval(),
            )
        elif type(ctx) is SystemVerilogParser.Loop_statementContext:
            condition = ctx.expression().getText()
            condition_name, source_interval = self.expression2Aplan(
                condition,
                ElementsTypes.CONDITION_ELEMENT,
                ctx.expression().getSourceInterval(),
            )

        sv_structure.behavior[beh_index].addBody(
            (
                "{1}.(LOOP_BODY_{0};LOOP_INC_{0};LOOP_MAIN_{0}) + !{1}".format(
                    Counters_Object.getCounter(CounterTypes.LOOP_COUNTER),
                    condition_name,
                ),
                ElementsTypes.ACTION_ELEMENT,
            )
        )

        # LOOP INIT
        initialization = ""
        if type(ctx) is SystemVerilogParser.Loop_generate_constructContext:
            initialization = ctx.genvar_initialization().getText()
            action_name, source_interval = self.expression2Aplan(
                initialization,
                ElementsTypes.ASSIGN_ELEMENT,
                ctx.genvar_initialization().getSourceInterval(),
            )
        elif type(ctx) is SystemVerilogParser.Loop_statementContext:
            initialization = removeTypeFromForInit(ctx.for_initialization())
            action_name, source_interval = self.expression2Aplan(
                initialization,
                ElementsTypes.ASSIGN_ELEMENT,
                ctx.for_initialization().getSourceInterval(),
            )

        beh_index = sv_structure.addProtocol(
            "LOOP_INIT_{0}".format(
                Counters_Object.getCounter(CounterTypes.LOOP_COUNTER)
            )
        )
        sv_structure.behavior[beh_index].addBody(
            (action_name, ElementsTypes.ACTION_ELEMENT)
        )

        # LOOP INC
        iteration = ""
        if type(ctx) is SystemVerilogParser.Loop_generate_constructContext:
            iteration = ctx.genvar_iteration().getText()
            action_name, source_interval = self.expression2Aplan(
                iteration,
                ElementsTypes.ASSIGN_ELEMENT,
                ctx.genvar_iteration().getSourceInterval(),
            )
        elif type(ctx) is SystemVerilogParser.Loop_statementContext:
            iteration = ctx.for_step().getText()
            action_name, source_interval = self.expression2Aplan(
                iteration,
                ElementsTypes.ASSIGN_ELEMENT,
                ctx.for_step().getSourceInterval(),
            )

        beh_index = sv_structure.addProtocol(
            "LOOP_INC_{0}".format(Counters_Object.getCounter(CounterTypes.LOOP_COUNTER))
        )
        sv_structure.behavior[beh_index].addBody(
            (action_name, ElementsTypes.ACTION_ELEMENT)
        )

        # BODY LOOP
        sv_structure.addProtocol(
            "LOOP_BODY_{0}".format(
                Counters_Object.getCounter(CounterTypes.LOOP_COUNTER)
            )
        )

        if type(ctx) is SystemVerilogParser.Loop_generate_constructContext:
            self.body2Aplan(ctx.generate_block(), sv_structure)
        elif type(ctx) is SystemVerilogParser.Loop_statementContext:
            self.body2Aplan(ctx.statement_or_null(), sv_structure)

        Counters_Object.incrieseCounter(CounterTypes.LOOP_COUNTER)
        self.module.name_change.deleteElement(for_decl_identifier)

    def body2Aplan(self, ctx, sv_structure: Structure):
        if ctx.getChildCount() == 0:
            return
        for child in ctx.getChildren():
            # Assert handler
            if (
                type(child)
                is SystemVerilogParser.Simple_immediate_assert_statementContext
            ):
                assert_name, source_interval = self.expression2Aplan(
                    child.expression().getText(),
                    ElementsTypes.ASSERT_ELEMENT,
                    child.expression().getSourceInterval(),
                )
                Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                assert_b = "ASSERT_B_{}".format(
                    Counters_Object.getCounter(CounterTypes.B_COUNTER)
                )
                beh_index = sv_structure.addProtocol(assert_b)
                sv_structure.behavior[beh_index].addBody(
                    (
                        "{0}.Delta + !{0}.0".format(assert_name),
                        ElementsTypes.ACTION_ELEMENT,
                    )
                )
                if beh_index != 0:
                    sv_structure.behavior[beh_index - 1].addBody(
                        (assert_b, ElementsTypes.PROTOCOL_ELEMENT)
                    )
            # Assign handler
            elif (
                type(child) is SystemVerilogParser.Variable_decl_assignmentContext
                or type(child) is SystemVerilogParser.Nonblocking_assignmentContext
                or type(child) is SystemVerilogParser.Net_assignmentContext
                or type(child) is SystemVerilogParser.Variable_assignmentContext
            ):
                action_name, source_interval = self.expression2Aplan(
                    child.getText(),
                    ElementsTypes.ASSIGN_ELEMENT,
                    child.getSourceInterval(),
                )
                beh_index = sv_structure.getLastBehaviorIndex()

                if type(child) is SystemVerilogParser.Nonblocking_assignmentContext:
                    action_name = "Sensetive(" + action_name + ")"
                if beh_index is not None:
                    sv_structure.behavior[beh_index].addBody(
                        (action_name, ElementsTypes.ACTION_ELEMENT)
                    )
                else:
                    Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                    b_index = sv_structure.addProtocol(
                        "B_{}".format(
                            Counters_Object.getCounter(CounterTypes.B_COUNTER)
                        )
                    )
                    sv_structure.behavior[b_index].addBody(
                        (action_name, ElementsTypes.ACTION_ELEMENT)
                    )
            elif type(child) is SystemVerilogParser.For_variable_declarationContext:
                assign_name = ""
                data_type = ctx.data_type().getText()
                size_expression = data_type
                sv2aplan = SV2aplan(self.module)
                if ctx.expression(0) is not None:
                    action_txt = f"{ctx.variable_identifier(0).getText()}={ctx.expression(0).getText()}"
                    assign_name, source_interval = sv2aplan.expression2Aplan(
                        action_txt,
                        ElementsTypes.ASSIGN_ELEMENT,
                        ctx.getSourceInterval(),
                    )
                data_type = DeclTypes.checkType(data_type)
                self.module.declarations.addElement(
                    Declaration(
                        data_type,
                        ctx.variable_identifier(0).getText(),
                        assign_name,
                        size_expression,
                        0,
                        "",
                        0,
                        ctx.getSourceInterval(),
                    )
                )
            elif type(child) is SystemVerilogParser.Loop_statementContext:
                self.loop2Aplan(child, sv_structure)
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
                            child.getSourceInterval(),
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
                        predicate_with_replaced_names = addEqueToBGET(
                            predicate_with_replaced_names
                        )
                        if_action.precondition.body.append(
                            predicate_with_replaced_names
                        )
                        if_action.description.body.append(
                            f"{self.module.identifier}#{self.module.ident_uniq_name}:action 'if ({predicate_string})'"
                        )
                        if_action.postcondition.body.append("1")

                        (
                            if_check_result,
                            source_interval,
                        ) = self.module.actions.isUniqAction(if_action)
                        if if_check_result is None:
                            self.module.actions.addElement(if_action)
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
                                (
                                    "B_{0}".format(
                                        Counters_Object.getCounter(
                                            CounterTypes.B_COUNTER
                                        )
                                    ),
                                    ElementsTypes.PROTOCOL_ELEMENT,
                                )
                            )
                        sv_structure.addProtocol(
                            "B_{0}".format(
                                Counters_Object.getCounter(CounterTypes.B_COUNTER)
                            )
                        )
                    else:
                        sv_structure.addProtocol(
                            "ELSE_BODY_{0}".format(
                                Counters_Object.getCounter(
                                    CounterTypes.ELSE_BODY_COUNTER
                                )
                            )
                        )
                        Counters_Object.incrieseCounter(CounterTypes.ELSE_BODY_COUNTER)

                    beh_index = sv_structure.getLastBehaviorIndex()
                    if beh_index is not None:
                        if element["predicate"] is None:
                            body = "IF_BODY_{0}".format(
                                Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                            )
                        elif index == len(predicate_statements_list) - 1:
                            body = "{0}.IF_BODY_{1} + !{0}".format(
                                action_name,
                                Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                            )
                        else:
                            body = "{0}.IF_BODY_{1} + !{0}.ELSE_BODY_{2}".format(
                                action_name,
                                Counters_Object.getCounter(CounterTypes.BODY_COUNTER),
                                Counters_Object.getCounter(
                                    CounterTypes.ELSE_BODY_COUNTER
                                ),
                            )

                        sv_structure.behavior[beh_index].addBody(
                            (body, ElementsTypes.ACTION_ELEMENT)
                        )

                    sv_structure.addProtocol(
                        "IF_BODY_{0}".format(
                            Counters_Object.getCounter(CounterTypes.BODY_COUNTER)
                        )
                    )
                    Counters_Object.incrieseCounter(CounterTypes.BODY_COUNTER)
                    self.body2Aplan(element["statement"], sv_structure)

            else:
                self.body2Aplan(child, sv_structure)

    def generate2Aplan(self, ctx: SystemVerilogParser.Loop_generate_constructContext):
        generate_name = (
            "GENERATE"
            + "_"
            + str(Counters_Object.getCounter(CounterTypes.LOOP_COUNTER))
        )
        struct = Structure(
            generate_name,
            ctx.getSourceInterval(),
        )
        struct.addProtocol(generate_name)
        self.loop2Aplan(ctx, struct)
        self.module.structures.addElement(struct)
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
            always_keyword.upper()
            + "_"
            + str(Counters_Object.getCounter(CounterTypes.ALWAYS_COUNTER))
        )
        always = Always(
            always_name,
            sensetive,
            ctx.getSourceInterval(),
        )
        always.addProtocol(always_name)
        # always.addProtocol(always_name)
        self.body2Aplan(always_body, always)
        self.module.structures.addElement(always)

        return

    def declaration2Aplan(self, ctx):
        assign_name, source_interval = self.expression2Aplan(
            ctx.getText(), ElementsTypes.ASSIGN_ELEMENT, ctx.getSourceInterval()
        )
        return assign_name
