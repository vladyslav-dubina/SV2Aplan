from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from classes.declarations import Declaration, DeclTypes
from classes.actions import Action
from classes.structure import Structure
from classes.protocols import Protocol
from classes.always import Always
from classes.module import Module
from classes.processed import ProcessedElement
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
    replace_cpp_operators,
    replaceArrayIndexing,
)
from utils.utils import (
    removeTypeFromForInit,
    extractVectorSize,
    extractDimentionSize,
    vectorSize2AplanVectorSize,
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
                res += self.module.findAndChangeNamesToAgentAttrCall(child.getText())
            else:
                res += self.extractSensetive(child)
        return res

    def prepareExpressionString(self, expression: str, expr_type: ElementsTypes):
        expression = valuesToAplanStandart(expression)
        expression = doubleOperators2Aplan(expression)
        expression = addLeftValueForUnaryOrOperator(expression)
        expression = addSpacesAroundOperators(expression)
        if ElementsTypes.ASSIGN_FOR_CALL_ELEMENT != expr_type:
            expression_with_replaced_names = (
                self.module.findAndChangeNamesToAgentAttrCall(expression)
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
                    ElementsTypes.MODULE_ASSIGN_ELEMENT,
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
                action_name = f"Sensetive({action_name})"
                struct_call_assign.addBody((action_name, ElementsTypes.ACTION_ELEMENT))

                self.module.out_of_block_elements.addElement(struct_call_assign)

    def expression2Aplan(
        self,
        input: str | List[str],
        element_type: ElementsTypes,
        source_interval: Tuple[int, int],
    ):
        name_part = ""
        counter_type = CounterTypes.NONE_COUNTER

        if element_type == ElementsTypes.ASSERT_ELEMENT:
            name_part = "assert"
            counter_type = CounterTypes.ASSERT_COUNTER
        elif element_type == ElementsTypes.CONDITION_ELEMENT:
            name_part = "cond"
            counter_type = CounterTypes.CONDITION_COUNTER
        elif (
            element_type == ElementsTypes.ASSIGN_ELEMENT
            or element_type == ElementsTypes.ASSIGN_FOR_CALL_ELEMENT
        ):
            name_part = "assign"
            counter_type = CounterTypes.ASSIGNMENT_COUNTER

        action_name = "{0}_{1}".format(
            name_part, Counters_Object.getCounter(counter_type)
        )

        if element_type != ElementsTypes.ASSIGN_FOR_CALL_ELEMENT:
            input = self.module.name_change.changeNamesInStr(input)
            expression, expression_with_replaced_names = self.prepareExpressionString(
                input, element_type
            )

        action = Action(
            name_part,
            Counters_Object.getCounter(counter_type),
            source_interval,
        )

        if element_type == ElementsTypes.ASSIGN_ELEMENT:
            action.precondition.body.append("1")
            action.postcondition.body.append(expression_with_replaced_names)
            action.description.body.append(
                f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{name_part} ({expression})'"
            )
        elif element_type == ElementsTypes.ASSIGN_FOR_CALL_ELEMENT:
            action.precondition.body.append("1")
            descroption = ""
            for index, input_str in enumerate(input):
                if index != 0:
                    descroption += "; "
                (
                    expression,
                    expression_with_replaced_names,
                ) = self.prepareExpressionString(input_str, element_type)
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
            decl_unique, decl_index = self.module.declarations.addElement(
                Declaration(
                    data_type,
                    identifier,
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
        loop_init = "LOOP_INIT_{0};".format(
            Counters_Object.getCounter(CounterTypes.LOOP_COUNTER)
        )
        loop_inc = "LOOP_INC_{0};".format(
            Counters_Object.getCounter(CounterTypes.LOOP_COUNTER)
        )

        loop_init_flag = True
        loop_inс_flag = True

        if type(ctx) is SystemVerilogParser.Loop_statementContext:
            for_initialization_ctx = ctx.for_initialization()
            for_inc_ctx = ctx.for_step()
            if for_inc_ctx is None:
                loop_inс_flag = False
            if for_initialization_ctx is not None:
                for_decl_identifier = self.forDeclarationToApan(for_initialization_ctx)
            else:
                loop_init_flag = False

        if loop_init_flag == False:
            loop_init = ""

        if loop_inс_flag == False:
            loop_inc = ""

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
                "({0}LOOP_MAIN_{1})".format(
                    loop_init,
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
                "{1}.(LOOP_BODY_{0};{2}LOOP_MAIN_{0}) + !{1}".format(
                    Counters_Object.getCounter(CounterTypes.LOOP_COUNTER),
                    condition_name,
                    loop_inc,
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
            loop_init_flag = True
        elif type(ctx) is SystemVerilogParser.Loop_statementContext:
            if loop_init_flag == True:
                initialization = removeTypeFromForInit(ctx.for_initialization())
                action_name, source_interval = self.expression2Aplan(
                    initialization,
                    ElementsTypes.ASSIGN_ELEMENT,
                    ctx.for_initialization().getSourceInterval(),
                )

        if loop_init_flag == True:
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
            if loop_inс_flag == True:
                iteration = ctx.for_step().getText()
                action_name, source_interval = self.expression2Aplan(
                    iteration,
                    ElementsTypes.ASSIGN_ELEMENT,
                    ctx.for_step().getSourceInterval(),
                )

        if loop_inс_flag == True:
            beh_index = sv_structure.addProtocol(
                "LOOP_INC_{0}".format(
                    Counters_Object.getCounter(CounterTypes.LOOP_COUNTER)
                )
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
            self.body2Aplan(
                ctx.generate_block(), sv_structure, ElementsTypes.LOOP_ELEMENT
            )
        elif type(ctx) is SystemVerilogParser.Loop_statementContext:
            self.body2Aplan(
                ctx.statement_or_null(), sv_structure, ElementsTypes.LOOP_ELEMENT
            )

        Counters_Object.incrieseCounter(CounterTypes.LOOP_COUNTER)
        self.module.name_change.deleteElement(for_decl_identifier)

    def body2Aplan(self, ctx, sv_structure: Structure, name_space: ElementsTypes):
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
                identifier = ctx.variable_identifier(0).getText()
                self.module.declarations.addElement(
                    Declaration(
                        data_type,
                        identifier,
                        identifier,
                        assign_name,
                        size_expression,
                        0,
                        "",
                        0,
                        ctx.getSourceInterval(),
                    )
                )
            elif type(child) is SystemVerilogParser.Data_declarationContext:
                from translator.declarations.data_declaration import (
                    dataDecaration2Aplan,
                )

                data_type = child.data_type_or_implicit().getText()
                if len(data_type) > 0:
                    action_name = dataDecaration2Aplan(
                        child, self.module, False, name_space
                    )

                    beh_index = sv_structure.getLastBehaviorIndex()
                    if beh_index is not None and action_name is not None:
                        sv_structure.behavior[beh_index].addBody(
                            (action_name, ElementsTypes.ACTION_ELEMENT)
                        )
                else:
                    self.body2Aplan(child, sv_structure, name_space)
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
                        predicate_txt = self.module.name_change.changeNamesInStr(
                            predicate_txt
                        )
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
                    if index == 0:
                        self.body2Aplan(
                            element["statement"],
                            sv_structure,
                            ElementsTypes.IF_STATEMENT_ELEMENT,
                        )
                    else:
                        self.body2Aplan(
                            element["statement"],
                            sv_structure,
                            ElementsTypes.ELSE_BODY_ELEMENT,
                        )

            else:
                self.body2Aplan(child, sv_structure, name_space)

    def replaceGenvarToValue(self, expression: str, genvar: str, value: int):
        expression = re.sub(
            r"\b{}\b".format(re.escape(genvar)),
            f"{value}",
            expression,
        )
        return expression

    def generateBodyToAplan(
        self, ctx, sv_structure: Structure, init_var_name, current_value
    ):
        if ctx.getChildCount() == 0:
            return
        for child in ctx.getChildren():
            if (
                type(child) is SystemVerilogParser.Variable_decl_assignmentContext
                or type(child) is SystemVerilogParser.Nonblocking_assignmentContext
                or type(child) is SystemVerilogParser.Net_assignmentContext
                or type(child) is SystemVerilogParser.Variable_assignmentContext
            ):
                expression = child.getText()
                expression = self.replaceGenvarToValue(
                    expression, init_var_name, current_value
                )
                self.module.processed_elements.addElement(
                    ProcessedElement("action", child.getSourceInterval())
                )
                action_name, source_interval = self.expression2Aplan(
                    expression,
                    ElementsTypes.ASSIGN_ELEMENT,
                    child.getSourceInterval(),
                )
                action_name = f"Sensetive({action_name})"
                sv_structure.behavior[0].addBody(
                    (action_name, ElementsTypes.ACTION_ELEMENT)
                )

            else:
                self.generateBodyToAplan(
                    child, sv_structure, init_var_name, current_value
                )

    def generate2Aplan(self, ctx: SystemVerilogParser.Loop_generate_constructContext):
        def prepareGenerateExpression(module: Module, expression: str):
            expression = replace_cpp_operators(expression)
            expression = parallelAssignment2Assignment(expression)
            expression = replaceParametrsCalls(module.parametrs, expression)

            return expression

        generate_name = (
            "GENERATE"
            + "_"
            + str(Counters_Object.getCounter(CounterTypes.LOOP_COUNTER))
        )
        struct = Structure(
            generate_name,
            ctx.getSourceInterval(),
        )
        struct.addProtocol(generate_name, ElementsTypes.GENERATE_ELEMENT)
        initialization = ctx.genvar_initialization().getText()
        initialization = prepareGenerateExpression(self.module, initialization)

        condition = ctx.genvar_expression().getText()
        condition = prepareGenerateExpression(self.module, condition)

        iteration = ctx.genvar_iteration().getText()
        iteration = prepareGenerateExpression(self.module, iteration)
        init_var_name = initialization.split("=")[0]
        exec(initialization)
        while eval(condition):
            current_value = eval(init_var_name)
            self.generateBodyToAplan(
                ctx.generate_block(), struct, init_var_name, current_value
            )
            exec(iteration)
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
        self.body2Aplan(always_body, always, ElementsTypes.ALWAYS_ELEMENT)
        self.module.structures.addElement(always)

        return

    def declaration2Aplan(self, ctx):
        assign_name, source_interval = self.expression2Aplan(
            ctx.getText(), ElementsTypes.ASSIGN_ELEMENT, ctx.getSourceInterval()
        )
        return assign_name
