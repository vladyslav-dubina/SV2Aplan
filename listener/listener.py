import antlr4
from antlr4_verilog.systemverilog import (
    SystemVerilogParserListener,
    SystemVerilogParser,
)

from AppModule.app.classes.design_unit_call import DesignUnitCall
from listener.base import BaseListener


def bodyPrint(ctx):
    if not ctx:
        return
    if isinstance(ctx, antlr4.tree.Tree.TerminalNodeImpl):
        return
    for element in ctx.getChildren():
        print(element.getText(), type(element))
        bodyPrint(element)


class SVToAplanListener(BaseListener, SystemVerilogParserListener):
    def __init__(self, design_unit_call: DesignUnitCall | None = None):
        BaseListener().__init__(design_unit_call)
        self.translator.getTranslator("module_decl")

    # =========================================================================================
    # OPERATORS
    # =========================================================================================

    # Enter a parse tree produced by SystemVerilogParser#polarity_operator.
    def enterPolarity_operator(self, ctx: SystemVerilogParser.Polarity_operatorContext):
        self.translator.translate("operator", ctx)

    # Exit a parse tree produced by SystemVerilogParser#polarity_operator.
    def exitPolarity_operator(self, ctx: SystemVerilogParser.Polarity_operatorContext):
        pass

    # Enter a parse tree produced by SystemVerilogParser#stream_operator.
    def enterStream_operator(self, ctx: SystemVerilogParser.Stream_operatorContext):
        self.translator.translate("operator", ctx)

    # Exit a parse tree produced by SystemVerilogParser#stream_operator.
    def exitStream_operator(self, ctx: SystemVerilogParser.Stream_operatorContext):
        pass

    # Enter a parse tree produced by SystemVerilogParser#unary_operator.
    def enterUnary_operator(self, ctx: SystemVerilogParser.Unary_operatorContext):
        self.translator.translate("operator", ctx)

    # Exit a parse tree produced by SystemVerilogParser#unary_operator.
    def exitUnary_operator(self, ctx: SystemVerilogParser.Unary_operatorContext):
        pass

    # Enter a parse tree produced by SystemVerilogParser#binary_operator.
    def enterBinary_operator(self, ctx: SystemVerilogParser.Binary_operatorContext):
        self.translator.translate("operator", ctx)

    # Exit a parse tree produced by SystemVerilogParser#binary_operator.
    def exitBinary_operator(self, ctx: SystemVerilogParser.Binary_operatorContext):
        pass

    # Enter a parse tree produced by SystemVerilogParser#inc_or_dec_operator.
    def enterInc_or_dec_operator(
        self, ctx: SystemVerilogParser.Inc_or_dec_operatorContext
    ):
        self.translator.translate("operator", ctx)

    # Exit a parse tree produced by SystemVerilogParser#inc_or_dec_operator.
    def exitInc_or_dec_operator(
        self, ctx: SystemVerilogParser.Inc_or_dec_operatorContext
    ):
        pass

    # Enter a parse tree produced by SystemVerilogParser#unary_module_path_operator.
    def enterUnary_module_path_operator(
        self, ctx: SystemVerilogParser.Unary_module_path_operatorContext
    ):
        self.translator.translate("operator", ctx)

    # Exit a parse tree produced by SystemVerilogParser#unary_module_path_operator.
    def exitUnary_module_path_operator(
        self, ctx: SystemVerilogParser.Unary_module_path_operatorContext
    ):
        pass

    # Enter a parse tree produced by SystemVerilogParser#binary_module_path_operator.
    def enterBinary_module_path_operator(
        self, ctx: SystemVerilogParser.Binary_module_path_operatorContext
    ):
        self.translator.translate("operator", ctx)

    # Exit a parse tree produced by SystemVerilogParser#binary_module_path_operator.
    def exitBinary_module_path_operator(
        self, ctx: SystemVerilogParser.Binary_module_path_operatorContext
    ):
        pass

    # Enter a parse tree produced by SystemVerilogParser#array_identifier.
    def exitIdentifier(self, ctx: SystemVerilogParser.IdentifierContext):
        self.translator.translate("identifyer", ctx)

    def enterNumber(self, ctx: SystemVerilogParser.NumberContext):
        self.translator.translate("number", ctx)

    # Enter a parse tree produced by SystemVerilogParser#bit_select.
    def enterBit_select(self, ctx: SystemVerilogParser.Bit_selectContext):
        self.translator.translate("bit_select", ctx)

    def enterVariable_lvalue(self, ctx: SystemVerilogParser.Variable_lvalueContext):
        self.translator.translate("var_l_val", ctx)

    def exitVariable_lvalue(self, ctx: SystemVerilogParser.Variable_lvalueContext):
        self.translator.exit("var_l_val", ctx)

    def enterConstant_bit_select(
        self, ctx: SystemVerilogParser.Constant_bit_selectContext
    ):
        self.translator.translate("bit_select", ctx)

    def enterUnpacked_dimension(
        self, ctx: SystemVerilogParser.Unpacked_dimensionContext
    ):
        self.translator.translate("unpkt_dmntn", ctx)

    def enterConstant_range(self, ctx: SystemVerilogParser.Constant_rangeContext):
        self.translator.translate("constant_range_select", ctx)

        # Enter a parse tree produced by SystemVerilogParser#dynamic_array_new.

    def enterDynamic_array_new(self, ctx: SystemVerilogParser.Dynamic_array_newContext):
        self.translator.translate("dynamic_array_new", ctx)

    # =========================================================================================
    # DECLARATIONS
    # =========================================================================================

    def enterInterface_declaration(
        self, ctx: SystemVerilogParser.Interface_declarationContext
    ):
        self.translator.translate("interface_decl", ctx)

    def enterModule_declaration(
        self, ctx: SystemVerilogParser.Module_declarationContext
    ):
        # self.counters.incriese(self.counters.types.STRUCT_COUNTER) ?
        self.translator.translate("module_decl", ctx)

    def enterPackage_declaration(
        self, ctx: SystemVerilogParser.Package_declarationContext
    ):
        self.translator.translate("package_decl", ctx)

    def enterClass_declaration(self, ctx: SystemVerilogParser.Class_declarationContext):
        self.translator.translate("class_decl", ctx)

    def exitGenvar_declaration(
        self, ctx: SystemVerilogParser.Genvar_declarationContext
    ):
        self.translator.translate("genvar_decl", ctx)

    def enterData_declaration(self, ctx: SystemVerilogParser.Data_declarationContext):
        self.translator.translate("data_decl", ctx)

    def exitData_declaration(self, ctx: SystemVerilogParser.Data_declarationContext):
        self.translator.exit("data_decl", ctx)

    def enterStruct_union_member(
        self, ctx: SystemVerilogParser.Struct_union_memberContext
    ):
        self.translator.translate("struct_union_member", ctx)

    # Exit a parse tree produced by SystemVerilogParser#struct_union_member.
    def exitStruct_union_member(
        self, ctx: SystemVerilogParser.Struct_union_memberContext
    ):
        self.translator.exit("struct_union_member", ctx)

    def enterEnum_name_declaration(
        self, ctx: SystemVerilogParser.Enum_name_declarationContext
    ):
        self.translator.translate("enum_name_decl", ctx)

    def exitEnum_name_declaration(
        self, ctx: SystemVerilogParser.Enum_name_declarationContext
    ):
        self.translator.exit("enum_name_decl", ctx)

    # Enter a parse tree produced by SystemVerilogParser#variable_decl_assignment.
    def enterVariable_decl_assignment(
        self, ctx: SystemVerilogParser.Variable_decl_assignmentContext
    ):
        self.translator.translate("var_decl", ctx)

    # Enter a parse tree produced by SystemVerilogParser#variable_decl_assignment.
    def exitVariable_decl_assignment(
        self, ctx: SystemVerilogParser.Variable_decl_assignmentContext
    ):
        self.translator.exit("var_decl", ctx)

    def enterNet_declaration(self, ctx: SystemVerilogParser.Net_declarationContext):
        self.translator.translate("net_decl", ctx)

    def exitNet_declaration(self, ctx: SystemVerilogParser.Net_declarationContext):
        self.translator.exit("net_decl", ctx)

    def enterAnsi_port_declaration(
        self, ctx: SystemVerilogParser.Ansi_port_declarationContext
    ):
        self.translator.translate("ansi_port_decl", ctx)

    def exitAnsi_port_declaration(
        self, ctx: SystemVerilogParser.Ansi_port_declarationContext
    ):
        self.translator.exit("ansi_port_decl", ctx)

    def exitPackage_import_declaration(
        self, ctx: SystemVerilogParser.Package_import_declarationContext
    ):
        self.translator.translate("package_import_decl", ctx)

    def enterTask_declaration(self, ctx: SystemVerilogParser.Task_declarationContext):
        self.translator.translate("task_body_decl", ctx.task_body_declaration())

    def exitTask_declaration(self, ctx: SystemVerilogParser.Task_declarationContext):
        self.translator.removeLastStructPointer()

    def enterFunction_declaration(
        self, ctx: SystemVerilogParser.Function_declarationContext
    ):
        self.translator.translate("task_body_decl", ctx.function_body_declaration())

    def exitFunction_declaration(
        self, ctx: SystemVerilogParser.Function_declarationContext
    ):
        self.translator.removeLastStructPointer()

    # =========================================================================================
    # JUMP
    # =========================================================================================

    def enterJump_statement(self, ctx: SystemVerilogParser.Jump_statementContext):
        if ctx.RETURN and ctx.expression():
            self.translator.translate("return", ctx.expression())

    def exitJump_statement(self, ctx: SystemVerilogParser.Jump_statementContext):
        if ctx.RETURN and ctx.expression():
            self.translator.exit("return", ctx.expression())

    # =========================================================================================
    # CALLS
    # =========================================================================================

    # Enter a parse tree produced by SystemVerilogParser#system_tf_call.
    def enterSystem_tf_call(self, ctx: SystemVerilogParser.System_tf_callContext):
        self.translator.translate("system_task_call", ctx)

    # Exit a parse tree produced by SystemVerilogParser#system_tf_call.
    def exitSystem_tf_call(self, ctx: SystemVerilogParser.System_tf_callContext):
        pass

    # Enter a parse tree produced by SystemVerilogParser#tf_call.
    def enterTf_call(self, ctx: SystemVerilogParser.Tf_callContext):
        self.translator.translate("task_call", ctx)

    # Exit a parse tree produced by SystemVerilogParser#tf_call.
    def exitTf_call(self, ctx: SystemVerilogParser.Tf_callContext):
        pass

    def exitModule_instantiation(
        self, ctx: SystemVerilogParser.Module_instantiationContext
    ):
        self.translator.translate("module_call", ctx)

    # Enter a parse tree produced by SystemVerilogParser#method_call_body.
    def enterMethod_call_body(self, ctx: SystemVerilogParser.Method_call_bodyContext):
        self.translator.translate("method_call", ctx)

    # Exit a parse tree produced by SystemVerilogParser#method_call_body.
    def exitMethod_call_body(self, ctx: SystemVerilogParser.Method_call_bodyContext):
        pass

    # =========================================================================================
    # ASSIGNMENTS
    # =========================================================================================

    # Enter a parse tree produced by SystemVerilogParser#expression.
    def enterExpression(self, ctx: SystemVerilogParser.ExpressionContext):
        self.translator.getTranslator("expr").insertOperator()
        pass

    # for ansiport
    def enterConstant_expression(
        self, ctx: SystemVerilogParser.Constant_expressionContext
    ):
        self.translator.getTranslator("expr").insertOperator()
        pass

    def enterNet_assignment(self, ctx: SystemVerilogParser.Net_assignmentContext):
        self.translator.translate("assignment", ctx)
        pass

    def exitNet_assignment(self, ctx: SystemVerilogParser.Net_assignmentContext):
        self.translator.exit("assignment", ctx)
        pass

    # <= in always
    def enterNonblocking_assignment(
        self, ctx: SystemVerilogParser.Nonblocking_assignmentContext
    ):
        self.translator.translate("assignment", ctx)

    def exitNonblocking_assignment(
        self, ctx: SystemVerilogParser.Nonblocking_assignmentContext
    ):
        self.translator.exit("assignment", ctx)
        pass

    # = in always
    def enterBlocking_assignment(
        self, ctx: SystemVerilogParser.Blocking_assignmentContext
    ):
        self.translator.translate("assignment", ctx)

    def exitBlocking_assignment(
        self, ctx: SystemVerilogParser.Blocking_assignmentContext
    ):
        self.translator.exit("assignment", ctx)

    def enterVariable_assignment(
        self, ctx: SystemVerilogParser.Variable_assignmentContext
    ):
        self.translator.translate("assignment", ctx)
        pass

    def exitVariable_assignment(
        self, ctx: SystemVerilogParser.Variable_assignmentContext
    ):
        self.translator.exit("assignment", ctx)
        pass

    def enterOperator_assignment(
        self, ctx: SystemVerilogParser.Operator_assignmentContext
    ):
        # self.translator.translate("assignment", ctx)
        pass

    def exitOperator_assignment(
        self, ctx: SystemVerilogParser.Operator_assignmentContext
    ):
        #  self.translator.exit("assignment", ctx)
        pass

    # =========================================================================================
    # PARAMETRS
    # =========================================================================================
    def exitLocal_parameter_declaration(
        self, ctx: SystemVerilogParser.Local_parameter_declarationContext
    ):
        self.translator.translate("params_assign", ctx)

    def exitParam_assignment(self, ctx: SystemVerilogParser.Param_assignmentContext):
        self.translator.translate("params_assign", ctx)

    def enterLoop_generate_construct(
        self, ctx: SystemVerilogParser.Loop_generate_constructContext
    ):
        self.translator.translate("generate_struct", ctx)

    def exitLoop_generate_construct(
        self, ctx: SystemVerilogParser.Loop_generate_constructContext
    ):
        self.translator.removeLastStructPointer()

    # =========================================================================================
    # ALWAYS
    # =========================================================================================
    def enterAlways_construct(self, ctx: SystemVerilogParser.Always_constructContext):
        self.translator.translate("alaways_struct", ctx)

    def exitAlways_construct(self, ctx: SystemVerilogParser.Always_constructContext):
        self.translator.removeLastStructPointer()

    # =========================================================================================
    # IF Statement
    # =========================================================================================
    def enterConditional_statement(
        self, ctx: SystemVerilogParser.Conditional_statementContext
    ):
        self.translator.translate("if_stmt", ctx)

    def exitConditional_statement(
        self, ctx: SystemVerilogParser.Conditional_statementContext
    ):
        self.translator.removeLastStructPointer()

    # =========================================================================================
    # COND PREDICATE
    # =========================================================================================
    def enterCond_predicate(self, ctx: SystemVerilogParser.Cond_predicateContext):
        self.translator.translate("if_cond_predicate", ctx)

    # =========================================================================================
    # SEQUENCE BLOCK CONTEXT
    # =========================================================================================
    def exitSeq_block(self, ctx: SystemVerilogParser.Seq_blockContext):
        self.translator.translate("if_seq_block", ctx)

    # =========================================================================================
    # CASE STATEMENT
    # =========================================================================================
    def enterCase_statement(self, ctx: SystemVerilogParser.Case_statementContext):
        self.translator.translate("case_stmt", ctx)

    def exitCase_statement(self, ctx: SystemVerilogParser.Case_statementContext):
        self.translator.removeLastStructPointer()

    # =========================================================================================
    # CASE ITEM
    # =========================================================================================
    def exitCase_item(self, ctx: SystemVerilogParser.Case_itemContext):
        self.translator.translate("case_item", ctx)

    # =========================================================================================
    # CASE ITEM EXPRESSION
    # =========================================================================================
    def enterCase_item_expression(
        self, ctx: SystemVerilogParser.Case_item_expressionContext
    ):
        self.translator.translate("case_item_expr", ctx)

    # =========================================================================================
    # ASSERT
    # =========================================================================================
    def enterAssert_property_statement(self, ctx):
        self.translator.translate("assert_property", ctx)

    def exitAssert_property_statement(self, ctx):
        self.translator.exit("assert_property", ctx)

    def enterSimple_immediate_assert_statement(
        self, ctx: SystemVerilogParser.Simple_immediate_assert_statementContext
    ):
        self.translator.translate("assert_block", ctx)

    def exitSimple_immediate_assert_statement(
        self, ctx: SystemVerilogParser.Simple_immediate_assert_statementContext
    ):
        self.translator.exit("assert_block", ctx)

    # =========================================================================================
    # INITIAL
    # =========================================================================================
    def enterInitial_construct(self, ctx: SystemVerilogParser.Initial_constructContext):
        self.translator.translate("initial", ctx)

    def exitInitial_construct(self, ctx: SystemVerilogParser.Initial_constructContext):
        self.translator.removeLastStructPointer()

    # =========================================================================================
    # LOOP
    # =========================================================================================
    def enterLoop_statement(self, ctx: SystemVerilogParser.Loop_statementContext):
        self.translator.translate("loop", ctx)

    def exitLoop_statement(self, ctx: SystemVerilogParser.Loop_statementContext):
        self.translator.translate("loop_iteration", ctx)
        self.translator.removeLastStructPointer()

    # =========================================================================================
    # Class
    # =========================================================================================

    def exitClass_constructor_declaration(
        self, ctx: SystemVerilogParser.Class_constructor_declarationContext
    ):
        self.translator.translate("task_body_decl", ctx)

    # Enter a parse tree produced by SystemVerilogParser#class_new.
    def enterClass_new(self, ctx: SystemVerilogParser.Class_newContext):
        self.translator.translate("class_new", ctx)

    # Exit a parse tree produced by SystemVerilogParser#class_new.
    def exitClass_new(self, ctx: SystemVerilogParser.Class_newContext):
        pass
