from antlr4_verilog.systemverilog import (
    SystemVerilogParserListener,
    SystemVerilogParser,
)
from classes.counters import CounterTypes


from translator.classes.structures.loops.forever import foreverIteration2AplanImpl
from utils.utils import Counters_Object
from translator.declarations.class_declaration import classDeclaration2Aplan
from translator.declarations.interface_declaration import interfaceDeclaration2Aplan
from translator.declarations.module_declaration import moduleDeclaration2Aplan
from translator.declarations.package_declaration import packageDeclaration2Aplan
from translator.translator import (
    Module_Translator,
)
from classes.module import Module
from classes.module import Module
from classes.module_call import ModuleCall


def body_run(ctx):
    if ctx.getChildCount() == 0:
        return
    for child in ctx.getChildren():
        print(type(child), child.getText())
        body_run(child)


class SVToAplanListener(SystemVerilogParserListener):
    def __init__(self, module_call: ModuleCall | None = None):

        self.module: Module = None
        self.translator: Module_Translator = Module_Translator(None, program)
        self.module_call: ModuleCall | None = module_call




