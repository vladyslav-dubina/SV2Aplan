from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from translator.system_verilog_to_aplan import SV2aplan


def identifier2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.IdentifierContext,
    destination_action_node_part: NodeArray,
):
    index = destination_action_node_part.addElement(
        Node(ctx.getText(), ctx.getSourceInterval(), ElementsTypes.IDENTIFIER_ELEMENT)
    )
    node = destination_action_node_part.getElementByIndex(index)
    decl = self.module.declarations.getElement(node.identifier)
    if decl:
        node.module_name = self.module.ident_uniq_name


def number2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.NumberContext,
    destination_action_node_part: NodeArray,
):
    index = destination_action_node_part.addElement(
        Node(ctx.getText(), ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
    )
    node = destination_action_node_part.getElementByIndex(index)
    decl = self.module.declarations.getElement(node.identifier)
    if decl:
        node.module_name = self.module.ident_uniq_name


def operator2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Binary_operatorContext,
    destination_action_node_part: NodeArray,
):
    operator = ctx.getText()
    if "input" in operator or "output" in operator:
        return
    index = destination_action_node_part.addElement(
        Node(operator, ctx.getSourceInterval(), ElementsTypes.OPERATOR_ELEMENT)
    )
    node = destination_action_node_part.getElementByIndex(index)
    decl = self.module.declarations.getElement(node.identifier)
    if decl:
        node.module_name = self.module.ident_uniq_name
