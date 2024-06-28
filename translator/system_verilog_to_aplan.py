from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from classes.actions import Action
from classes.module_call import ModuleCall
from classes.structure import Structure
from classes.protocols import Protocol
from classes.always import Always
from classes.module import Module
from classes.processed import ProcessedElement
from classes.element_types import ElementsTypes
from classes.counters import CounterTypes
from program.program import Program
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

    # ---------------------------------------------------------------------------------
    def netAssignment2Aplan(self, ctx: SystemVerilogParser.Net_assignmentContext):
        from translator.assignments.net_assignment import netAssignment2AplanImpl

        netAssignment2AplanImpl(self, ctx)

    # ---------------------------------------------------------------------------------
    def paramAssignment2Aplan(
        self, ctx: SystemVerilogParser.Param_assignmentContext, module_call: ModuleCall
    ):
        from translator.assignments.param_assignment import paramAssignment2AplanImpl

        paramAssignment2AplanImpl(self, ctx, module_call)

    # ---------------------------------------------------------------------------------
    def blockAssignment2Aplan(
        self,
        ctx: (
            SystemVerilogParser.Variable_decl_assignmentContext
            | SystemVerilogParser.Nonblocking_assignmentContext
            | SystemVerilogParser.Net_assignmentContext
            | SystemVerilogParser.Variable_assignmentContext
        ),
        sv_structure: Structure,
    ):
        from translator.assignments.in_block_assignments import (
            blockAssignment2AplanImpl,
        )

        blockAssignment2AplanImpl(self, ctx, self.module, sv_structure)

    # ---------------------------------------------------------------------------------

    # =============================DECLARATIONS========================================
    def genvarDeclaration2Aplan(
        self, ctx: SystemVerilogParser.Genvar_declarationContext
    ):
        from translator.declarations.genvar_declaration import (
            genvarDeclaration2AplanImpl,
        )

        genvarDeclaration2AplanImpl(self, ctx)

    # ---------------------------------------------------------------------------------
    def ansiPortDeclaration2Aplan(
        self, ctx: SystemVerilogParser.Ansi_port_declarationContext
    ):
        from translator.declarations.ansi_port_declaration import (
            ansiPortDeclaration2AplanImpl,
        )

        ansiPortDeclaration2AplanImpl(self, ctx)

    # ---------------------------------------------------------------------------------
    def dataDecaration2Aplan(
        self,
        ctx: SystemVerilogParser.Data_declarationContext,
        listener: bool,
        sv_structure: Structure | None = None,
        name_space: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        from translator.declarations.data_declaration import dataDecaration2AplanImpl

        return dataDecaration2AplanImpl(self, ctx, listener, sv_structure, name_space)

    # ---------------------------------------------------------------------------------
    def netDeclaration2Aplan(self, ctx: SystemVerilogParser.Net_declarationContext):
        from translator.declarations.net_declaration import (
            netDeclaration2AplanImpl,
        )

        netDeclaration2AplanImpl(self, ctx)

    # ---------------------------------------------------------------------------------

    def forInitializationToApan(self, ctx: SystemVerilogParser.Net_declarationContext):
        from translator.declarations.for_declaration import (
            forInitializationToApanImpl,
        )

        return forInitializationToApanImpl(self, ctx)

    # ---------------------------------------------------------------------------------

    def forDeclarationToApan(self, ctx: SystemVerilogParser.Net_declarationContext):
        from translator.declarations.for_declaration import (
            forDeclarationToApanImpl,
        )

        forDeclarationToApanImpl(self, ctx)

    # ==================================================================================
    # ====================================CALLS=========================================
    def moduleCall2Apan(
        self,
        ctx: SystemVerilogParser.Module_instantiationContext,
        program: Program,
    ):
        from translator.calls.module_call import (
            moduleCall2AplanImpl,
        )

        moduleCall2AplanImpl(self, ctx, program)

    # ==================================================================================
    # ===================================ASSERTS=======================================
    def assertPropertyStatement2Aplan(
        self, ctx: SystemVerilogParser.Assert_property_statementContext
    ):
        from translator.asserts.assert_statement import (
            assertPropertyStatement2AplanImpl,
        )

        assertPropertyStatement2AplanImpl(self, ctx)

    def assertInBlock2Aplan(
        self,
        ctx: SystemVerilogParser.Simple_immediate_assert_statementContext,
        sv_structure: Structure,
    ):
        from translator.asserts.assert_statement import (
            assertInBlock2AplanImpl,
        )

        assertInBlock2AplanImpl(self, ctx, sv_structure)

    # =================================IF STATEMENT=====================================
    def ifStatement2Aplan(
        self,
        ctx: SystemVerilogParser.Conditional_statementContext,
        sv_structure: Structure,
        names_for_change: List[str],
    ):
        from translator.if_statement.if_statement import (
            ifStatement2AplanImpl,
        )

        ifStatement2AplanImpl(self, ctx, sv_structure, names_for_change)

    # ==================================================================================

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

    def loop2Aplan(
        self,
        ctx: (
            SystemVerilogParser.Loop_generate_constructContext
            | SystemVerilogParser.Loop_statementContext
        ),
        sv_structure: Structure,
    ):
        from translator.loops.loop import loop2AplanImpl

        loop2AplanImpl(self, ctx, sv_structure)

    def body2Aplan(self, ctx, sv_structure: Structure, name_space: ElementsTypes):
        names_for_change = []
        if ctx.getChildCount() == 0:
            return names_for_change
        for child in ctx.getChildren():
            # Assert handler
            if (
                type(child)
                is SystemVerilogParser.Simple_immediate_assert_statementContext
            ):
                self.assertInBlock2Aplan(child, sv_structure)
            # ---------------------------------------------------------------------------
            # Assign handler
            elif (
                type(child) is SystemVerilogParser.Variable_decl_assignmentContext
                or type(child) is SystemVerilogParser.Nonblocking_assignmentContext
                or type(child) is SystemVerilogParser.Net_assignmentContext
                or type(child) is SystemVerilogParser.Variable_assignmentContext
            ):
                self.blockAssignment2Aplan(child, sv_structure)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.For_variable_declarationContext:
                self.forDeclarationToApan(child)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.Data_declarationContext:
                data_type = child.data_type_or_implicit().getText()
                if len(data_type) > 0:
                    identifier = self.dataDecaration2Aplan(
                        child, False, sv_structure, name_space
                    )
                    if identifier is not None:
                        names_for_change.append(identifier)
                else:
                    names_for_change += self.body2Aplan(child, sv_structure, name_space)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.Loop_statementContext:
                self.loop2Aplan(child, sv_structure)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.Conditional_statementContext:
                self.ifStatement2Aplan(child, sv_structure, names_for_change)
            # ---------------------------------------------------------------------------
            else:
                names_for_change += self.body2Aplan(child, sv_structure, name_space)

        return names_for_change

    def generate2Aplan(self, ctx: SystemVerilogParser.Loop_generate_constructContext):
        from translator.structures.generate import generate2AplanImpl

        generate2AplanImpl(self, ctx)

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
        names_for_change = self.body2Aplan(
            always_body, always, ElementsTypes.ALWAYS_ELEMENT
        )
        for element in names_for_change:
            self.module.name_change.deleteElement(element)
        self.module.structures.addElement(always)
