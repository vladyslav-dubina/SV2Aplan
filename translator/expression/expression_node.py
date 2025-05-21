import re
from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from classes.declarations import DeclTypes, Declaration
from classes.parametrs import Parametr
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray, RangeTypes
from translator.translator import Module_Translator
from utils.string_formating import (
    parallelAssignment2Assignment,
    replaceValueParametrsCalls,
    valuesToAplanStandart,
)




def identifier2AplanImpl(
    self: Module_Translator,
    ctx: SystemVerilogParser.IdentifierContext,
    destination_node_array: NodeArray,
):
    if destination_node_array is not None:

        identifier = ctx.getText()
        index = destination_node_array.addElement(
            Node(identifier, ctx.getSourceInterval(), ElementsTypes.IDENTIFIER_ELEMENT)
        )
        node = destination_node_array.getElementByIndex(index)

        identifier, decl = self.module.declarations.replaceDeclName(identifier)

        if isinstance(decl, Declaration):
            node.identifier = identifier
            if self.module.element_type == ElementsTypes.CLASS_ELEMENT:
                node.module_name = "object_pointer"
            else:
                node.module_name = self.module.ident_uniq_name

            if decl.data_type == DeclTypes.ARRAY:
                node.element_type = ElementsTypes.ARRAY_ELEMENT

        node.identifier = paramsCallReplace(self, node.identifier)


def number2AplanImpl(
    self: Module_Translator,
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

        node.identifier = paramsCallReplace(self, node.identifier)


def unpackedDimention2AplanImpl(
    self: Module_Translator,
    ctx: SystemVerilogParser.Unpacked_dimensionContext,
    destination_node_array: NodeArray,
):
    expression = ctx.constant_expression()
    if expression:
        expression = expression.getText()

        index = destination_node_array.addElement(
            Node(expression, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
        )
        node = destination_node_array.getElementByIndex(index)
        node.bit_selection = True

        expression, decl = self.module.declarations.replaceDeclName(expression)
        if isinstance(decl, Declaration):
            node.identifier = expression
            node.module_name = self.module.ident_uniq_name

        if self.current_genvar_value is not None:
            (genvar, value) = self.current_genvar_value
            node.identifier = re.sub(
                r"\b{}\b".format(re.escape(genvar)),
                f"{value}",
                node.identifier,
            )

        node.identifier = paramsCallReplace(self, node.identifier)


def bitSelection2AplanImpl(
    self: Module_Translator,
    ctx: (
        SystemVerilogParser.Bit_selectContext
        | SystemVerilogParser.Constant_bit_selectContext
    ),
    destination_node_array: NodeArray,
):
    if destination_node_array is not None:
        if isinstance(ctx, SystemVerilogParser.Bit_selectContext):
            expression = ctx.expression()
        elif isinstance(ctx, SystemVerilogParser.Constant_bit_selectContext):
            expression = ctx.constant_expression()

        for element in expression:

            bit = element.getText()

            index = destination_node_array.addElement(
                Node(bit, ctx.getSourceInterval(), ElementsTypes.NUMBER_ELEMENT)
            )
            node = destination_node_array.getElementByIndex(index)
            node.bit_selection = True

            bit, decl = self.module.declarations.replaceDeclName(bit)

            if isinstance(decl, Declaration):
                node.identifier = bit
                node.module_name = self.module.ident_uniq_name

            if self.current_genvar_value is not None:
                (genvar, value) = self.current_genvar_value
                node.identifier = re.sub(
                    r"\b{}\b".format(re.escape(genvar)),
                    f"{value}",
                    node.identifier,
                )

            node.identifier = paramsCallReplace(self, node.identifier)



