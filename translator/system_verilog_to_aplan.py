from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from classes.actions import Action
from classes.module_call import ModuleCall
from classes.node import NodeArray
from classes.structure import Structure, StructureArray
from classes.module import Module
from classes.element_types import ElementsTypes
from program.program import Program
from typing import Tuple, List


class SV2aplan:
    def __init__(self, module: Module, program: Program | None = None):
        self.module = module
        self.program: Program = program
        self.inside_the_task = False
        self.inside_the_function = False
        self.current_genvar_value: Tuple[str, int] | None = None
        self.structure_pointer_list: StructureArray = StructureArray()
        self.name_space_list: List[ElementsTypes] = []
        self.names_for_change = []
        self.condPredicate_List: List[
            Tuple[List[SystemVerilogParser.Cond_predicateContext], int]
        ] = []

    def removeLastNameChange(self):
        list_len = len(self.names_for_change)
        if list_len > 0:
            for element in self.names_for_change[list_len - 1]:
                self.module.name_change.deleteElement(element)
            element = self.names_for_change[list_len - 1]
            self.names_for_change.remove(element)

    def removeLastNameSpace(self):
        list_len = len(self.name_space_list)
        if list_len > 0:
            element = self.name_space_list[list_len - 1]
            self.name_space_list.remove(element)

    def removeLastStructPointer(self):
        if self.structure_pointer_list.getLen() > 0:
            self.structure_pointer_list.removeElementByIndex(
                self.structure_pointer_list.getLen() - 1
            )

    def removeLastCondPredicateList(self):
        list_len = len(self.condPredicate_List)
        if list_len > 0:
            element = self.condPredicate_List[list_len - 1]
            self.condPredicate_List.remove(element)

    def removeLastRelatedArrays(self):
        self.removeLastNameChange()
        self.removeLastNameSpace()
        self.removeLastStructPointer()

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
    ):
        from translator.assignments.in_block_assignments import (
            blockAssignment2AplanImpl,
        )
        blockAssignment2AplanImpl(self, ctx)

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
    def enumDecaration2Aplan(
        self,
        ctx: SystemVerilogParser.Data_declarationContext,
    ):
        from translator.declarations.struct_declaration import (
            typedefDecaration2AplanImpl,
        )

        return typedefDecaration2AplanImpl(self, ctx)

        # ---------------------------------------------------------------------------------

    def structDeclaration2Aplan(
        self,
        ctx: SystemVerilogParser.Data_declarationContext,
    ):
        from translator.declarations.struct_declaration import (
            structDeclaration2AplanImpl,
        )

        return structDeclaration2AplanImpl(self, ctx)

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

    def interfaceCall2Apan(
        self,
        ctx: SystemVerilogParser.Ansi_port_declarationContext,
    ):
        from translator.calls.interface_call import (
            interfaceCall2AplanImpl,
        )

        interfaceCall2AplanImpl(self, ctx)

    def taskCall2Aplan(
        self,
        ctx: SystemVerilogParser.Tf_callContext,
        sv_structure: Structure,
        destination_node_array: NodeArray | None = None,
    ):
        from translator.task_and_function.task_function import taskCall2AplanImpl

        taskCall2AplanImpl(self, ctx, sv_structure, destination_node_array)

    def systemTFCall2Aplan(
        self,
        ctx: SystemVerilogParser.System_tf_callContext,
        destination_node_array: NodeArray | None = None,
        sv_structure: Structure | None = None,
    ):
        from translator.task_and_function.build_in_functions.system_tf import (
            systemTF2AplanImpl,
        )

        systemTF2AplanImpl(self, ctx, destination_node_array, sv_structure)

    def methodCall2Aplan(
        self,
        ctx: SystemVerilogParser.Method_call_bodyContext,
        sv_structure: Structure,
        destination_node_array: NodeArray | None = None,
    ):
        from translator.task_and_function.task_function import methodCall2AplanImpl

        methodCall2AplanImpl(self, ctx, sv_structure, destination_node_array)

    def classNew2Aplan(
        self,
        ctx: SystemVerilogParser.Class_newContext,
        sv_structure: Structure,
        destination_node_array: NodeArray | None = None,
    ):
        from translator.task_and_function.task_function import classNew2AplanImpl

        classNew2AplanImpl(self, ctx, sv_structure, destination_node_array)

    def dinamycArrayNew2Aplan(
        self,
        ctx: SystemVerilogParser.Dynamic_array_newContext,
        sv_structure: Structure,
        destination_node_array: NodeArray | None = None,
    ):
        from translator.task_and_function.task_function import dinamycArrayNew2AplanImpl

        dinamycArrayNew2AplanImpl(self, ctx, sv_structure, destination_node_array)

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
    ):
        from translator.asserts.assert_statement import (
            assertInBlock2AplanImpl,
        )

        assertInBlock2AplanImpl(self, ctx)

    # =================================IF STATEMENT=====================================
    def ifStatement2Aplan(
        self,
        ctx: SystemVerilogParser.Conditional_statementContext,
    ):
        from translator.if_statement.if_statement import (
            ifStatement2AplanImpl,
        )

        ifStatement2AplanImpl(self, ctx)

    def conditionalPredecate2Aplan(
        self,
        ctx: SystemVerilogParser.Conditional_statementContext,
    ):
        from translator.if_statement.if_statement import (
            conditionalPredecate2AplanImpl,
        )

        conditionalPredecate2AplanImpl(self, ctx)

    # =================================CASE STATEMENT===================================

    def case2Aplan(
        self,
        ctx: SystemVerilogParser.Case_statementContext,
        sv_structure: Structure,
        names_for_change: List[str],
    ):
        from translator.case_statement.case_statement import caseStatement2AplanImpl

        caseStatement2AplanImpl(self, ctx, sv_structure, names_for_change)

    # =================================IDENTIFIER===================================

    def identifier2Aplan(
        self,
        ctx: SystemVerilogParser.IdentifierContext,
        destination_node_array: NodeArray,
    ):
        from translator.expression.expression_node import identifier2AplanImpl

        identifier2AplanImpl(self, ctx, destination_node_array)

    # =================================NUMBER===================================

    def number2Aplan(
        self,
        ctx: SystemVerilogParser.NumberContext,
        destination_node_array: NodeArray,
    ):
        from translator.expression.expression_node import number2AplanImpl

        number2AplanImpl(self, ctx, destination_node_array)

    # =================================BIT SELECTION==============================
    def bitSelection2Aplan(
        self,
        ctx: (
            SystemVerilogParser.Bit_selectContext
            | SystemVerilogParser.Constant_bit_selectContext
        ),
        destination_node_array: NodeArray,
    ):
        from translator.expression.expression_node import bitSelection2AplanImpl

        bitSelection2AplanImpl(self, ctx, destination_node_array)

    def unpackedDimention2Aplan(
        self,
        ctx: SystemVerilogParser.Unpacked_dimensionContext,
        destination_node_array: NodeArray,
    ):
        from translator.expression.expression_node import unpackedDimention2AplanImpl

        unpackedDimention2AplanImpl(self, ctx, destination_node_array)

    # =================================RANGE SELECTION============================
    def rangeSelection2Aplan(
        self,
        ctx: SystemVerilogParser.Bit_selectContext,
        destination_node_array: NodeArray,
    ):
        from translator.expression.expression_node import rangeSelection2AplanImpl

        rangeSelection2AplanImpl(self, ctx, destination_node_array)

    # =================================OPERATOR===================================

    def operator2Aplan(
        self,
        ctx: SystemVerilogParser.NumberContext,
        destination_node_array: NodeArray,
    ):
        from translator.expression.expression_node import operator2AplanImpl

        operator2AplanImpl(self, ctx, destination_node_array)
        # ==================================================================================

    def returnToAssign2Aplan(
        self,
        ctx: SystemVerilogParser.ExpressionContext,
        sv_structure: Structure | None = None,
    ):
        from translator.assignments.return_to_assignment import returnToAssign2AplanImpl

        returnToAssign2AplanImpl(self, ctx, sv_structure)

    # ==================================================================================
    def expression2Aplan(
        self,
        ctx: (
            SystemVerilogParser.Net_assignmentContext
            | SystemVerilogParser.Ansi_port_declarationContext
        ),
        element_type: ElementsTypes,
        sv_structure: Structure | None = None,
        name_space_element: ElementsTypes = ElementsTypes.NONE_ELEMENT,
        remove_association: bool = False,
    ) -> Tuple[Action, str, Tuple[int, int], bool]:
        from translator.expression.expression import expression2AplanImpl

        return expression2AplanImpl(
            self,
            ctx,
            element_type,
            sv_structure,
            name_space_element,
            remove_association,
        )

    # ==================================================================================

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

    def body2Aplan(
        self,
        ctx,
        sv_structure: Structure | None = None,
        name_space: ElementsTypes | None = None,
        destination_node_array: NodeArray | None = None,
    ):
        names_for_change = []
        if ctx is None:
            return names_for_change
        if ctx.getChildCount() == 0:
            return names_for_change
        for child in ctx.getChildren():
            # print(type(child), child.getText())
            # Assert handler
            # if (
            #    type(child)
            #    is SystemVerilogParser.Simple_immediate_assert_statementContext
            # ):
            #    self.assertInBlock2Aplan(child, sv_structure)
            # ---------------------------------------------------------------------------
            if type(child) is SystemVerilogParser.System_tf_callContext:
                self.systemTFCall2Aplan(child, destination_node_array, sv_structure)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.IdentifierContext:
                self.identifier2Aplan(child, destination_node_array)
            # ---------------------------------------------------------------------------
            elif (
                type(child) is SystemVerilogParser.Bit_selectContext
                or type(child) is SystemVerilogParser.Constant_bit_selectContext
            ):
                self.bitSelection2Aplan(child, destination_node_array)
            elif type(child) is SystemVerilogParser.Unpacked_dimensionContext:
                self.unpackedDimention2Aplan(child, destination_node_array)
            elif type(child) is SystemVerilogParser.Part_select_rangeContext:
                self.rangeSelection2Aplan(child, destination_node_array)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.NumberContext:
                self.number2Aplan(child, destination_node_array)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.Jump_statementContext:
                if child.RETURN and child.expression():
                    self.returnToAssign2Aplan(child.expression(), sv_structure)
                # ---------------------------------------------------------------------------
                # Assign handler
                """ elif (
                    type(child) is SystemVerilogParser.Variable_decl_assignmentContext
                    or type(child) is SystemVerilogParser.Nonblocking_assignmentContext
                    or type(child) is SystemVerilogParser.Net_assignmentContext
                    or type(child) is SystemVerilogParser.Variable_assignmentContext
                    or type(child) is SystemVerilogParser.Operator_assignmentContext
                    ):
                        self.blockAssignment2Aplan(child, sv_structure)
                """
            # ---------------------------------------------------------------------------
            # Task and function handler
            elif type(child) is SystemVerilogParser.Tf_callContext:
                self.taskCall2Aplan(child, sv_structure, destination_node_array)
            # ---------------------------------------------------------------------------
            # Dynamic_array new[] handler
            elif type(child) is SystemVerilogParser.Dynamic_array_newContext:
                self.dinamycArrayNew2Aplan(child, sv_structure, destination_node_array)
            # ---------------------------------------------------------------------------
            # Class new() handler
            elif type(child) is SystemVerilogParser.Class_newContext:
                self.classNew2Aplan(child, sv_structure, destination_node_array)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.Method_call_bodyContext:
                self.methodCall2Aplan(child, sv_structure, destination_node_array)
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
                    names_for_change += self.body2Aplan(
                        child, sv_structure, name_space, destination_node_array
                    )
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.Loop_statementContext:
                self.loop2Aplan(child, sv_structure)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.Case_statementContext:
                self.case2Aplan(child, sv_structure, names_for_change)
            # ---------------------------------------------------------------------------
            # elif type(child) is SystemVerilogParser.Conditional_statementContext:
            #    self.ifStatement2Aplan(child, sv_structure, names_for_change)
            # ---------------------------------------------------------------------------
            elif type(child) is Tree.TerminalNodeImpl:
                self.operator2Aplan(child, destination_node_array)
            else:
                names_for_change += self.body2Aplan(
                    child, sv_structure, name_space, destination_node_array
                )

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
