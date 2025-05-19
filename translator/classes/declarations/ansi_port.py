from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.module import Module
from translator.classes.base_translator import BaseTranslator
from translator.utils import module_call_resolve
from utils.string_formating import replaceValueParametrsCalls
from utils.utils import (
    dataTypeToStr,
    extractDimentionSize,
    extractVectorSize,
    vectorSize2AplanVectorSize,
)


class AnsiPortDeclTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Ansi_port_declarationContext):
        header = ctx.net_port_header().port_direction()
        unpacked_dimention = ctx.unpacked_dimension(0)
        dimension_size = 0
        dimension_size_expression = ""
        if unpacked_dimention is not None:
            dimension = unpacked_dimention.getText()
            dimension_size_expression = dimension
            dimension = replaceValueParametrsCalls(
                self.module.value_parametrs, dimension
            )
            dimension_size = extractDimentionSize(dimension)

        data_type = DeclTypes.INPORT
        if header.OUTPUT():
            data_type = DeclTypes.OUTPORT

        if header.INPUT():
            data_type = DeclTypes.INPORT

        port_type = ctx.net_port_header().net_port_type()

        port_data_type = port_type.data_type_or_implicit().data_type()

        port_dimention = None
        vector_size = None
        if port_data_type is not None:
            if DeclTypes.checkType(dataTypeToStr(port_data_type), []) == DeclTypes.NONE:
                self._translator_ptr.translate("interface_call", ctx)
                return

            port_dimention = port_data_type.packed_dimension(0)

            if port_dimention is not None:
                vector_size = port_dimention.getText()
        else:
            port_data_type = port_type.data_type_or_implicit().implicit_data_type()
            if port_data_type is not None:
                port_dimention = port_data_type.packed_dimension(0)
                if port_dimention is not None:
                    vector_size = port_dimention.getText()

        size_expression = ""
        if vector_size is not None:
            size_expression = vector_size
            vector_size = replaceValueParametrsCalls(
                self.module.value_parametrs, vector_size
            )
            vector_size = extractVectorSize(vector_size)

        aplan_vector_size = [0]

        if vector_size is not None:
            aplan_vector_size = vectorSize2AplanVectorSize(
                vector_size[0], vector_size[1]
            )

        assign_name = ""
        identifier = ctx.port_identifier().getText()
        port = Declaration(
            data_type,
            identifier,
            assign_name,
            size_expression,
            aplan_vector_size[0],
            dimension_size_expression,
            dimension_size,
            ctx.getSourceInterval(),
            name_space_level=self.getLastNameSpaceLevel(),
        )
        decl_unique, decl_index = self.module.declarations.addElement(port)

        constant_expression = ctx.constant_expression()
        if constant_expression is not None:
            expression = constant_expression.getText()
            (
                action_pointer,
                assign_name,
                source_interval,
                uniq_action,
            ) = self._translator_ptr.translate(
                "expr", ctx, ElementsTypes.ASSIGN_ELEMENT
            )
            declaration = self.module.declarations.getElementByIndex(decl_index)
            declaration.expression = assign_name
            declaration.action = action_pointer
