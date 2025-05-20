from antlr4_verilog.systemverilog import (
    SystemVerilogParserListener,
    SystemVerilogParser,
)

from classes.counters import CounterTypes
from classes.module_call import ModuleCall
from translator.translator import Translator
from utils.utils import Counters_Object


class SVToAplanListener(SystemVerilogParserListener):

    translator = Translator()

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
        self.translator.taskOrFunctionDeclaration2Aplan(ctx)

    def exitTask_declaration(self, ctx: SystemVerilogParser.Task_declarationContext):
        self.translator.taskOrFunctionDeclaration2Aplan(ctx)

    def exitFunction_declaration(
        self, ctx: SystemVerilogParser.Function_declarationContext
    ):
        self.translator.taskOrFunctionDeclaration2Aplan(ctx)

    # =========================================================================================
    # CALLS
    # =========================================================================================
    def enterSystem_tf_call(self, ctx: SystemVerilogParser.System_tf_callContext):
        self.translator.systemTFCall2Aplan(ctx)

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
    # SEQUENCE BLOCK CONTEXT
    # =========================================================================================
    def exitSeq_block(self, ctx: SystemVerilogParser.Seq_blockContext):
        self.translator.ifSeqBlock2Aplan(ctx)

    # =========================================================================================
    # IF Statement
    # =========================================================================================
    def enterConditional_statement(
        self, ctx: SystemVerilogParser.Conditional_statementContext
    ):
        self.translator.ifStatement2Aplan(ctx)

    def exitConditional_statement(
        self, ctx: SystemVerilogParser.Conditional_statementContext
    ):
        self.translator.removeLastStructPointer()
