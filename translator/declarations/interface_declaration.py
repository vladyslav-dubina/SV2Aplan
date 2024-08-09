from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.element_types import ElementsTypes
from classes.module import Module
from program.program import Program
from classes.module_call import ModuleCall


def interfaceDeclaration2Aplan(
    ctx: SystemVerilogParser.Interface_declarationContext,
    program: Program,
    module_call: ModuleCall,
):
    identifier = ctx.interface_ansi_header().interface_identifier().getText()
    local_module_call: ModuleCall = None
    uniq_name = identifier
    if module_call is not None:
        local_module_call = module_call
    else:
        local_module_call = program.module_calls.findElement(identifier)
    if local_module_call is not None:
        if identifier == local_module_call.identifier:
            identifier = local_module_call.identifier
            uniq_name = local_module_call.object_name
    index = program.modules.addElement(
        Module(
            identifier,
            ctx.getSourceInterval(),
            uniq_name,
            ElementsTypes.INTERFACE_ELEMENT,
        )
    )
    module = program.modules.getElementByIndex(index)

    return module
