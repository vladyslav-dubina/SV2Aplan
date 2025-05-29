import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator


class InitialStructTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

       from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Initial_constructContext) -> None:

        initial_name = self.module.ident_uniq_name_upper + "_" + "INITITAL"
        structure = Structure(
            initial_name,
            ctx.getSourceInterval(),
        )
        if self.module.input_parametrs is not None:
            structure.parametrs += self.module.input_parametrs
        structure.addProtocol(
            initial_name,
            inside_the_task=self.inside_the_task,
        )

        self.module.structures.addElement(structure)
        self.structure_pointer_list.addElement(structure)
