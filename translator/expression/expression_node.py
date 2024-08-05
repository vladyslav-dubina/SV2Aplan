import re
from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import addEqueToBGET, valuesToAplanStandart


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
            node = destination_node_array.getElementByIndex(
                destination_node_array.getLen() - 1
            )
            bit = element.getText()
            if self.current_genvar_value is not None:
                (genvar, value) = self.current_genvar_value
                bit = re.sub(
                    r"\b{}\b".format(re.escape(genvar)),
                    f"{value}",
                    bit,
                )
            node.bit_selection = bit


def rangeSelection2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Part_select_rangeContext,
    destination_node_array: NodeArray,
):
    if destination_node_array is not None:
        node = destination_node_array.getElementByIndex(
            destination_node_array.getLen() - 1
        )

        range = ""
        for index, element in enumerate(ctx.constant_range().constant_expression()):
            if index != 0:
                range = "," + range
            range = element.getText() + range
        node.range_selection = range


def operator2AplanImpl(
    self: SV2aplan,
    ctx: Tree.TerminalNodeImpl,
    destination_node_array: NodeArray,
):
    if destination_node_array is not None:
        operator = ctx.getText()
        if isNotUsedOperator(operator):
            return
        index = destination_node_array.addElement(
            Node(operator, ctx.getSourceInterval(), ElementsTypes.OPERATOR_ELEMENT)
        )
        node = destination_node_array.getElementByIndex(index)
        decl = self.module.declarations.getElement(node.identifier)
        if decl:
            node.module_name = self.module.ident_uniq_name


unused_operators = "inputoutputbeginend[];"


def isNotUsedOperator(operator: str):

    if operator in unused_operators:
        return True
    else:
        return False
