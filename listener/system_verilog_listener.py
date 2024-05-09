from antlr4_verilog.systemverilog import SystemVerilogParserListener
from translator.system_verilog_to_aplan import SV2aplan
from structures.module_params import Parametr

class SVListener(SystemVerilogParserListener):
    def __init__(self):
        self.identifier = ''
        self.params = []
        self.input_port_ident = []
        self.output_port_ident = []
        self.internal_signals = []
        self.assignments = []
        self.assignment_counter = 1
        self.inp_sensetive_list = []
        self.if_counter = 1
        self.actions = ''
        self.behaviour = ''
        self.always_counter = 1
        self.not_blocked_prot = []
        self.parameters = []

    def enterModule_declaration(self, ctx):
        self.identifier = ctx.module_ansi_header().module_identifier().getText()

    def exitNet_declaration(self, ctx):
        if (ctx.net_type().getText() == 'wire'):
            for elem in ctx.list_of_net_decl_assignments().net_decl_assignment():
                identifier = elem.net_identifier().identifier().getText()
                self.internal_signals.append(identifier)
                expression = elem.expression().getText()
                if (expression):
                    self.assignments.append([identifier, expression])
                    sv2aplan = SV2aplan(self.input_port_ident, self.output_port_ident,
                                        self.internal_signals, self.identifier, self.assignment_counter, self.if_counter)
                    declaration_to_aplan = sv2aplan.declaration2Aplan(elem)
                    self.actions += declaration_to_aplan[0]
                    self.not_blocked_prot.append(declaration_to_aplan[1])
                    self.assignment_counter += 1

    def exitAnsi_port_declaration(self, ctx):
        if (ctx.net_port_header().getText() == 'input'):
            self.input_port_ident.append(ctx.port_identifier().getText())
        if (ctx.net_port_header().getText() == 'output'):
            self.output_port_ident.append(
                ctx.port_identifier().getText())

    def exitParam_assignment(self, ctx):
        self.params.append(Parametr(ctx.parameter_identifier(
        ).getText(), ctx.constant_param_expression().getText()))

    def enterAlways_construct(self, ctx):
        
        sv2aplan = SV2aplan(self.input_port_ident, self.output_port_ident,
                            self.internal_signals, self.identifier, self.assignment_counter, self.if_counter)
        always_to_aplan_result = sv2aplan.always2Aplan(ctx,  self.always_counter)
        self.actions += always_to_aplan_result[0]
        self.behaviour += always_to_aplan_result[1]
        self.inp_sensetive_list.append(always_to_aplan_result[2])
        self.assignment_counter = always_to_aplan_result[3]
        self.if_counter = always_to_aplan_result[4]
        self.always_counter += 1