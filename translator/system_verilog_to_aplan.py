from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from classes.action_parametr import ActionParametrArray
from classes.action_precondition import ActionPreconditionArray
from classes.module_call import ModuleCall
from classes.structure import Structure
from classes.module import Module, ModuleArray
from classes.element_types import ElementsTypes
from classes.tasks import Task
from program.program import Program
from typing import Tuple, List


class SV2aplan:
    def __init__(self, module: Module, program: Program | None = None):
        self.module = module
        self.program: Program = program
        self.inside_the_task = False
        self.inside_the_function = False

    def extractSensetive(self, ctx):
        from translator.sensetive.sensetive import extractSensetiveImpl

        return extractSensetiveImpl(self, ctx)

    def prepareExpressionString(self, expression: str, expr_type: ElementsTypes):
        from translator.expression.expression import prepareExpressionStringImpl

        return prepareExpressionStringImpl(self, expression, expr_type)

    # ---------------------------------------------------------------------------------

    # =============================ASSIGNMENTS=========================================

    def netAssignment2Aplan(self, ctx: SystemVerilogParser.Net_assignmentContext):
        from translator.assignments.net_assignment import netAssignment2AplanImpl

        netAssignment2AplanImpl(self, ctx)

    # ---------------------------------------------------------------------------------
    def paramAssignment2Aplan(
        self,
        ctx: (
            SystemVerilogParser.Param_assignmentContext
            | SystemVerilogParser.Local_parameter_declarationContext
        ),
        module_call: ModuleCall,
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
            | SystemVerilogParser.Operator_assignmentContext
            | SystemVerilogParser.ExpressionContext
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
    def netDeclaration2Aplan(
        self,
        ctx: SystemVerilogParser.Net_declarationContext,
    ):
        from translator.declarations.net_declaration import (
            netDeclaration2AplanImpl,
        )

        netDeclaration2AplanImpl(self, ctx)

    # ---------------------------------------------------------------------------------

    def loopVarsToAplan(
        self,
        ctx: SystemVerilogParser.Loop_variablesContext,
        sv_structure: Structure,
    ):
        from translator.declarations.for_declaration import (
            loopVars2AplanImpl,
        )

        return loopVars2AplanImpl(self, ctx, sv_structure)

    # ---------------------------------------------------------------------------------

    def loopVarsDeclarationsToAplan(
        self,
        vars_names: List[str],
        source_intervals: List[Tuple[int, int]],
        sv_structure: Structure,
    ):
        from translator.declarations.for_declaration import (
            loopVarsDeclarations2AplanImpl,
        )

        return loopVarsDeclarations2AplanImpl(
            self, vars_names, source_intervals, sv_structure
        )

    # ---------------------------------------------------------------------------------

    def loopVarsToIteration2Aplan(
        self,
        vars_names: List[str],
        source_intervals: List[Tuple[int, int]],
        sv_structure: Structure,
    ):
        from translator.declarations.for_declaration import (
            loopVarsToIteration2AplanImpl,
        )

        return loopVarsToIteration2AplanImpl(
            self, vars_names, source_intervals, sv_structure
        )

    # ---------------------------------------------------------------------------------

    def loopVarsAndArrayIdentifierToCondition2Aplan(
        self,
        vars_names: List[str],
        ctx: SystemVerilogParser.Ps_or_hierarchical_array_identifierContext,
        sv_structure: Structure,
    ):
        from translator.declarations.for_declaration import (
            loopVarsAndArrayIdentifierToCondition2AplanImpl,
        )

        return loopVarsAndArrayIdentifierToCondition2AplanImpl(
            self, vars_names, ctx, sv_structure
        )

    # ---------------------------------------------------------------------------------

    def forInitialization2Apan(
        self,
        ctx: SystemVerilogParser.For_initializationContext,
        sv_structure: Structure,
    ):
        from translator.declarations.for_declaration import (
            forInitialization2ApanImpl,
        )

        return forInitialization2ApanImpl(self, ctx, sv_structure)

    # ---------------------------------------------------------------------------------

    def forDeclaration2Apan(
        self,
        ctx: SystemVerilogParser.For_variable_declarationContext,
        sv_structure: Structure,
    ):
        from translator.declarations.for_declaration import (
            forDeclaration2ApanImpl,
        )

        forDeclaration2ApanImpl(self, ctx, sv_structure)

    # ====================================CALLS=========================================
    def moduleCall2Apan(
        self,
        ctx: SystemVerilogParser.Module_instantiationContext,
    ):
        from translator.calls.module_call import (
            moduleCall2AplanImpl,
        )

        moduleCall2AplanImpl(self, ctx)

    def packageImport2Apan(
        self,
        ctx: SystemVerilogParser.Package_import_declarationContext,
    ):
        from translator.import_stmt.package_import import (
            packageImport2ApanImpl,
        )

        packageImport2ApanImpl(self, ctx)

    def taskCall2Aplan(
        self, ctx: SystemVerilogParser.Tf_callContext, sv_structure: Structure
    ):
        from translator.task_and_function.task_function import taskCall2AplanImpl

        taskCall2AplanImpl(self, ctx, sv_structure)

    def funtionCall2Aplan(
        self,
        task: Task,
        sv_structure: Structure,
        function_result_var: str | None,
        function_call: str,
        source_interval: Tuple[int, int],
        object_pointer: str | None,
    ):
        from translator.task_and_function.task_function import funtionCall2AplanImpl

        funtionCall2AplanImpl(
            self,
            task,
            sv_structure,
            function_result_var,
            function_call,
            source_interval,
            object_pointer,
        )

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

    # =================================CASE STATEMENT===================================

    def case2Aplan(
        self,
        ctx: SystemVerilogParser.Case_statementContext,
        sv_structure: Structure,
        names_for_change: List[str],
    ):
        from translator.case_statement.case_statement import caseStatement2AplanImpl

        caseStatement2AplanImpl(self, ctx, sv_structure, names_for_change)

    # ==================================================================================
    def expression2Aplan(
        self,
        input: str | List[str],
        element_type: ElementsTypes,
        source_interval: Tuple[int, int],
        input_parametrs: (
            Tuple[
                str | None, ActionParametrArray | None, ActionPreconditionArray | None
            ]
            | None
        ) = None,
        sv_structure: Structure | None = None,
    ):
        from translator.expression.expression import expression2AplanImpl

        return expression2AplanImpl(
            self,
            input,
            element_type,
            source_interval,
            input_parametrs,
            sv_structure,
        )

    def loop2Aplan(
        self,
        ctx: (
            SystemVerilogParser.Loop_generate_constructContext
            | SystemVerilogParser.Loop_statementContext
        ),
        sv_structure: Structure,
    ):
        from translator.loops.loop import loop2AplanImpl
        from translator.loops.repeat import repeat2AplanImpl
        from translator.loops.forever import forever2AplanImpl

        if ctx.REPEAT():
            repeat2AplanImpl(self, ctx, sv_structure)
        elif ctx.FOREVER():
            forever2AplanImpl(self, ctx, sv_structure)
        else:
            loop2AplanImpl(self, ctx, sv_structure)

    def body2Aplan(self, ctx, sv_structure: Structure, name_space: ElementsTypes):
        names_for_change = []
        if ctx is None:
            return names_for_change
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
            elif type(child) is SystemVerilogParser.Jump_statementContext:
                if child.RETURN:
                    self.blockAssignment2Aplan(child.expression(), sv_structure)
            # ---------------------------------------------------------------------------
            # Assign handler
            elif (
                type(child) is SystemVerilogParser.Variable_decl_assignmentContext
                or type(child) is SystemVerilogParser.Nonblocking_assignmentContext
                or type(child) is SystemVerilogParser.Net_assignmentContext
                or type(child) is SystemVerilogParser.Variable_assignmentContext
                or type(child) is SystemVerilogParser.Operator_assignmentContext
            ):
                self.blockAssignment2Aplan(child, sv_structure)
            # ---------------------------------------------------------------------------
            # Task and function handler
            elif type(child) is SystemVerilogParser.Tf_callContext:
                self.taskCall2Aplan(child, sv_structure)

            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.For_variable_declarationContext:
                self.forDeclaration2Apan(child, sv_structure)
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
            elif type(child) is SystemVerilogParser.Case_statementContext:
                self.case2Aplan(child, sv_structure, names_for_change)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.Conditional_statementContext:
                self.ifStatement2Aplan(child, sv_structure, names_for_change)
            # ---------------------------------------------------------------------------
            elif type(child) is Tree.TerminalNodeImpl:
                pass
            else:
                names_for_change += self.body2Aplan(child, sv_structure, name_space)

        return names_for_change

    def generate2Aplan(self, ctx: SystemVerilogParser.Loop_generate_constructContext):
        from translator.structures.generate import generate2AplanImpl

        generate2AplanImpl(self, ctx)

    def always2Aplan(self, ctx: SystemVerilogParser.Always_constructContext):
        from translator.structures.always import always2AplanImpl

        always2AplanImpl(self, ctx)

    def initial2Aplan(self, ctx: SystemVerilogParser.Initial_constructContext):
        from translator.structures.initial import initital2AplanImpl

        initital2AplanImpl(self, ctx)

    def taskOrFunctionDeclaration2Aplan(
        self,
        ctx: (
            SystemVerilogParser.Task_declarationContext
            | SystemVerilogParser.Function_declarationContext
            | SystemVerilogParser.Class_constructor_declarationContext
        ),
    ):
        from translator.task_and_function.task_function import (
            taskOrFunctionDeclaration2AplanImpl,
        )

        taskOrFunctionDeclaration2AplanImpl(self, ctx)
