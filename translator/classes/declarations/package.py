import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.design_unit import DesignUnit
from translator.classes.base_translator import BaseTranslator


class PackageDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Package_declarationContext) -> None:
        for element in ctx.package_identifier():
            identifier = element.getText()
            (identifier, uniq_name) = self._translator_ptr.getTranslator(
                "design_unit_call"
            ).resolve(identifier)
            index = self.design_units.addElement(
                DesignUnit(
                    identifier,
                    ctx.getSourceInterval(),
                    uniq_name,
                    ElementsTypes.PACKAGE_ELEMENT,
                )
            )
            self.design_unit = self.design_units.getElementByIndex(index)
