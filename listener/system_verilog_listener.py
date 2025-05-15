from antlr4_verilog.systemverilog import (
    SystemVerilogParserListener,
    SystemVerilogParser,
)
from classes.case_stmt import CaseStmt
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.if_stmt import IfStmt
from classes.structure import Structure

from translator.loops.forever import foreverIteration2AplanImpl
from utils.utils import Counters_Object
from translator.declarations.class_declaration import classDeclaration2Aplan
from translator.declarations.interface_declaration import interfaceDeclaration2Aplan
from translator.declarations.module_declaration import moduleDeclaration2Aplan
from translator.declarations.package_declaration import packageDeclaration2Aplan
from translator.translator import (
    Translator,
)
from classes.module import Module
from classes.module import Module
from classes.module_call import ModuleCall


def body_run(ctx):
    if ctx.getChildCount() == 0:
        return
    for child in ctx.getChildren():
        print(type(child), child.getText())
        body_run(child)


class SVToAplanListener(SystemVerilogParserListener):
    def __init__(self, program, module_call: ModuleCall | None = None):
        from program.program import Program

        self.module: Module = None
        self.program: Program = program
        self.translator: Translator = Translator(None, program)
        self.module_call: ModuleCall | None = module_call

    # DECLARATIONS
    def enterInterface_declaration(
        self, ctx: SystemVerilogParser.Interface_declarationContext
    ):
        self.module = interfaceDeclaration2Aplan(ctx, self.program, self.module_call)
        self.translator = Translator(self.module, self.program)

    def enterModule_declaration(
        self, ctx: SystemVerilogParser.Module_declarationContext
    ):
        self.module = moduleDeclaration2Aplan(ctx, self.program, self.module_call)
        self.translator = Translator(
            self.module,
            self.program,
        )
        # body_run(ctx)

        self.translator.name_space_levels.append(
            Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER)
        )
        Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)

    def enterPackage_declaration(
        self, ctx: SystemVerilogParser.Package_declarationContext
    ):
        self.module = packageDeclaration2Aplan(ctx, self.program, self.module_call)
        self.translator = Translator(self.module, self.program)

    def enterClass_declaration(self, ctx: SystemVerilogParser.Class_declarationContext):
        self.module = classDeclaration2Aplan(ctx, self.program, self.module_call)
        self.translator = Translator(self.module, self.program)

    def enterSystem_tf_call(self, ctx: SystemVerilogParser.System_tf_callContext):
        self.translator.systemTFCall2Aplan(ctx)

    def exitGenvar_declaration(self, ctx):
        self.translator.genvarDeclaration2Aplan(ctx)

    def exitData_declaration(self, ctx):
        self.translator.dataDecaration2Aplan(ctx, True)

    def exitNet_declaration(self, ctx: SystemVerilogParser.Net_declarationContext):
        self.translator.netDeclaration2Aplan(ctx)

    def exitAnsi_port_declaration(self, ctx):
        self.translator.ansiPortDeclaration2Aplan(ctx)

    def exitTask_declaration(self, ctx: SystemVerilogParser.Task_declarationContext):
        self.translator.taskOrFunctionDeclaration2Aplan(ctx)

    def exitFunction_declaration(
        self, ctx: SystemVerilogParser.Function_declarationContext
    ):
        self.translator.taskOrFunctionDeclaration2Aplan(ctx)

    def exitClass_constructor_declaration(
        self, ctx: SystemVerilogParser.Class_constructor_declarationContext
    ):
        self.translator.taskOrFunctionDeclaration2Aplan(ctx)

    def exitPackage_import_declaration(
        self, ctx: SystemVerilogParser.Package_import_declarationContext
    ):
        self.translator.packageImport2Apan(ctx)

    # ASSIGNMENTS
    def exitNet_assignment(self, ctx):
        self.translator.netAssignment2Aplan(ctx)

    def exitVariable_decl_assignment(
        self, ctx: SystemVerilogParser.Variable_decl_assignmentContext
    ):
        if ctx.expression():

            self.translator.blockAssignment2Aplan(ctx)

    def exitNonblocking_assignment(
        self, ctx: SystemVerilogParser.Nonblocking_assignmentContext
    ):
        self.translator.blockAssignment2Aplan(ctx)

    def exitNet_assignment(self, ctx: SystemVerilogParser.Net_assignmentContext):
        self.translator.blockAssignment2Aplan(ctx)

    def exitVariable_assignment(
        self, ctx: SystemVerilogParser.Variable_assignmentContext
    ):
        self.translator.blockAssignment2Aplan(ctx)

    def exitOperator_assignment(
        self, ctx: SystemVerilogParser.Operator_assignmentContext
    ):
        self.translator.blockAssignment2Aplan(ctx)

    # PARAMETRS

    def exitLocal_parameter_declaration(
        self, ctx: SystemVerilogParser.Local_parameter_declarationContext
    ):
        self.translator.paramAssignment2Aplan(ctx, self.module_call)

    def exitParam_assignment(self, ctx: SystemVerilogParser.Param_assignmentContext):
        self.translator.paramAssignment2Aplan(ctx, self.module_call)

    def enterLoop_generate_construct(self, ctx):
        self.translator.generate2Aplan(ctx)

    def exitModule_instantiation(self, ctx):
        self.translator.moduleCall2Apan(ctx)

    # ALWAYS

    def enterAlways_construct(self, ctx: SystemVerilogParser.Always_constructContext):
        self.translator.always2Aplan(ctx)

    def exitAlways_construct(self, ctx: SystemVerilogParser.Always_constructContext):
        self.translator.removeLastStructPointer()

    # SEQUENCE BLOCK CONTEXT

    def exitSeq_block(self, ctx: SystemVerilogParser.Seq_blockContext):
        self.translator.ifSeqBlock2Aplan(ctx)

    # IF Statement
    def enterConditional_statement(
        self, ctx: SystemVerilogParser.Conditional_statementContext
    ):
        self.translator.ifStatement2Aplan(ctx)

    def exitConditional_statement(
        self, ctx: SystemVerilogParser.Conditional_statementContext
    ):
        self.translator.removeLastStructPointer()

    # COND PREDICATE
    def enterCond_predicate(self, ctx: SystemVerilogParser.Cond_predicateContext):
        self.translator.conditionalPredecate2Aplan(ctx)

    # CASE STATEMENT
    def enterCase_statement(self, ctx: SystemVerilogParser.Case_statementContext):
        self.translator.case2Aplan(ctx)

    def exitCase_statement(self, ctx: SystemVerilogParser.Case_statementContext):
        self.translator.removeLastStructPointer()

    # CASE ITEM
    def exitCase_item(self, ctx: SystemVerilogParser.Case_itemContext):
        self.translator.caseItem2Aplan(ctx)

    # CASE ITEM EXPRESSION
    def enterCase_item_expression(
        self, ctx: SystemVerilogParser.Case_item_expressionContext
    ):
        self.translator.caseItemExpr2Aplan(ctx)

    # ASSERT
    def exitAssert_property_statement(self, ctx):
        self.translator.assertPropertyStatement2Aplan(ctx)

    def exitSimple_immediate_assert_statement(
        self, ctx: SystemVerilogParser.Simple_immediate_assert_statementContext
    ):
        self.translator.assertInBlock2Aplan(ctx)

    # INITIAL
    def enterInitial_construct(self, ctx: SystemVerilogParser.Initial_constructContext):
        self.translator.initial2Aplan(ctx)

    def exitInitial_construct(self, ctx: SystemVerilogParser.Initial_constructContext):
        self.translator.removeLastStructPointer()

    # LOOP
    def enterLoop_statement(self, ctx: SystemVerilogParser.Loop_statementContext):
        self.translator.loop2Aplan(ctx)

    def exitLoop_statement(self, ctx: SystemVerilogParser.Loop_statementContext):
        self.translator.loopIteration2Aplan(ctx)
        self.translator.removeLastStructPointer()
