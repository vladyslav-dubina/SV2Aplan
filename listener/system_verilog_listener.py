from antlr4_verilog.systemverilog import SystemVerilogParserListener

from translator.system_verilog_to_aplan import (
    SV2aplan,
    extractVectorSize,
    vectorSize2Aplan,
)
from structures.aplan import Declaration, DeclTypes, Module, Protocol
from structures.counters import CounterTypes
from utils import Counters_Object


class SVListener(SystemVerilogParserListener):
    global Counters_Object

    def __init__(self):
        self.module = None

    def enterModule_declaration(self, ctx):
        if ctx.module_ansi_header() is not None:
            self.module = Module(ctx.module_ansi_header().module_identifier().getText())

    def exitGenvar_declaration(self, ctx):
        assign_name = ""
        for element in ctx.list_of_genvar_identifiers().genvar_identifier():
            identifier = element.identifier().getText()
            self.module.addDeclaration(
                Declaration(
                    DeclTypes.REG,
                    identifier,
                    assign_name,
                    0,
                )
            )

    def exitData_declaration(self, ctx):
        assign_name = ""
        if ctx.data_type_or_implicit():
            data_type = ctx.data_type_or_implicit().getText()
            index = data_type.find("reg")
            if index != -1:
                for (
                    elem
                ) in ctx.list_of_variable_decl_assignments().variable_decl_assignment():
                    identifier = elem.variable_identifier().identifier().getText()
                    if elem.expression():
                        expression = elem.expression().getText()
                        if expression:
                            sv2aplan = SV2aplan(self.module)
                            assign_name = sv2aplan.declaration2Aplan(elem)
                    if not assign_name:
                        assign_name = ""

                    self.module.addDeclaration(
                        Declaration(
                            DeclTypes.REG,
                            identifier,
                            assign_name,
                            0,
                        )
                    )

    def exitNet_declaration(self, ctx):
        assign_name = ""
        if ctx.net_type().getText() == "wire":
            for elem in ctx.list_of_net_decl_assignments().net_decl_assignment():
                identifier = elem.net_identifier().identifier().getText()
                if elem.expression():
                    expression = elem.expression().getText()
                    if expression:
                        sv2aplan = SV2aplan(self.module)
                        assign_name = sv2aplan.declaration2Aplan(elem)
                if not assign_name:
                    assign_name = ""

                self.module.addDeclaration(
                    Declaration(DeclTypes.WIRE, identifier, assign_name, 0)
                )

    def exitAnsi_port_declaration(self, ctx):
        header = ctx.net_port_header().getText()
        index = header.find("input")
        if index != -1:
            vector_size = extractVectorSize(header)
            if vector_size is None:
                port = Declaration(
                    DeclTypes.INPORT,
                    ctx.port_identifier().getText(),
                    "",
                    0,
                )
                self.module.addDeclaration(port)
            else:
                aplan_vector_size = vectorSize2Aplan(vector_size[0], vector_size[1])
                port = Declaration(
                    DeclTypes.INPORT,
                    ctx.port_identifier().getText(),
                    "",
                    aplan_vector_size[0],
                )
                self.module.addDeclaration(port)

        index = header.find("output")
        if index != -1:
            vector_size = extractVectorSize(header)
            if vector_size is None:
                port = Declaration(
                    DeclTypes.OUTPORT,
                    ctx.port_identifier().getText(),
                    "",
                    0,
                )
                self.module.addDeclaration(port)
            else:
                aplan_vector_size = vectorSize2Aplan(vector_size[0], vector_size[1])
                port = Declaration(
                    DeclTypes.OUTPORT,
                    ctx.port_identifier().getText(),
                    "",
                    aplan_vector_size[0],
                )
                self.module.addDeclaration(port)

    def enterAlways_construct(self, ctx):
        sv2aplan = SV2aplan(self.module)
        sv2aplan.always2Aplan(ctx)

    def exitAssert_property_statement(self, ctx):
        expression = ctx.property_spec()
        if expression is not None:
            sv2aplan = SV2aplan(self.module)
            assert_name = sv2aplan.assert2Aplan(expression.getText())
            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
            assert_b = "assert_B_{}".format(
                Counters_Object.getCounter(CounterTypes.B_COUNTER)
            )
            struct_assert = Protocol(assert_b)
            struct_assert.addBody("{0}.Delta + !{0}.0".format(assert_name))
            self.module.not_block_elements.append(struct_assert)

   # def exitNet_assignment(self, ctx):
     #   print(ctx.getText())

    #def exitVariable_assignment(self, ctx):
     #   print(ctx.getText())
