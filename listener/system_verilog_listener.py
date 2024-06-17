from antlr4_verilog.systemverilog import SystemVerilogParserListener

from translator.system_verilog_to_aplan import (
    SV2aplan,
)
from classes.declarations import Declaration, DeclTypes
from classes.protocols import Protocol
from classes.aplan import Module, ElementsTypes
from classes.counters import CounterTypes
from utils import Counters_Object, extractVectorSize, vectorSize2AplanVectorSize


class SVListener(SystemVerilogParserListener):
    global Counters_Object

    def __init__(self):
        self.module = None

    def enterModule_declaration(self, ctx):
        if ctx.module_ansi_header() is not None:
            self.module = Module(ctx.module_ansi_header().module_identifier().getText())

    def exitParameter_declaration(self, ctx):
        print(ctx.getText())

    def exitGenvar_declaration(self, ctx):
        assign_name = ""
        for element in ctx.list_of_genvar_identifiers().genvar_identifier():
            identifier = element.identifier().getText()
            self.module.declarations.addElement(
                Declaration(
                    DeclTypes.INT,
                    identifier,
                    assign_name,
                    0,
                    Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
                    ctx.getSourceInterval(),
                )
            )

    def exitData_declaration(self, ctx):
        if ctx.data_type_or_implicit():
            data_type = ctx.data_type_or_implicit().getText()
            aplan_vector_size = [0]
            vector_size = extractVectorSize(data_type)
            if vector_size is not None:
                aplan_vector_size = vectorSize2AplanVectorSize(
                    vector_size[0], vector_size[1]
                )
            index = data_type.find("reg")
            if index != -1:
                for (
                    elem
                ) in ctx.list_of_variable_decl_assignments().variable_decl_assignment():
                    assign_name = ""
                    identifier = elem.variable_identifier().identifier().getText()
                    decl_index = self.module.declarations.addElement(
                        Declaration(
                            DeclTypes.REG,
                            identifier,
                            assign_name,
                            aplan_vector_size[0],
                            Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
                            ctx.getSourceInterval(),
                        )
                    )

                    if elem.expression():
                        expression = elem.expression().getText()
                        if expression:
                            sv2aplan = SV2aplan(self.module)
                            assign_name = sv2aplan.declaration2Aplan(elem)
                            declaration = self.module.declarations.getElementByIndex(
                                decl_index
                            )
                            declaration.expression = assign_name

    def exitNet_declaration(self, ctx):
        data_type = ctx.data_type_or_implicit()
        aplan_vector_size = [0]
        if data_type:
            vector_size = extractVectorSize(data_type.getText())
            if vector_size is not None:
                aplan_vector_size = vectorSize2AplanVectorSize(
                    vector_size[0], vector_size[1]
                )

        if ctx.net_type().getText() == "wire":
            for elem in ctx.list_of_net_decl_assignments().net_decl_assignment():
                identifier = elem.net_identifier().identifier().getText()
                assign_name = ""
                decl_index = self.module.declarations.addElement(
                    Declaration(
                        DeclTypes.WIRE,
                        identifier,
                        assign_name,
                        aplan_vector_size[0],
                        Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
                        ctx.getSourceInterval(),
                    )
                )

                if elem.expression():
                    expression = elem.expression().getText()
                    if expression:
                        sv2aplan = SV2aplan(self.module)
                        assign_name = sv2aplan.declaration2Aplan(elem)
                        declaration = self.module.declarations.getElementByIndex(
                            decl_index
                        )
                        declaration.expression = assign_name

    def exitAnsi_port_declaration(self, ctx):
        header = ctx.net_port_header().getText()
        index = header.find("input")
        if index != -1:
            vector_size = extractVectorSize(header)
            aplan_vector_size = [0]
            if vector_size is not None:
                aplan_vector_size = vectorSize2AplanVectorSize(
                    vector_size[0], vector_size[1]
                )

            port = Declaration(
                DeclTypes.INPORT,
                ctx.port_identifier().getText(),
                "",
                aplan_vector_size[0],
                Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
                ctx.getSourceInterval(),
            )
            self.module.declarations.addElement(port)

        index = header.find("output")
        if index != -1:
            vector_size = extractVectorSize(header)
            aplan_vector_size = [0]
            if vector_size is not None:
                aplan_vector_size = vectorSize2AplanVectorSize(
                    vector_size[0], vector_size[1]
                )

            port = Declaration(
                DeclTypes.OUTPORT,
                ctx.port_identifier().getText(),
                "",
                aplan_vector_size[0],
                Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
                ctx.getSourceInterval(),
            )
            self.module.declarations.addElement(port)

    def enterLoop_generate_construct(self, ctx):
        sv2aplan = SV2aplan(self.module)
        sv2aplan.generate2Aplan(ctx)

    def enterAlways_construct(self, ctx):
        sv2aplan = SV2aplan(self.module)
        sv2aplan.always2Aplan(ctx)

    def exitAssert_property_statement(self, ctx):
        expression = ctx.property_spec()
        if expression is not None:
            sv2aplan = SV2aplan(self.module)
            assert_name, source_interval = sv2aplan.expression2Aplan(
                expression.getText(),
                ElementsTypes.ASSERT_ELEMENT,
                ctx.getSourceInterval(),
            )
            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
            assert_b = "assert_B_{}".format(
                Counters_Object.getCounter(CounterTypes.B_COUNTER)
            )
            struct_assert = Protocol(
                assert_b,
                Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
                ctx.getSourceInterval(),
            )
            struct_assert.addBody("{0}.Delta + !{0}.0".format(assert_name))
            self.module.out_of_block_elements.addElement(struct_assert)

    def exitNet_assignment(self, ctx):
        sv2aplan = SV2aplan(self.module)
        assign_name, source_interval = sv2aplan.expression2Aplan(
            ctx.getText(), ElementsTypes.ASSIGN_ELEMENT, ctx.getSourceInterval()
        )
        if source_interval != ctx.getSourceInterval():
            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
            assign_b = "assign_B_{}".format(
                Counters_Object.getCounter(CounterTypes.B_COUNTER)
            )
            struct_assign = Protocol(
                assign_b,
                Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
                ctx.getSourceInterval(),
            )
            struct_assign.addBody(assign_name)
            self.module.out_of_block_elements.addElement(struct_assign)
