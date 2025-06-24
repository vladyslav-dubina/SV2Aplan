import re
import typing
import antlr4
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.declarations import Declaration
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.node import Node
from translator.classes.base_translator import BaseTranslator


class VariableLValueTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Variable_lvalueContext,
    ) -> None:
        self.last_dot_operator = "."

    def exit(self, ctx) -> None:
        pass

    # self.last_dot_operator = None
