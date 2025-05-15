from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.element_types import ElementsTypes
from classes.module import Module
from translator.classes.base_translator import BaseTranslator
from translator.utils import module_call_resolve


class InterfaceDeclTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(
        self, ctx: SystemVerilogParser.Interface_declarationContext
    ) -> Module:
        identifier = ctx.interface_ansi_header().interface_identifier().getText()
        (identifier, uniq_name) = module_call_resolve(self.module_call, identifier)
        index = self.modules.addElement(
            Module(
                identifier,
                ctx.getSourceInterval(),
                uniq_name,
                ElementsTypes.INTERFACE_ELEMENT,
            )
        )
        module = self.modules.getElementByIndex(index)

        return module
