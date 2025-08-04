import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.design_unit import DesignUnit
from translator.classes.base_translator import BaseTranslator


class InterfaceDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Interface_declarationContext) -> None:
        identifier = ctx.interface_ansi_header().interface_identifier().getText()
        (identifier, uniq_name) = self._translator_ptr.getTranslator(
            "module_call"
        ).resolve(identifier)
        index = self.design_units.addElement(
            DesignUnit(
                identifier,
                ctx.getSourceInterval(),
                uniq_name,
                ElementsTypes.INTERFACE_ELEMENT,
            )
        )
        self.design_unit = self.design_units.getElementByIndex(index)
