from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.element_types import ElementsTypes
from classes.module import Module
from program.program import Program
from classes.module_call import ModuleCall
from translator.utils import module_call_resolve


def classDeclaration2Aplan(
    ctx: SystemVerilogParser.Class_declarationContext,
    program: Program,
    module_call: ModuleCall,
):
    module = None
    for element in ctx.class_identifier():
        identifier = element.identifier().getText()

        (identifier, uniq_name) = module_call_resolve(module_call, identifier)
        index = program.modules.addElement(
            Module(
                identifier,
                ctx.getSourceInterval(),
                uniq_name,
                ElementsTypes.CLASS_ELEMENT,
            )
        )
        module = program.modules.getElementByIndex(index)
    return module
