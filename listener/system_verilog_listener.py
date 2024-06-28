from antlr4_verilog.systemverilog import SystemVerilogParserListener
from translator.declarations.ansi_port_declaration import ansiPortDeclaration2Aplan
from translator.declarations.data_declaration import dataDecaration2Aplan
from translator.declarations.genvar_declaration import genvarDeclaration2Aplan
from translator.declarations.module_declaration import moduleDeclaration2Aplan
from translator.declarations.net_declaration import netDeclaration2Aplan
from translator.system_verilog_to_aplan import (
    SV2aplan,
)
from classes.declarations import Declaration, DeclTypes
from classes.protocols import Protocol
from classes.element_types import ElementsTypes
from classes.module import Module
from classes.counters import CounterTypes
from classes.parametrs import Parametr
from classes.module import Module
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

    def __init__(self, program, module_call: ModuleCall | None = None):
        from program.program import Program

        self.module: Module = None
        self.program: Program = program
        self.module_call: ModuleCall | None = module_call

    def enterModule_declaration(self, ctx):
        self.module = moduleDeclaration2Aplan(ctx, self.program, self.module_call)

    def exitGenvar_declaration(self, ctx):
        genvarDeclaration2Aplan(ctx, self.module)

    def exitData_declaration(self, ctx):
        dataDecaration2Aplan(ctx, self.module, True)

    def exitNet_declaration(self, ctx):
        netDeclaration2Aplan(ctx, self.module)

    def exitAnsi_port_declaration(self, ctx):
        ansiPortDeclaration2Aplan(ctx, self.module)

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
        if not self.module.processed_elements.isInProcessedElementAlready(
            ctx.getSourceInterval()
        ):
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
                    ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT,
                )
                assign_name = f"Sensetive({assign_name})"
                struct_assign.addBody((assign_name, ElementsTypes.ACTION_ELEMENT))
                self.module.out_of_block_elements.addElement(struct_assign)

    def exitModule_instantiation(self, ctx):
        from translator.translator import SystemVerilogFinder

        destination_identifier = ctx.module_identifier().getText()

        object_name = ""
        hierarchy = ctx.hierarchical_instance(0)
        if hierarchy is not None:
            object_name = hierarchy.name_of_instance().getText()

        parametrs = ctx.parameter_value_assignment()
        if parametrs is not None:
            parametrs = parametrs.getText()
        else:
            parametrs = ""

        parametrs = ctx.parameter_value_assignment()
        if parametrs is not None:
            parametrs = parametrs.getText()
        else:
            parametrs = ""

        module_call = ModuleCall(
            destination_identifier,
            object_name,
            self.module.identifier,
            destination_identifier,
            parametrs,
            self.module.parametrs,
        )
        call_module_name = object_name

        try:
            previous_file_path = self.program.file_path
            file_path = replace_filename(
                self.program.file_path, f"{destination_identifier}.sv"
            )
            file_data = self.program.readFileData(file_path)
            finder = SystemVerilogFinder()
            finder.setUp(file_data)
            finder.startTranslate(self.program, module_call)
        except Exception as e:
            self.program.module_calls.addElement(module_call)

        self.program.file_path = previous_file_path
        sv2aplan = SV2aplan(self.module)
        sv2aplan.moduleCall2Aplan(ctx, call_module_name)
        Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
        call_b = "MODULE_CALL_B_{}".format(
            Counters_Object.getCounter(CounterTypes.B_COUNTER)
        )
        struct_call = Protocol(
            call_b, ctx.getSourceInterval(), ElementsTypes.MODULE_CALL_ELEMENT
        )
        struct_call.addBody(
            (f"call B_{call_module_name.upper()}", ElementsTypes.PROTOCOL_ELEMENT)
        )
        self.module.out_of_block_elements.addElement(struct_call)
