from antlr4_verilog.systemverilog import SystemVerilogParser

from classes.element_types import ElementsTypes
from classes.module import Module
from translator.classes.base_translator import BaseTranslator


class ClassDeclTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Class_declarationContext,
    ) -> Module | None:
        module: Module | None = None
        for element in ctx.class_identifier():
            identifier = element.identifier().getText()

            (identifier, uniq_name) = self._translator_ptr.getTranslator(
                "module_call"
            ).resolve(identifier)
            index = self._program.modules.addElement(
                Module(
                    identifier,
                    ctx.getSourceInterval(),
                    uniq_name,
                    ElementsTypes.CLASS_ELEMENT,
                )
            )
            module = self._program.modules.getElementByIndex(index)
        return module
