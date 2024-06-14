from antlr4_verilog.systemverilog import SystemVerilogParserListener

from translator.system_verilog_to_aplan import (
    SV2aplan,
)
from structures.aplan import Declaration, DeclTypes, Module, Protocol, ElementsTypes
from structures.counters import CounterTypes
from utils import Counters_Object, extractVectorSize, vectorSize2AplanVectorSize


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
                    DeclTypes.INT,
                    identifier,
                    assign_name,
                    0,
                    Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
                )
            )

    def exitData_declaration(self, ctx):
        assign_name = ""
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
                            aplan_vector_size[0],
                            Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
                        )
                    )

    def exitNet_declaration(self, ctx):
        assign_name = ""
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
                if elem.expression():
                    expression = elem.expression().getText()
                    if expression:
                        sv2aplan = SV2aplan(self.module)
                        assign_name = sv2aplan.declaration2Aplan(elem)
                if not assign_name:
                    assign_name = ""

                self.module.addDeclaration(
                    Declaration(
                        DeclTypes.WIRE,
                        identifier,
                        assign_name,
                        aplan_vector_size[0],
                        Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
                    )
                )

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
            )
            self.module.addDeclaration(port)

        index = header.find("output")
        if index != -1:
            vector_size = extractVectorSize(header)
            aplan_vector_size = [0]
            if vector_size is None:
                aplan_vector_size = vectorSize2AplanVectorSize(
                    vector_size[0], vector_size[1]
                )
            aplan_vector_size = vectorSize2AplanVectorSize(
                vector_size[0], vector_size[1]
            )
            port = Declaration(
                DeclTypes.OUTPORT,
                ctx.port_identifier().getText(),
                "",
                aplan_vector_size[0],
                Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
            )
            self.module.addDeclaration(port)

    def exitFor_variable_declaration(self, ctx):
        assign_name = ""
        data_type = ctx.data_type()
        sv2aplan = SV2aplan(self.module)
        action_txt = (
            f"{ctx.variable_identifier(0).getText()}={ctx.expression(0).getText()}"
        )
        assign_name = sv2aplan.expression2Aplan(
            action_txt, ElementsTypes.ASSIGN_ELEMENT
        )
        print(assign_name)
        data_type = DeclTypes.checkType(data_type)
        self.module.addDeclaration(
            Declaration(
                data_type,
                ctx.variable_identifier(0).getText(),
                assign_name,
                0,
                Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
            )
        )

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
            assert_name = sv2aplan.expression2Aplan(
                expression.getText(), ElementsTypes.ASSERT_ELEMENT
            )
            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
            assert_b = "assert_B_{}".format(
                Counters_Object.getCounter(CounterTypes.B_COUNTER)
            )
            struct_assert = Protocol(
                assert_b,
                Counters_Object.getCounter(CounterTypes.SEQUENCE_COUNTER),
            )
            struct_assert.addBody("{0}.Delta + !{0}.0".format(assert_name))
            self.module.out_of_block_elements.append(struct_assert)


"""
    def exitNet_assignment(self, ctx):
        print("tre")
        sv2aplan = SV2aplan(self.module)
        assign_name = sv2aplan.expression2Aplan(
            ctx.getText(), ElementsTypes.ASSIGN_ELEMENT
        )
        Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
        assign_b = "assign_B_{}".format(
            Counters_Object.getCounter(CounterTypes.B_COUNTER)
        )
        struct_assign = Protocol(assign_b)
        struct_assign.addBody(assign_name)
        self.module.out_of_block_elements.append(struct_assign)

    def exitVariable_assignment(self, ctx):
        sv2aplan = SV2aplan(self.module)
        assign_name = sv2aplan.expression2Aplan(
            ctx.getText(), ElementsTypes.ASSIGN_ELEMENT
        )
        Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
        assign_b = "assign_B_{}".format(
            Counters_Object.getCounter(CounterTypes.B_COUNTER)
        )
        struct_assign = Protocol(assign_b)
        struct_assign.addBody(assign_name)
        self.module.out_of_block_elements.append(struct_assign)
"""

"""
    def exitFor_variable_declaration(self, ctx):
        assign_name = ""
        data_type = ctx.data_type().getText()
        data_type = DeclTypes.checkType(data_type)
        for elem in ctx.variable_identifier():
            identifier = elem.getText()
            self.module.addDeclaration(
                Declaration(data_type, identifier, assign_name, 0)
            )
            
            if ctx.expression():
                expression = ctx.expression(0).getText()
                if expression:
                    sv2aplan = SV2aplan(self.module)
                    assign_name = sv2aplan.assign2Aplan(f"{identifier}={expression}")
            if not assign_name:
                assign_name = ""
            self.module.updateDeclarationExpression(
                self.module.findDeclaration(identifier), assign_name
            )
            """
