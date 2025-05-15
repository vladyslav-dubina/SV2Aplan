from antlr4_verilog.systemverilog import (
    SystemVerilogParserListener,
    SystemVerilogParser,
)

from classes.counters import CounterTypes
from classes.module_call import ModuleCall
from translator.translator import Translator
from utils.utils import Counters_Object


class SVToAplanListener(SystemVerilogParserListener):

    translator = Translator()

    def __init__(self, module_call: ModuleCall | None = None):
        self.translator.module_call = module_call

    # DECLARATIONS

    def enterInterface_declaration(
        self, ctx: SystemVerilogParser.Interface_declarationContext
    ):
        self.translator.interface_decl_translator.translate(ctx)

    def enterModule_declaration(
        self, ctx: SystemVerilogParser.Module_declarationContext
    ):
        self.translator.module_decl_translator.translate(ctx)
        # body_run(ctx)
        Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)  # ???

    def enterPackage_declaration(
        self, ctx: SystemVerilogParser.Package_declarationContext
    ):
        self.translator.package_decl_translator.translate(ctx)

    def exitGenvar_declaration(
        self, ctx: SystemVerilogParser.Genvar_declarationContext
    ):
        self.translator.genvar_decl_translator.translate(ctx)

    def exitData_declaration(self, ctx: SystemVerilogParser.Data_declarationContext):
        self.translator.data_decl_translator.translate(ctx)

    def exitNet_declaration(self, ctx: SystemVerilogParser.Net_declarationContext):
        self.translator.net_decl_translator.translate(ctx)
