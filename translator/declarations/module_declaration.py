from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.module import Module
from program.program import Program
from classes.module_call import ModuleCall


def moduleOrPackageDeclaration2Aplan(
    ctx: (
        SystemVerilogParser.Module_declarationContext
        | SystemVerilogParser.Package_declarationContext
    ),
    program: Program,
    module_call: ModuleCall,
):
    module = None
    if isinstance(ctx, SystemVerilogParser.Module_declarationContext):

        if ctx.module_ansi_header() is not None:
            identifier = ctx.module_ansi_header().module_identifier().getText()
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
                Module(identifier, ctx.getSourceInterval(), uniq_name)
            )
            module = program.modules.getElementByIndex(index)

    elif isinstance(ctx, SystemVerilogParser.Package_declarationContext):
        for element in ctx.package_identifier():
            identifier = element.getText()
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
                Module(identifier, ctx.getSourceInterval(), uniq_name)
            )
            module = program.modules.getElementByIndex(index)
    return module
