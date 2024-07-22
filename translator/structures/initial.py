from antlr4_verilog.systemverilog import SystemVerilogParser

from classes.structure import Structure
from classes.element_types import ElementsTypes
from translator.system_verilog_to_aplan import SV2aplan


def initital2AplanImpl(
    self: SV2aplan, ctx: SystemVerilogParser.Initial_constructContext
):

    initial_name = self.module.ident_uniq_name_upper + "_" + "INITITAL"
    structure = Structure(
        initial_name,
        ctx.getSourceInterval(),
    )
    structure.addProtocol(initial_name)
    names_for_change = self.body2Aplan(ctx, structure, ElementsTypes.INITIAL_ELEMENT)
    for element in names_for_change:
        self.module.name_change.deleteElement(element)
    self.module.structures.addElement(structure)