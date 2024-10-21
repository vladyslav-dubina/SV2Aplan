from antlr4_verilog.systemverilog import (
    SystemVerilogParserListener,
    SystemVerilogParser,
)
from classes.counters import CounterTypes
from classes.structure import Structure, StructureArray
from utils.utils import Counters_Object
from translator.declarations.class_declaration import classDeclaration2Aplan
from translator.declarations.interface_declaration import interfaceDeclaration2Aplan
from translator.declarations.module_declaration import moduleDeclaration2Aplan
from translator.declarations.package_declaration import packageDeclaration2Aplan
from translator.if_statement.if_statement import (
    getLastCondPredicateList,
    getProtocolParams,
    removeFirstCondPredicate,
)
from translator.system_verilog_to_aplan import (
    SV2aplan,
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


class SVListener(SystemVerilogParserListener):
    def __init__(self, program, module_call: ModuleCall | None = None):
        from program.program import Program

        self.module: Module = None
        self.program: Program = program
        self.sv2aplan: SV2aplan = SV2aplan(None, program)
        self.module_call: ModuleCall | None = module_call

    # DECLARATIONS
    def enterInterface_declaration(
        self, ctx: SystemVerilogParser.Interface_declarationContext
    ):
        self.module = interfaceDeclaration2Aplan(ctx, self.program, self.module_call)
        self.sv2aplan = SV2aplan(self.module, self.program)

    def enterModule_declaration(
        self, ctx: SystemVerilogParser.Module_declarationContext
    ):
        self.module = moduleDeclaration2Aplan(ctx, self.program, self.module_call)
        self.sv2aplan = SV2aplan(
            self.module,
            self.program,
        )

    def enterPackage_declaration(
        self, ctx: SystemVerilogParser.Package_declarationContext
    ):
        self.module = packageDeclaration2Aplan(ctx, self.program, self.module_call)
        self.sv2aplan = SV2aplan(self.module, self.program)

    def enterClass_declaration(self, ctx: SystemVerilogParser.Class_declarationContext):
        self.module = classDeclaration2Aplan(ctx, self.program, self.module_call)
        self.sv2aplan = SV2aplan(self.module, self.program)

    # def enterSystem_tf_call(
    #     self, ctx: SystemVerilogParser.System_tf_callContext
    # ):
    #     self.sv2aplan.systemTFCall2Aplan(ctx)

    def exitGenvar_declaration(self, ctx):
        self.sv2aplan.genvarDeclaration2Aplan(ctx)

    def exitData_declaration(self, ctx):
        self.sv2aplan.dataDecaration2Aplan(ctx, True)

    def exitNet_declaration(self, ctx: SystemVerilogParser.Net_declarationContext):
        self.sv2aplan.netDeclaration2Aplan(ctx)

    def exitAnsi_port_declaration(self, ctx):
        self.sv2aplan.ansiPortDeclaration2Aplan(ctx)

    # ASSIGNMENTS
    def exitNet_assignment(self, ctx):
        self.sv2aplan.netAssignment2Aplan(ctx)

    def exitVariable_decl_assignment(
        self, ctx: SystemVerilogParser.Variable_decl_assignmentContext
    ):
        if ctx.expression():

            self.sv2aplan.blockAssignment2Aplan(ctx)

    def exitNonblocking_assignment(
        self, ctx: SystemVerilogParser.Nonblocking_assignmentContext
    ):
        self.sv2aplan.blockAssignment2Aplan(ctx)

    def exitNet_assignment(self, ctx: SystemVerilogParser.Net_assignmentContext):
        self.sv2aplan.blockAssignment2Aplan(ctx)

    def exitVariable_assignment(
        self, ctx: SystemVerilogParser.Variable_assignmentContext
    ):
        self.sv2aplan.blockAssignment2Aplan(ctx)

    def exitOperator_assignment(
        self, ctx: SystemVerilogParser.Operator_assignmentContext
    ):
        self.sv2aplan.blockAssignment2Aplan(ctx)

    # PARAMETRS
    def exitLocal_parameter_declaration(
        self, ctx: SystemVerilogParser.Local_parameter_declarationContext
    ):
        self.sv2aplan.paramAssignment2Aplan(ctx, self.module_call)

    def exitParam_assignment(self, ctx: SystemVerilogParser.Param_assignmentContext):
        self.sv2aplan.paramAssignment2Aplan(ctx, self.module_call)

    def enterLoop_generate_construct(self, ctx):
        self.sv2aplan.generate2Aplan(ctx)

    def exitModule_instantiation(self, ctx):
        self.sv2aplan.moduleCall2Apan(ctx)

    # ALWAYS

    def enterAlways_construct(self, ctx: SystemVerilogParser.Always_constructContext):
        self.sv2aplan.always2Aplan(ctx)

    def exitAlways_construct(self, ctx: SystemVerilogParser.Always_constructContext):
        self.sv2aplan.removeLastRelatedArrays()

    # SEQUENCE BLOCK CONTEXT

    def exitSeq_block(self, ctx: SystemVerilogParser.Seq_blockContext):
        sv_structure: Structure | None = (
            self.sv2aplan.structure_pointer_list.getLastElement()
        )
        if sv_structure:
            predicate_list, initial_len = getLastCondPredicateList(self.sv2aplan)
            if len(predicate_list) == 1 and predicate_list[0] == None:
                protocol_params = getProtocolParams(self.sv2aplan)
                sv_structure.addProtocol(
                    "ELSE_BODY_{0}".format(
                        Counters_Object.getCounter(CounterTypes.ELSE_BODY_COUNTER)
                    ),
                    parametrs=protocol_params,
                    inside_the_task=(
                        self.sv2aplan.inside_the_task
                        or self.sv2aplan.inside_the_function
                    ),
                )
                removeFirstCondPredicate(self.sv2aplan)
                Counters_Object.incrieseCounter(CounterTypes.ELSE_BODY_COUNTER)

    # IFStatement
    def enterConditional_statement(
        self, ctx: SystemVerilogParser.Conditional_statementContext
    ):
        self.sv2aplan.ifStatement2Aplan(ctx)

    def exitConditional_statement(
        self, ctx: SystemVerilogParser.Conditional_statementContext
    ):
        self.sv2aplan.removeLastNameSpace()
        self.sv2aplan.removeLastNameChange()
        self.sv2aplan.removeLastCondPredicateList()

    # Enter a parse tree produced by SystemVerilogParser#cond_predicate.
    def enterCond_predicate(self, ctx: SystemVerilogParser.Cond_predicateContext):
        self.sv2aplan.conditionalPredecate2Aplan(ctx)

    def exitCond_predicate(self, ctx: SystemVerilogParser.Cond_predicateContext):
        removeFirstCondPredicate(self.sv2aplan)

    # ASSERT
    def exitAssert_property_statement(self, ctx):
        self.sv2aplan.assertPropertyStatement2Aplan(ctx)

    def exitSimple_immediate_assert_statement(
        self, ctx: SystemVerilogParser.Simple_immediate_assert_statementContext
    ):
        self.sv2aplan.assertInBlock2Aplan(ctx)

    # INITIAL
    def enterInitial_construct(self, ctx: SystemVerilogParser.Initial_constructContext):
        self.sv2aplan.initial2Aplan(ctx)

    def exitInitial_construct(self, ctx: SystemVerilogParser.Initial_constructContext):
        self.sv2aplan.removeLastRelatedArrays()

    #
    def exitTask_declaration(self, ctx: SystemVerilogParser.Task_declarationContext):
        self.sv2aplan.taskOrFunctionDeclaration2Aplan(ctx)

    def exitFunction_declaration(
        self, ctx: SystemVerilogParser.Function_declarationContext
    ):
        self.sv2aplan.taskOrFunctionDeclaration2Aplan(ctx)

    def exitClass_constructor_declaration(
        self, ctx: SystemVerilogParser.Class_constructor_declarationContext
    ):
        self.sv2aplan.taskOrFunctionDeclaration2Aplan(ctx)

    def exitPackage_import_declaration(
        self, ctx: SystemVerilogParser.Package_import_declarationContext
    ):
        self.sv2aplan.packageImport2Apan(ctx)
