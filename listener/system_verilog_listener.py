from antlr4_verilog.systemverilog import (
    SystemVerilogParserListener,
    SystemVerilogParser,
)
from translator.declarations.class_declaration import classDeclaration2Aplan
from translator.declarations.interface_declaration import interfaceDeclaration2Aplan
from translator.declarations.module_declaration import moduleDeclaration2Aplan
from translator.declarations.package_declaration import packageDeclaration2Aplan
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

    def exitGenvar_declaration(self, ctx):
        self.sv2aplan.genvarDeclaration2Aplan(ctx)

    def exitData_declaration(self, ctx):
        self.sv2aplan.dataDecaration2Aplan(ctx, True)

    def exitNet_declaration(self, ctx: SystemVerilogParser.Net_declarationContext):
        self.sv2aplan.netDeclaration2Aplan(ctx)

    def exitAnsi_port_declaration(self, ctx):
        self.sv2aplan.ansiPortDeclaration2Aplan(ctx)

    def exitNet_assignment(self, ctx):
        self.sv2aplan.netAssignment2Aplan(ctx)

    def exitLocal_parameter_declaration(
        self, ctx: SystemVerilogParser.Local_parameter_declarationContext
    ):
        self.sv2aplan.paramAssignment2Aplan(ctx, self.module_call)

    def exitParam_assignment(self, ctx: SystemVerilogParser.Param_assignmentContext):
        self.sv2aplan.paramAssignment2Aplan(ctx, self.module_call)

    def enterLoop_generate_construct(self, ctx):
        self.sv2aplan.generate2Aplan(ctx)

    def enterAlways_construct(self, ctx):
        self.sv2aplan.always2Aplan(ctx)

    def exitAssert_property_statement(self, ctx):
        self.sv2aplan.assertPropertyStatement2Aplan(ctx)

    def exitModule_instantiation(self, ctx):
        self.sv2aplan.moduleCall2Apan(ctx)

    def exitInitial_construct(self, ctx):
        self.sv2aplan.initial2Aplan(ctx)

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
