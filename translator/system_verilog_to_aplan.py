from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from classes.action_parametr import ActionParametrArray
from classes.action_precondition import ActionPreconditionArray
from classes.module_call import ModuleCall
from classes.structure import Structure
from classes.module import Module
from classes.element_types import ElementsTypes
from program.program import Program
from typing import Tuple, List


class SV2aplan:
    def __init__(self, module: Module):
        self.module = module

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
        input_parametrs: (
            Tuple[
                str | None, ActionParametrArray | None, ActionPreconditionArray | None
            ]
            | None
        ) = None,
    ):
        from translator.expression.expression import expression2AplanImpl

        return expression2AplanImpl(
            self, input, element_type, source_interval, input_parametrs
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

    def always2Aplan(self, ctx: SystemVerilogParser.Always_constructContext):
        from translator.structures.always import always2AplanImpl

        always2AplanImpl(self, ctx)
