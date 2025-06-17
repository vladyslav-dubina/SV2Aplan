import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.declarations import DeclTypes, Declaration
from AppModule.app.classes.element_types import ElementsTypes
from translator.classes.base_translator import BaseTranslator


class AnsiPortDeclTranslator(BaseTranslator):
    decl_index = None

    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Ansi_port_declarationContext):
        header = ctx.net_port_header().port_direction()
        unpacked_dimention = ctx.unpacked_dimension(0)
        dimension_size = 0
        dimension_size_expression = ""
        if unpacked_dimention is not None:
            dimension = unpacked_dimention.getText()
            dimension_size_expression = dimension
            dimension = self.str_formater.replaceValueParametrsCalls(
                self.module.value_parametrs, dimension
            )
            dimension_size = self.utils.extractDimentionSize(dimension)

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
            if DeclTypes.checkType(self.utils.dataTypeToStr(port_data_type), []) == DeclTypes.NONE:
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
            vector_size = self.str_formater.replaceValueParametrsCalls(
                self.module.value_parametrs, vector_size
            )
            vector_size = self.utils.extractVectorSize(vector_size)

        aplan_vector_size = [0]

        if vector_size is not None:
            aplan_vector_size = self.utils.vectorSize2AplanVectorSize(
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
        decl_unique, self.decl_index = self.module.declarations.addElement(port)

        constant_expression = ctx.constant_expression()
        if constant_expression is None:
            return

        self.last_element_type = ElementsTypes.ASSIGN_ELEMENT
        self.last_operator = "="
        self._translator_ptr.translate(
            "expr",
            ctx,
        )

    def exit(self, ctx: SystemVerilogParser.Ansi_port_declarationContext) -> None:
        constant_expression = ctx.constant_expression()
        if constant_expression is not None:

            (
                action_pointer,
                assign_name,
                source_interval,
                uniq_action,
            ) = self._translator_ptr.getTranslator("expr").exit()
            declaration = self.module.declarations.getElementByIndex(self.decl_index)
            declaration.expression = assign_name
            declaration.action = action_pointer
