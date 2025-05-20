from os import name
from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from classes.actions import Action
from classes.case_stmt import CaseStmt
from classes.counters import CounterTypes
from classes.if_stmt import IfStmt
from classes.loop_stmt import ForeverStmt, LoopStmt, WhileStmt
from classes.module_call import ModuleCall
from classes.node import NodeArray
from classes.parametrs import ParametrArray
from classes.protocols import BodyElement
from classes.structure import Structure, StructureArray
from classes.module import Module
from classes.element_types import ElementsTypes
from program.program import Program
from typing import Literal, Tuple, List, overload
from translator.classes.assignments.in_block import InBlockAssignmentTranslator
from translator.classes.assignments.net import NetAssignmentTranslator
from translator.classes.calls.interface import InterfaceCallTranslator
from translator.classes.calls.module import ModuleCallTranslator
from translator.classes.declarations.ansi_port import AnsiPortDeclTranslator
from translator.classes.declarations.data import DataDeclTranslator
from translator.classes.declarations.genvar import GenvarDeclTranslator
from translator.classes.declarations.interface import (
    InterfaceDeclTranslator,
)
from translator.classes.declarations.module import (
    Module_Translator,
    ModuleDeclTranslator,
)
from translator.classes.declarations.net import NewDeclTranslator
from translator.classes.declarations.object import ObjectDeclTranslator
from translator.classes.declarations.package import PackageDeclTranslator
from translator.classes.declarations.package_import import PackageImportDeclTranslator
from translator.classes.declarations.struct import StructDeclTranslator
from translator.classes.expressions.expression import ExpressionTranslator
from translator.classes.parameters.parameters_assignment import (
    ParametrsAssignmentTranslator,
)
from translator.classes.structures.always import AlwaysStructureTranslator
from translator.classes.structures.generate import GenerateStructTranslator
from utils.utils import Counters_Object


class Module_Translator2:
    def __init__(self, module: Module, program: Program | None = None):
        self.module = module
        self.program: Program = program

        self.current_genvar_value: Tuple[str, int] | None = None

    def getProtocolParams(self):
        protocol_params = None
        if self.inside_the_task == True:
            task = self.module.tasks.getLastTask()
            if task is not None:
                protocol_params = task.parametrs
        return protocol_params

    def removeLastStructPointer(self):
        if self.structure_pointer_list.getLen() > 0:
            self.structure_pointer_list.removeElementByIndex(
                self.structure_pointer_list.getLen() - 1
            )
            # Counters_Object.decrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)

    def createStatement(
        self,
        name,
        element_type: ElementsTypes,
        sensetive: str | None = None,
        counter_type: CounterTypes = CounterTypes.UNIQ_NAMES_COUNTER,
    ):
        sv_structure: Structure | None = self.structure_pointer_list.getLastElement()

        if sv_structure:
            protocol_params = self.getProtocolParams()
            beh_index = sv_structure.getLastBehaviorIndex()
            if beh_index is not None:
                if element_type == ElementsTypes.FOREVER_ELEMENT:
                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(
                            identifier="Sensetive({0}_{1}, {2})".format(
                                name,
                                Counters_Object.getCounter(counter_type),
                                sensetive,
                            ),
                            element_type=ElementsTypes.PROTOCOL_ELEMENT,
                            parametrs=protocol_params,
                        )
                    )
                else:
                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(
                            identifier="{0}_{1}".format(
                                name,
                                Counters_Object.getCounter(counter_type),
                            ),
                            element_type=ElementsTypes.PROTOCOL_ELEMENT,
                            parametrs=protocol_params,
                        )
                    )

            tmp: ParametrArray = ParametrArray()
            if (self.inside_the_task or self.inside_the_function) is False:
                if sv_structure.parametrs is not None:
                    tmp += sv_structure.parametrs
                if protocol_params is not None:
                    tmp += protocol_params
            else:
                tmp = protocol_params

            if element_type == ElementsTypes.CASE_STATEMENT_ELEMENT:
                struct = CaseStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )

            elif element_type == ElementsTypes.IF_STATEMENT_ELEMENT:
                struct = IfStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )
            elif element_type == ElementsTypes.FOREVER_ELEMENT:
                struct = ForeverStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )

            elif element_type == ElementsTypes.WHILE_ELEMENT:
                struct = WhileStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )

            elif element_type == ElementsTypes.LOOP_ELEMENT:
                struct = LoopStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )

            else:
                struct = Structure(
                    name,
                    (0, 0),
                    element_type,
                    Counters_Object.getCounter(counter_type),
                )

            struct.addInitProtocol()
            struct.parametrs = tmp
            struct.inside_the_task = self.inside_the_task or self.inside_the_function
            sv_structure.behavior.append(struct)
            self._structure_pointer_list.addElement(struct)
            Counters_Object.incrieseCounter(counter_type)

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
    ):
        from translator.declarations.data_declaration import dataDecaration2AplanImpl

        return dataDecaration2AplanImpl(self, ctx, listener, sv_structure)

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
    def loopIteration2Aplan(
        self,
        ctx: SystemVerilogParser.Loop_statementContext,
    ):
        from translator.loops.forever import (
            foreverIteration2AplanImpl,
        )

        if ctx.FOREVER():
            foreverIteration2AplanImpl(self, ctx)
        elif ctx.REPEAT():
            return

    # else:
    #    loop2AplanImpl(self, ctx)

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

    def ifSeqBlock2Aplan(self, ctx: SystemVerilogParser.Seq_blockContext):
        from translator.if_statement.if_statement import (
            ifSeqBlock2AplanImpl,
        )

        return ifSeqBlock2AplanImpl(self, ctx)

    # =================================CASE STATEMENT===================================

    def case2Aplan(
        self,
        ctx: SystemVerilogParser.Case_statementContext,
    ):
        from translator.case_statement.case_statement import caseStatement2AplanImpl

        caseStatement2AplanImpl(self, ctx)

    # =================================CASE ITEM EXPR ===================================

    def caseItemExpr2Aplan(
        self,
        ctx: SystemVerilogParser.Case_item_expressionContext,
    ):
        from translator.case_statement.case_statement import caseItemExpr2AplanImpl

        caseItemExpr2AplanImpl(self, ctx)

    # =================================CASE Item ===================================

    def caseItem2Aplan(
        self,
        ctx: SystemVerilogParser.Case_itemContext,
    ):
        from translator.case_statement.case_statement import caseItem2AplanImpl

        caseItem2AplanImpl(self, ctx)

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
        remove_association: bool = False,
    ) -> Tuple[Action, str, Tuple[int, int], bool]:
        from translator.expression.expression import expression2AplanImpl

        return expression2AplanImpl(
            self,
            ctx,
            element_type,
            sv_structure,
            remove_association,
        )

    # ==================================================================================

    def loop2Aplan(
        self,
        ctx: (
            SystemVerilogParser.Loop_generate_constructContext
            | SystemVerilogParser.Loop_statementContext
        ),
    ):
        from translator.loops.loop import loop2AplanImpl
        from translator.loops.repeat import repeat2AplanImpl
        from translator.loops.forever import forever2AplanImpl
        from translator.loops._while import while2AplanImpl

        if ctx.REPEAT():
            repeat2AplanImpl(self, ctx)
        elif ctx.FOREVER():
            forever2AplanImpl(self, ctx)
        elif ctx.WHILE():
            while2AplanImpl(self, ctx)
        else:
            loop2AplanImpl(self, ctx)

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


from program.program import Program


class Translator:
    module_call: ModuleCall | None = None
    _module: Module | None = None
    _structure_pointer_list: StructureArray = StructureArray()
    _inside_the_task = False
    _inside_the_function = False
    _cache = {}

    TranslatorName = Literal[
        "interface_decl",
        "module_decl",
        "package_decl",
        "genvar_decl",
        "struct_decl",
        "data_decl",
        "net_decl",
        "obj_decl",
        "ansi_port_decl",
        "package_import_decl",
        "expr",
        "interface_call",
        "module_call",
        "net_assign",
        "in_block_assign",
        "params_assign",
        "generate_struct",
        "alaways_struct",
    ]

    _translators: dict[str, type] = {
        "interface_decl": InterfaceDeclTranslator,
        "module_decl": ModuleDeclTranslator,
        "package_decl": PackageDeclTranslator,
        "genvar_decl": GenvarDeclTranslator,
        "struct_decl": StructDeclTranslator,
        "data_decl": DataDeclTranslator,
        "net_decl": NewDeclTranslator,
        "obj_decl": ObjectDeclTranslator,
        "ansi_port_decl": AnsiPortDeclTranslator,
        "package_import_decl": PackageImportDeclTranslator,
        "expr": ExpressionTranslator,
        "interface_call": InterfaceCallTranslator,
        "module_call": ModuleCallTranslator,
        "net_assign": NetAssignmentTranslator,
        "in_block_assign": InBlockAssignmentTranslator,
        "params_assign": ParametrsAssignmentTranslator,
        "generate_struct": GenerateStructTranslator,
        "alaways_struct": AlwaysStructureTranslator,
    }

    def __init__(self):

        pass

    @overload
    def getTranslator(
        self, key: Literal["interface_decl"]
    ) -> InterfaceDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["module_decl"]) -> ModuleDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["package_decl"]) -> PackageDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["genvar_decl"]) -> GenvarDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["struct_decl"]) -> StructDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["data_decl"]) -> DataDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["net_decl"]) -> NewDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["obj_decl"]) -> ObjectDeclTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["ansi_port_decl"]
    ) -> AnsiPortDeclTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["package_import_decl"]
    ) -> PackageImportDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["expr"]) -> ExpressionTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["interface_call"]
    ) -> InterfaceCallTranslator: ...
    @overload
    def getTranslator(self, key: Literal["net_assign"]) -> NetAssignmentTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["in_block_assign"]
    ) -> InBlockAssignmentTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["params_assign"]
    ) -> ParametrsAssignmentTranslator: ...
    @overload
    def getTranslator(self, key: Literal["module_call"]) -> ModuleCallTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["generate_struct"]
    ) -> GenerateStructTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["alaways_struct"]
    ) -> AlwaysStructureTranslator: ...

    def getTranslator(self, key: TranslatorName):
        cls = self._selectTranlator(name)
        if key not in self._cache:
            self._cache[key] = cls(self)
        return self._cache[key]

    def _selectTranlator(self, name: TranslatorName):
        if name not in self._translators:
            raise ValueError(f"Unknown translator name: {name}")
        return self._translators[name]

    def translate(self, trnslt_name: TranslatorName, *args, **kwargs):
        translator = self.getTranslator(trnslt_name)
        return translator.translate(*args, **kwargs)

    def getProtocolParams(self):
        protocol_params = None
        if self._inside_the_task == True:
            task = self._module.tasks.getLastTask()
            if task is not None:
                protocol_params = task.parametrs
        return protocol_params

    def getLastNameSpaceLevel(self):

        struct: Structure | None = self._structure_pointer_list.getLastElement()
        if struct:
            return struct.number
        else:
            return self._module.number

    def removeLastStructPointer(self):
        if self._structure_pointer_list.getLen() > 0:
            self._structure_pointer_list.removeElementByIndex(
                self._structure_pointer_list.getLen() - 1
            )
            # Counters_Object.decrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)

    def body2Aplan(
        self,
        ctx,
        sv_structure: Structure | None = None,
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

            # ---------------------------------------------------------------------------
            # elif type(child) is SystemVerilogParser.Loop_statementContext:
            #     self.loop2Aplan(child, sv_structure)
            # ---------------------------------------------------------------------------
            elif type(child) is Tree.TerminalNodeImpl:
                self.operator2Aplan(child, destination_node_array)
            # ---------------------------------------------------------------------------
            else:
                names_for_change += self.body2Aplan(
                    child, sv_structure, destination_node_array
                )

        return names_for_change

    def createStatement(
        self,
        name,
        element_type: ElementsTypes,
        sensetive: str | None = None,
        counter_type: CounterTypes = CounterTypes.UNIQ_NAMES_COUNTER,
    ):
        sv_structure: Structure | None = self._structure_pointer_list.getLastElement()

        if sv_structure:
            protocol_params = self.getProtocolParams()
            beh_index = sv_structure.getLastBehaviorIndex()
            if beh_index is not None:
                if element_type == ElementsTypes.FOREVER_ELEMENT:
                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(
                            identifier="Sensetive({0}_{1}, {2})".format(
                                name,
                                Counters_Object.getCounter(counter_type),
                                sensetive,
                            ),
                            element_type=ElementsTypes.PROTOCOL_ELEMENT,
                            parametrs=protocol_params,
                        )
                    )
                else:
                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(
                            identifier="{0}_{1}".format(
                                name,
                                Counters_Object.getCounter(counter_type),
                            ),
                            element_type=ElementsTypes.PROTOCOL_ELEMENT,
                            parametrs=protocol_params,
                        )
                    )

            tmp: ParametrArray = ParametrArray()
            if (self._inside_the_task or self._inside_the_function) is False:
                if sv_structure.parametrs is not None:
                    tmp += sv_structure.parametrs
                if protocol_params is not None:
                    tmp += protocol_params
            else:
                tmp = protocol_params

            if element_type == ElementsTypes.CASE_STATEMENT_ELEMENT:
                struct = CaseStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )

            elif element_type == ElementsTypes.IF_STATEMENT_ELEMENT:
                struct = IfStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )
            elif element_type == ElementsTypes.FOREVER_ELEMENT:
                struct = ForeverStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )

            elif element_type == ElementsTypes.WHILE_ELEMENT:
                struct = WhileStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )

            elif element_type == ElementsTypes.LOOP_ELEMENT:
                struct = LoopStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )

            else:
                struct = Structure(
                    name,
                    (0, 0),
                    element_type,
                    Counters_Object.getCounter(counter_type),
                )

            struct.addInitProtocol()
            struct.parametrs = tmp
            struct.inside_the_task = self._inside_the_task or self._inside_the_function
            sv_structure.behavior.append(struct)
            self._structure_pointer_list.addElement(struct)
            Counters_Object.incrieseCounter(counter_type)
