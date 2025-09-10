import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from Core.src.classes.structure import Structure
from translator.classes.base_translator import BaseTranslator


class InitialStructTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Initial_constructContext) -> None:
        initial_name = self.design_unit.ident_uniq_name_upper + "_" + "INITITAL"
        structure = Structure(
            initial_name,
            ctx.getSourceInterval(),
        )
        if self.design_unit.input_parametrs is not None:
            structure.parametrs += self.design_unit.input_parametrs
        structure.addProtocol(
            structure.getName(False),
            inside_the_task=self.inside_the_task,
        )

        self.design_unit.structures.addElement(structure)
        self.structure_pointer_list.addElement(structure)
