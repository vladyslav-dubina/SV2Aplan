from antlr4_verilog.systemverilog import SystemVerilogParserListener
from antlr4_verilog.systemverilog import SystemVerilogParser

from translator.system_verilog_to_aplan import (
    SV2aplan,
)
from classes.declarations import Declaration, DeclTypes
from classes.protocols import Protocol
from classes.element_types import ElementsTypes
from classes.module import Module
from classes.counters import CounterTypes
from classes.parametrs import Parametr
from classes.module import (
    Module,
)
from classes.module_call import ModuleCall
from utils.string_formating import (
    replaceParametrsCalls,
    replace_filename,
)
from utils.utils import (
    Counters_Object,
    extractVectorSize,
    vectorSize2AplanVectorSize,
    is_numeric_string,
    extractDimentionSize,
)


class SVListener(SystemVerilogParserListener):
    global Counters_Object

    def __init__(self, program, module_call: ModuleCall | None):
        from program.program import Program

        self.module: Module = None
        self.program: Program = program
        self.module_call: ModuleCall | None = module_call

    def enterModule_declaration(self, ctx):
        if ctx.module_ansi_header() is not None:
            index = self.program.modules.addElement(
                Module(
                    ctx.module_ansi_header().module_identifier().getText(),
                    ctx.getSourceInterval(),
                )
            )
            self.module = self.program.modules.getElementByIndex(index)

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
        if self.module_call is not None:
            source_parametr = self.module_call.paramets.findElement(identifier)
            if source_parametr is not None:
                parametr = self.module.parametrs.getElementByIndex(parametr_index)
                parametr.value = source_parametr.value

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
                    "",
                    0,
                    ctx.getSourceInterval(),
                )
            )

    def exitData_declaration(self, ctx):
        data_type = ctx.data_type_or_implicit().getText()
        aplan_vector_size = [0]
        size_expression = data_type
        data_type = replaceParametrsCalls(self.module.parametrs, data_type)
        vector_size = extractVectorSize(data_type)
        if vector_size is not None:
            aplan_vector_size = vectorSize2AplanVectorSize(
                vector_size[0], vector_size[1]
            )

        for elem in ctx.list_of_variable_decl_assignments().variable_decl_assignment():
            identifier = elem.variable_identifier().identifier().getText()

            unpacked_dimention = elem.variable_dimension(0)
            dimension_size = 0
            dimension_size_expression = ""
            if unpacked_dimention is not None:
                dimension = unpacked_dimention.getText()
                dimension_size_expression = dimension
                dimension = replaceParametrsCalls(self.module.parametrs, dimension)
                dimension_size = extractDimentionSize(dimension)

            index = data_type.find("reg")
            is_register = False
            if index != -1:
                is_register = True

            if is_register == True:
                assign_name = ""
                decl_index = self.module.declarations.addElement(
                    Declaration(
                        DeclTypes.REG,
                        identifier,
                        assign_name,
                        size_expression,
                        aplan_vector_size[0],
                        dimension_size_expression,
                        dimension_size,
                        ctx.getSourceInterval(),
                    )
                )

            if elem.expression() is not None:
                if is_register == True:
                    expression = elem.expression().getText()
                    sv2aplan = SV2aplan(self.module)
                    assign_name = sv2aplan.declaration2Aplan(elem)
                    declaration = self.module.declarations.getElementByIndex(decl_index)
                    declaration.expression = assign_name

    def exitNet_declaration(self, ctx):
        data_type = ctx.data_type_or_implicit()

        unpacked_dimention = ctx.unpacked_dimension(0)
        dimension_size = 0
        dimension_size_expression = ""
        if unpacked_dimention is not None:
            dimension = unpacked_dimention.getText()
            dimension_size_expression = dimension
            dimension = replaceParametrsCalls(self.module.parametrs, dimension)
            dimension_size = extractDimentionSize(dimension)

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
                        dimension_size_expression,
                        dimension_size,
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
        unpacked_dimention = ctx.unpacked_dimension(0)
        dimension_size = 0
        dimension_size_expression = ""
        if unpacked_dimention is not None:
            dimension = unpacked_dimention.getText()
            dimension_size_expression = dimension
            dimension = replaceParametrsCalls(self.module.parametrs, dimension)
            dimension_size = extractDimentionSize(dimension)

        data_type = DeclTypes.INPORT
        index = header.find("output")
        if index != -1:
            data_type = DeclTypes.OUTPORT

        index = header.find("input")
        if index != -1:
            data_type = DeclTypes.INPORT

        size_expression = header
        header = replaceParametrsCalls(self.module.parametrs, header)
        vector_size = extractVectorSize(header)
        aplan_vector_size = [0]

        if vector_size is not None:
            aplan_vector_size = vectorSize2AplanVectorSize(
                vector_size[0], vector_size[1]
            )

        assign_name = ""

        port = Declaration(
            data_type,
            ctx.port_identifier().getText(),
            assign_name,
            size_expression,
            aplan_vector_size[0],
            dimension_size_expression,
            dimension_size,
            ctx.getSourceInterval(),
        )
        decl_index = self.module.declarations.addElement(port)

        constant_expression = ctx.constant_expression()
        if constant_expression is not None:
            expression = constant_expression.getText()
            sv2aplan = SV2aplan(self.module)
            assign_name, source_interval = sv2aplan.expression2Aplan(
                expression, ElementsTypes.ASSIGN_ELEMENT, ctx.getSourceInterval()
            )
            declaration = self.module.declarations.getElementByIndex(decl_index)
            declaration.expression = assign_name

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
            assert_b = "ASSERT_B_{}".format(
                Counters_Object.getCounter(CounterTypes.B_COUNTER)
            )
            struct_assert = Protocol(
                assert_b,
                ctx.getSourceInterval(),
            )
            struct_assert.addBody(
                ("{0}.Delta + !{0}.0".format(assert_name), ElementsTypes.ACTION_ELEMENT)
            )
            self.module.out_of_block_elements.addElement(struct_assert)

    def exitNet_assignment(self, ctx):
        sv2aplan = SV2aplan(self.module)
        assign_name, source_interval = sv2aplan.expression2Aplan(
            ctx.getText(), ElementsTypes.ASSIGN_ELEMENT, ctx.getSourceInterval()
        )
        if source_interval != ctx.getSourceInterval():
            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
            assign_b = "ASSIGN_B_{}".format(
                Counters_Object.getCounter(CounterTypes.B_COUNTER)
            )
            struct_assign = Protocol(
                assign_b,
                ctx.getSourceInterval(),
            )
            struct_assign.addBody((assign_name, ElementsTypes.ACTION_ELEMENT))
            self.module.out_of_block_elements.addElement(struct_assign)

    def exitModule_instantiation(self, ctx):
        from translator.translator import SystemVerilogFinder

        destination_identifier = ctx.module_identifier().getText()
        previous_file_path = self.program.file_path
        file_path = replace_filename(
            self.program.file_path, f"{destination_identifier}.sv"
        )
        file_data = self.program.readFileData(file_path)
        finder = SystemVerilogFinder()
        finder.setUp(file_data)

        module_call = ModuleCall(
            self.module.identifier,
            destination_identifier,
            ctx.parameter_value_assignment().getText(),
            self.module.parametrs,
        )

        call_module_name = finder.startTranslate(self.program, module_call)
        self.program.file_path = previous_file_path
        sv2aplan = SV2aplan(self.module)
        sv2aplan.moduleCall2Aplan(ctx, call_module_name)
        Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
        call_b = "MODULE_CALL_B_{}".format(
            Counters_Object.getCounter(CounterTypes.B_COUNTER)
        )
        struct_call = Protocol(
            call_b,
            ctx.getSourceInterval(),
        )
        struct_call.addBody(
            (f"call B_{call_module_name.upper()}", ElementsTypes.PROTOCOL_ELEMENT)
        )
        self.module.out_of_block_elements.addElement(struct_call)
