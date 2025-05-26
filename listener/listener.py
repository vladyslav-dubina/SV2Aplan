from antlr4_verilog.systemverilog import (
    SystemVerilogParserListener,
    SystemVerilogParser,
)

from classes.counters import CounterTypes
from classes.module import Module
from classes.module_call import ModuleCall
from translator.translator import Translator
from utils.utils import Counters_Object


class SVToAplanListener(SystemVerilogParserListener):

    translator = Translator()

    @property
    def module(self) -> Module:
        return self.translator._module

    def __init__(self, module_call: ModuleCall | None = None):
        self.translator.module_call = module_call

    # =========================================================================================
    # DECLARATIONS
    # =========================================================================================

    def enterInterface_declaration(
        self, ctx: SystemVerilogParser.Interface_declarationContext
    ):
        self.translator.translate("interface_decl", ctx)

    def enterModule_declaration(
        self, ctx: SystemVerilogParser.Module_declarationContext
    ):
        self.translator.translate("module_decl", ctx)
        # body_run(ctx)
        Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)  # ???

    def enterPackage_declaration(
        self, ctx: SystemVerilogParser.Package_declarationContext
    ):
        self.translator.translate("package_decl", ctx)

    def enterClass_declaration(self, ctx: SystemVerilogParser.Class_declarationContext):
        self.translator.translate("class_decl", ctx)

    def exitGenvar_declaration(
        self, ctx: SystemVerilogParser.Genvar_declarationContext
    ):
        self.translator.translate("genvar_decl", ctx)

    def exitData_declaration(self, ctx: SystemVerilogParser.Data_declarationContext):
        self.translator.translate("data_decl", ctx)

    def exitNet_declaration(self, ctx: SystemVerilogParser.Net_declarationContext):
        self.translator.translate("net_decl", ctx)

    def exitAnsi_port_declaration(
        self, ctx: SystemVerilogParser.Ansi_port_declarationContext
    ):
        self.translator.translate("ansi_port_decl", ctx)

    def exitPackage_import_declaration(
        self, ctx: SystemVerilogParser.Package_import_declarationContext
    ):
        self.translator.translate("package_import_decl", ctx)

    def exitClass_constructor_declaration(
        self, ctx: SystemVerilogParser.Class_constructor_declarationContext
    ):
        self.translator.translate("task_body_decl", ctx)

    def exitTask_declaration(self, ctx: SystemVerilogParser.Task_declarationContext):
        self.translator.translate("task_body_decl", ctx.task_body_declaration())

    def exitFunction_declaration(
        self, ctx: SystemVerilogParser.Function_declarationContext
    ):
        self.translator.translate("task_body_decl", ctx.function_body_declaration())

    # =========================================================================================
    # CALLS
    # =========================================================================================
    def enterSystem_tf_call(self, ctx: SystemVerilogParser.System_tf_callContext):
        self.translator.translate("system_task_call", ctx)

    def exitModule_instantiation(
        self, ctx: SystemVerilogParser.Module_instantiationContext
    ):
        self.translator.translate("module_call", ctx)

    # =========================================================================================
    # ASSIGNMENTS
    # =========================================================================================
    # def exitNet_assignment(self, ctx):
    #    self.translator.translate("net_assign", ctx)

    def exitNet_assignment(self, ctx: SystemVerilogParser.Net_assignmentContext):
        self.translator.translate("in_block_assign", ctx)

    def exitVariable_decl_assignment(
        self, ctx: SystemVerilogParser.Variable_decl_assignmentContext
    ):
        if ctx.expression():
            self.translator.translate("in_block_assign", ctx)

    def exitNonblocking_assignment(
        self, ctx: SystemVerilogParser.Nonblocking_assignmentContext
    ):
        self.translator.translate("in_block_assign", ctx)

    def exitVariable_assignment(
        self, ctx: SystemVerilogParser.Variable_assignmentContext
    ):
        self.translator.translate("in_block_assign", ctx)

    def exitOperator_assignment(
        self, ctx: SystemVerilogParser.Operator_assignmentContext
    ):
        self.translator.translate("in_block_assign", ctx)

    # =========================================================================================
    # PARAMETRS
    # =========================================================================================
    def exitLocal_parameter_declaration(
        self, ctx: SystemVerilogParser.Local_parameter_declarationContext
    ):
        self.translator.translate("params_assign", ctx)

    def exitParam_assignment(self, ctx: SystemVerilogParser.Param_assignmentContext):
        self.translator.translate("params_assign", ctx)

    def enterLoop_generate_construct(
        self, ctx: SystemVerilogParser.Loop_generate_constructContext
    ):
        self.translator.translate("generate_struct", ctx)

    def enterLoop_generate_construct(
        self, ctx: SystemVerilogParser.Loop_generate_constructContext
    ):
        self.translator.removeLastStructPointer()

    # =========================================================================================
    # ALWAYS
    # =========================================================================================
    def enterAlways_construct(self, ctx: SystemVerilogParser.Always_constructContext):
        self.translator.translate("alaways_struct", ctx)

    def exitAlways_construct(self, ctx: SystemVerilogParser.Always_constructContext):
        self.translator.removeLastStructPointer()

    # =========================================================================================
    # IF Statement
    # =========================================================================================
    def enterConditional_statement(
        self, ctx: SystemVerilogParser.Conditional_statementContext
    ):
        self.translator.translate("if_stmt", ctx)

    def exitConditional_statement(
        self, ctx: SystemVerilogParser.Conditional_statementContext
    ):
        self.translator.removeLastStructPointer()

    # =========================================================================================
    # COND PREDICATE
    # =========================================================================================
    def enterCond_predicate(self, ctx: SystemVerilogParser.Cond_predicateContext):
        self.translator.translate("if_cond_predicate", ctx)

    # =========================================================================================
    # SEQUENCE BLOCK CONTEXT
    # =========================================================================================
    def exitSeq_block(self, ctx: SystemVerilogParser.Seq_blockContext):
        self.translator.translate("if_seq_block", ctx)

    # =========================================================================================
    # CASE STATEMENT
    # =========================================================================================
    def enterCase_statement(self, ctx: SystemVerilogParser.Case_statementContext):
        self.translator.translate("case_stmt", ctx)

    def exitCase_statement(self, ctx: SystemVerilogParser.Case_statementContext):
        self.translator.removeLastStructPointer()

    # =========================================================================================
    # CASE ITEM
    # =========================================================================================
    def exitCase_item(self, ctx: SystemVerilogParser.Case_itemContext):
        self.translator.translate("case_item", ctx)

    # =========================================================================================
    # CASE ITEM EXPRESSION
    # =========================================================================================
    def enterCase_item_expression(
        self, ctx: SystemVerilogParser.Case_item_expressionContext
    ):
        self.translator.translate("case_item_expr", ctx)

    # =========================================================================================
    # ASSERT
    # =========================================================================================
    def exitAssert_property_statement(self, ctx):
        self.translator.translate("assert_property", ctx)

    def exitSimple_immediate_assert_statement(
        self, ctx: SystemVerilogParser.Simple_immediate_assert_statementContext
    ):
        self.translator.translate("assert_block", ctx)

    # =========================================================================================
    # INITIAL
    # =========================================================================================
    def enterInitial_construct(self, ctx: SystemVerilogParser.Initial_constructContext):
        self.translator.translate("initial", ctx)

    def exitInitial_construct(self, ctx: SystemVerilogParser.Initial_constructContext):
        self.translator.removeLastStructPointer()

    # =========================================================================================
    # LOOP
    # =========================================================================================
    def enterLoop_statement(self, ctx: SystemVerilogParser.Loop_statementContext):
        self.translator.translate("loop", ctx)

    def exitLoop_statement(self, ctx: SystemVerilogParser.Loop_statementContext):
        self.translator.translate("loop_iteration", ctx)
        self.translator.removeLastStructPointer()
