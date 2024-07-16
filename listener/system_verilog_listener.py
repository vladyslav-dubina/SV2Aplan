from antlr4_verilog.systemverilog import SystemVerilogParserListener
from translator.declarations.module_declaration import moduleDeclaration2Aplan
from translator.system_verilog_to_aplan import (
    SV2aplan,
)
from classes.module import Module
from classes.module import Module
from classes.module_call import ModuleCall


class SVListener(SystemVerilogParserListener):
    def __init__(self, program, module_call: ModuleCall | None = None):
        from program.program import Program

        self.module: Module = None
        self.program: Program = program
        self.sv2aplan: SV2aplan = SV2aplan(None)
        self.module_call: ModuleCall | None = module_call

    def enterModule_declaration(self, ctx):
        self.module = moduleDeclaration2Aplan(ctx, self.program, self.module_call)
        self.sv2aplan = SV2aplan(self.module)

    def exitGenvar_declaration(self, ctx):
        self.sv2aplan.genvarDeclaration2Aplan(ctx)

    def exitData_declaration(self, ctx):
        self.sv2aplan.dataDecaration2Aplan(ctx, True)

    def exitNet_declaration(self, ctx):
        self.sv2aplan.netDeclaration2Aplan(ctx)

    def exitAnsi_port_declaration(self, ctx):
        self.sv2aplan.ansiPortDeclaration2Aplan(ctx)

    def exitNet_assignment(self, ctx):
        self.sv2aplan.netAssignment2Aplan(ctx)

    def exitParam_assignment(self, ctx):
        self.sv2aplan.paramAssignment2Aplan(ctx, self.module_call)

    def enterLoop_generate_construct(self, ctx):
        self.sv2aplan.generate2Aplan(ctx)

    def enterAlways_construct(self, ctx):
        self.sv2aplan.always2Aplan(ctx)

    def exitAssert_property_statement(self, ctx):
        self.sv2aplan.assertPropertyStatement2Aplan(ctx)

    def exitModule_instantiation(self, ctx):
        self.sv2aplan.moduleCall2Apan(ctx, self.program)

    def exitInitial_construct(self, ctx):
        self.sv2aplan.initial2Aplan(ctx)
