from antlr4_verilog.systemverilog import SystemVerilogParserListener

from translator.system_verilog_to_aplan import SV2aplan, extractVectorSize, vectorSize2Aplan
from structures.aplan import Declaration, DeclTypes, Module, CounterTypes


class SVListener(SystemVerilogParserListener):
    def __init__(self):
        self.module = None

    def enterModule_declaration(self, ctx):
        if (ctx.module_ansi_header() is not None):
            self.module = Module(
                ctx.module_ansi_header().module_identifier().getText())

    def exitData_declaration(self, ctx):
        assign_name = ''
        if ctx.data_type_or_implicit():
            data_type = ctx.data_type_or_implicit().getText()
            index = data_type.find('reg')
            if index != -1:
                for elem in ctx.list_of_variable_decl_assignments().variable_decl_assignment():
                    identifier = elem.variable_identifier().identifier().getText()
                    if (elem.expression()):
                        expression = elem.expression().getText()
                        if (expression):
                            sv2aplan = SV2aplan(self.module)
                            assign_name = sv2aplan.declaration2Aplan(elem)
                    if (not assign_name):
                        assign_name = ''
                    self.module.declarations.append(Declaration(
                        DeclTypes.REG, identifier, assign_name, 0))

    def exitNet_declaration(self, ctx):
        assign_name = ''
        if (ctx.net_type().getText() == 'wire'):
            for elem in ctx.list_of_net_decl_assignments().net_decl_assignment():
                identifier = elem.net_identifier().identifier().getText()
                self.module.internal_signals.append(identifier)
                if (elem.expression()):
                    expression = elem.expression().getText()
                    if (expression):
                        sv2aplan = SV2aplan(self.module)
                        assign_name = sv2aplan.declaration2Aplan(elem)
                    if (not assign_name):
                        assign_name = ''
                    self.module.declarations.append(Declaration(
                        DeclTypes.WIRE, identifier, assign_name, 0))

    def exitAnsi_port_declaration(self, ctx):
        header = ctx.net_port_header().getText()
        index = header.find('input')
        if index != -1:
            vector_size = extractVectorSize(header)
            if (vector_size is None):
                port = Declaration(
                    DeclTypes.INPORT, ctx.port_identifier().getText(), '', 0)
                self.module.declarations.append(port)
            else:
                aplan_vector_size = vectorSize2Aplan(
                    vector_size[0], vector_size[1])
                port = Declaration(DeclTypes.INPORT, ctx.port_identifier().getText(), '',
                                   aplan_vector_size[0])
                self.module.declarations.append(port)

        index = header.find('output')
        if index != -1:
            vector_size = extractVectorSize(header)
            if (vector_size is None):
                port = Declaration(
                    DeclTypes.OUTPORT, ctx.port_identifier().getText(), '', 0)
                self.module.declarations.append(port)
            else:
                aplan_vector_size = vectorSize2Aplan(
                    vector_size[0], vector_size[1])
                port = Declaration(DeclTypes.OUTPORT, ctx.port_identifier().getText(), '',
                                   aplan_vector_size[0])
                self.module.declarations.append(port)

    def enterAlways_construct(self, ctx):
        sv2aplan = SV2aplan(self.module)
        always_to_aplan_result = sv2aplan.always2Aplan(ctx)
#        self.actions += always_to_aplan_result[0]
#        self.behaviour += always_to_aplan_result[1]
#        self.assignment_counter = always_to_aplan_result[2]
#        self.if_counter = always_to_aplan_result[3]
#        self.always_counter += 1
