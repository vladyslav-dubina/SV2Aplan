from antlr4_verilog.systemverilog import SystemVerilogParserListener

from translator.system_verilog_to_aplan import (
    SV2aplan,
)
from classes.declarations import Declaration, DeclTypes
from classes.protocols import Protocol
from classes.module import Module, ElementsTypes
from classes.counters import CounterTypes
from classes.parametrs import Parametr
from utils import (
    Counters_Object,
    extractVectorSize,
    vectorSize2AplanVectorSize,
    is_numeric_string,
    replaceParametrsCalls,
)
from classes.module import Module, ModuleArray


class SVListener(SystemVerilogParserListener):
    global Counters_Object

    def __init__(self, modules: ModuleArray):
        self.module = None
        self.modules: ModuleArray = modules

    def enterModule_declaration(self, ctx):
        if ctx.module_ansi_header() is not None:
            index = self.modules.addElement(
                Module(
                    ctx.module_ansi_header().module_identifier().getText(),
                    ctx.getSourceInterval(),
                )
            )
            self.module = self.modules.getElementByIndex(index)

    def exitParam_assignment(self, ctx):
        identifier = ctx.parameter_identifier().getText()
        expression = ctx.constant_param_expression()
        expression_str = ""
        value = 0
        if expression is not None:
            numeric_string = is_numeric_string(expression.getText())
            if numeric_string is None:
                expression_str = expression.getText()
            else:
                value = numeric_string
        parametr_index = self.module.parametrs.addElement(
            Parametr(
                identifier,
                ctx.getSourceInterval(),
                value,
                expression_str,
            )
        )
        self.module.parametrs.evaluateParametrExpressionByIndex(parametr_index)

    def exitGenvar_declaration(self, ctx):
        assign_name = ""
        for element in ctx.list_of_genvar_identifiers().genvar_identifier():
            identifier = element.identifier().getText()
            self.module.declarations.addElement(
                Declaration(
                    DeclTypes.INT,
                    identifier,
                    assign_name,
                    "",
                    0,
                    ctx.getSourceInterval(),
                )
            )

    def exitData_declaration(self, ctx):
        if ctx.data_type_or_implicit():
            data_type = ctx.data_type_or_implicit().getText()
            aplan_vector_size = [0]
            size_expression = data_type
            data_type = replaceParametrsCalls(self.module.parametrs, data_type)
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
                            size_expression,
                            aplan_vector_size[0],
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
        size_expression = ""
        if data_type:
            size_expression = data_type.getText()
            data_type = replaceParametrsCalls(
                self.module.parametrs, data_type.getText()
            )
            vector_size = extractVectorSize(data_type)
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
                        size_expression,
                        aplan_vector_size[0],
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
            size_expression = header
            header = replaceParametrsCalls(self.module.parametrs, header)
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
                size_expression,
                aplan_vector_size[0],
                ctx.getSourceInterval(),
            )
            self.module.declarations.addElement(port)

        index = header.find("output")
        if index != -1:
            size_expression = header
            header = replaceParametrsCalls(self.module.parametrs, header)
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
                size_expression,
                aplan_vector_size[0],
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
                ctx.getSourceInterval(),
            )
            struct_assign.addBody(assign_name)
            self.module.out_of_block_elements.addElement(struct_assign)
