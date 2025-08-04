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
                self.design_unit.value_parametrs, dimension
            )
            dimension_size = self.utils.extractDimentionSize(dimension)

        data_type = DeclTypes.INPORT
        if header.OUTPUT():
            data_type = DeclTypes.OUTPORT

        if header.INPUT():
            data_type = DeclTypes.INPORT

        port_type: SystemVerilogParser.Net_port_typeContext = (
            ctx.net_port_header().net_port_type()
        )

        implicit_data_type_ctx: SystemVerilogParser.Data_type_or_implicitContext = (
            port_type.data_type_or_implicit()
        )
        port_data_type_ctx: SystemVerilogParser.Data_typeContext = (
            implicit_data_type_ctx.data_type()
        )
        port_dimention = None

        if port_data_type_ctx is not None:
            if (
                DeclTypes.checkType(
                    self._translator_ptr.getTranslator("data_decl").dataTypeToStr(
                        port_data_type_ctx
                    ),
                    [],
                )
                == DeclTypes.NONE
            ):
                self._translator_ptr.translate("interface_call", ctx)
                return

        # Визначаємо packed_dimension_ctx
        packed_dimension_ctx = None
        if port_data_type_ctx is not None:
            packed_dimension_ctx = port_data_type_ctx.packed_dimension(0)
        else:  # implicit_data_type може мати packed_dimension
            implicit_data_type_ctx = (
                port_type.data_type_or_implicit().implicit_data_type()
            )
            if implicit_data_type_ctx is not None:
                packed_dimension_ctx = implicit_data_type_ctx.packed_dimension(0)

        (
            size_expression,
            aplan_vector_size,
            dimension_size_expression,
            dimension_size,
            _,
        ) = self._process_dimensions(ctx.unpacked_dimension(0), packed_dimension_ctx)

        assign_name = ""
        identifier = ctx.port_identifier().getText()
        port = Declaration(
            data_type,
            identifier,
            assign_name,
            size_expression,
            aplan_vector_size,
            dimension_size_expression,
            dimension_size,
            ctx.getSourceInterval(),
            name_space_level=self.getLastNameSpaceLevel(),
        )

        decl_unique, self.decl_index = self.design_unit.declarations.addElement(port)

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
            declaration = self.design_unit.declarations.getElementByIndex(
                self.decl_index
            )
            declaration.expression = assign_name
            declaration.action = action_pointer
