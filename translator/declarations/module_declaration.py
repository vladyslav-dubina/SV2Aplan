from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.module import Module
from program.program import Program
from classes.module_call import ModuleCall


def moduleDeclaration2Aplan(
    ctx: SystemVerilogParser.Module_declarationContext,
    program: Program,
    module_call: ModuleCall,
):
    """The function `moduleDeclaration2Aplan` parses a SystemVerilog module declaration and adds it to a
    program object.

    Parameters
    ----------
    ctx : SystemVerilogParser.Module_declarationContext
        The `ctx` parameter in the `moduleDeclaration2Aplan` function is of type
    `SystemVerilogParser.Module_declarationContext`. This parameter represents the context of the module
    declaration in the SystemVerilog code being parsed. It contains information about the module
    declaration such as the module identifier, parameters,
    program : Program
        The `program` parameter in the `moduleDeclaration2Aplan` function is an instance of the `Program`
    class. It is used to store information about the program being parsed, such as modules, module
    calls, etc. This parameter allows the function to interact with the program data structure and
    update
    module_call : ModuleCall
        The `module_call` parameter in the `moduleDeclaration2Aplan` function is an instance of the
    `ModuleCall` class. It is used to represent a call to a module within the program. The function
    checks if a module call exists in the program based on the identifier provided in the context

    Returns
    -------
        The function `moduleDeclaration2Aplan` is returning the `module` object that is created within the
    function.

    """
    module = None
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

    return module
