import typing
from antlr4_verilog.systemverilog import SystemVerilogParser

from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.design_unit import DesignUnit
from translator.classes.base_translator import BaseTranslator


class ClassDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Class_declarationContext,
    ) -> None:

        for element in ctx.class_identifier():
            identifier = element.identifier().getText()

            (identifier, uniq_name) = self._translator_ptr.getTranslator(
                "module_call"
            ).resolve(identifier)
            index = self._program.design_units.addElement(
                DesignUnit(
                    identifier,
                    ctx.getSourceInterval(),
                    uniq_name,
                    ElementsTypes.CLASS_ELEMENT,
                )
            )
            self.design_unit = self._program.design_units.getElementByIndex(index)
