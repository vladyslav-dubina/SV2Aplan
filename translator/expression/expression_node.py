import re
from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray, RangeTypes
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import (
    addEqueToBGET,
    parallelAssignment2Assignment,
    valuesToAplanStandart,
)


def identifier2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.IdentifierContext,
    destination_node_array: NodeArray,
):
    if destination_node_array is not None:
        identifier = self.module.name_change.changeNamesInStr(ctx.getText())

        index = destination_node_array.addElement(
            Node(identifier, ctx.getSourceInterval(), ElementsTypes.IDENTIFIER_ELEMENT)
        )
        node = destination_node_array.getElementByIndex(index)
        decl = self.module.declarations.getElement(node.identifier)
        if decl:
            node.module_name = self.module.ident_uniq_name


def number2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.NumberContext,
    destination_node_array: NodeArray,
):
    if destination_node_array is not None:
        value = valuesToAplanStandart(ctx.getText())
        index = destination_node_array.addElement(
            Node(value, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
        )
        node = destination_node_array.getElementByIndex(index)
        decl = self.module.declarations.getElement(node.identifier)
        if decl:
            node.module_name = self.module.ident_uniq_name


def bitSelection2AplanImpl(
    self: SV2aplan,
    ctx: (
        SystemVerilogParser.Bit_selectContext
        | SystemVerilogParser.Constant_bit_selectContext
    ),
    destination_node_array: NodeArray,
):
    if destination_node_array is not None:
        if isinstance(ctx, SystemVerilogParser.Bit_selectContext):
            expression = ctx.expression()
        if isinstance(ctx, SystemVerilogParser.Constant_bit_selectContext):
            expression = ctx.constant_expression()

        for element in expression:

            bit = element.getText()

            bit = self.module.name_change.changeNamesInStr(bit)

            if self.current_genvar_value is not None:
                (genvar, value) = self.current_genvar_value
                bit = re.sub(
                    r"\b{}\b".format(re.escape(genvar)),
                    f"{value}",
                    bit,
                )

            index = destination_node_array.addElement(
                Node(bit, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
            )
            node = destination_node_array.getElementByIndex(index)
            node.bit_selection = True
            decl = self.module.declarations.getElement(bit)

            if decl:
                node.module_name = self.module.ident_uniq_name


def rangeSelection2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Part_select_rangeContext,
    destination_node_array: NodeArray,
):
    if destination_node_array is not None:
        expressions = ctx.constant_range().constant_expression()
        for index, element in enumerate(expressions):
            if index != 0:
                range = ","
                destination_node_array.addElement(
                    Node(range, ctx.getSourceInterval(), ElementsTypes.OPERATOR_ELEMENT)
                )
                
            range = element.getText()
            node_index = destination_node_array.addElement(
                Node(range, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
            )
            node = destination_node_array.getElementByIndex(node_index)
            if len(ctx.constant_range().constant_expression()) == 1:
                node.range_selection = RangeTypes.START_END
            else:
                if index == 0:
                    node.range_selection = RangeTypes.START
                if index == len(ctx.constant_range().constant_expression()) - 1:
                    node.range_selection = RangeTypes.END


def operator2AplanImpl(
    self: SV2aplan,
    ctx: Tree.TerminalNodeImpl,
    destination_node_array: NodeArray,
):
    if destination_node_array is not None:
        operator = ctx.getText()
        if isNotUsedOperator(operator):
            return

        operator = parallelAssignment2Assignment(operator)

        index = destination_node_array.addElement(
            Node(operator, ctx.getSourceInterval(), ElementsTypes.OPERATOR_ELEMENT)
        )
        node = destination_node_array.getElementByIndex(index)
        decl = self.module.declarations.getElement(node.identifier)
        if decl:
            node.module_name = self.module.ident_uniq_name


unused_operators = "inputoutputbeginend[];intwirereg"


def isNotUsedOperator(operator: str):
    if operator in unused_operators:
        return True
    else:
        return False
