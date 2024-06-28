from typing import List
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.module_call import ModuleCall
from classes.protocols import Protocol
from program.program import Program
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import replace_filename
from utils.utils import Color, Counters_Object, printWithColor


def moduleCallAssign2Aplan(
    self: SV2aplan,
    ctx: SystemVerilogParser.Module_instantiationContext,
    destination_module_name: str,
):
    for hierarchical_instance in ctx.hierarchical_instance():
        instance = hierarchical_instance.name_of_instance().getText()
        index = instance.find("core")
        if index != -1:
            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
            call_assign_b = "MODULE_ASSIGN_B_{}".format(
                Counters_Object.getCounter(CounterTypes.B_COUNTER)
            )
            struct_call_assign = Protocol(
                call_assign_b,
                ctx.getSourceInterval(),
                ElementsTypes.MODULE_ASSIGN_ELEMENT,
            )

            for (
                order_port_connection
            ) in (
                hierarchical_instance.list_of_port_connections().ordered_port_connection()
            ):
                printWithColor(f"Unhandled case for module call", Color.RED)

            assign_str_list: List[str] = []
            for (
                named_port_connection
            ) in (
                hierarchical_instance.list_of_port_connections().named_port_connection()
            ):
                assign_str = "{0}.{1}={2}.{3}".format(
                    destination_module_name,
                    named_port_connection.port_identifier().getText(),
                    self.module.ident_uniq_name,
                    named_port_connection.expression().getText(),
                )
                assign_str_list.append(assign_str)

            action_name, source_interval = self.expression2Aplan(
                assign_str_list,
                ElementsTypes.ASSIGN_FOR_CALL_ELEMENT,
                ctx.getSourceInterval(),
            )
            action_name = f"Sensetive({action_name})"
            struct_call_assign.addBody((action_name, ElementsTypes.ACTION_ELEMENT))

            self.module.out_of_block_elements.addElement(struct_call_assign)


def moduleCall2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Module_instantiationContext,
    program: Program,
):
    from translator.translator import SystemVerilogFinder

    destination_identifier = ctx.module_identifier().getText()

    object_name = ""
    hierarchy = ctx.hierarchical_instance(0)
    if hierarchy is not None:
        object_name = hierarchy.name_of_instance().getText()

    parametrs = ctx.parameter_value_assignment()
    if parametrs is not None:
        parametrs = parametrs.getText()
    else:
        parametrs = ""

    parametrs = ctx.parameter_value_assignment()
    if parametrs is not None:
        parametrs = parametrs.getText()
    else:
        parametrs = ""

    module_call = ModuleCall(
        destination_identifier,
        object_name,
        self.module.identifier,
        destination_identifier,
        parametrs,
        self.module.parametrs,
    )
    call_module_name = object_name

    try:
        previous_file_path = program.file_path
        file_path = replace_filename(program.file_path, f"{destination_identifier}.sv")
        file_data = program.readFileData(file_path)
        finder = SystemVerilogFinder()
        finder.setUp(file_data)
        finder.startTranslate(program, module_call)
    except Exception as e:
        program.module_calls.addElement(module_call)

    program.file_path = previous_file_path
    moduleCallAssign2Aplan(self, ctx, call_module_name)
    Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
    call_b = "MODULE_CALL_B_{}".format(
        Counters_Object.getCounter(CounterTypes.B_COUNTER)
    )
    struct_call = Protocol(
        call_b, ctx.getSourceInterval(), ElementsTypes.MODULE_CALL_ELEMENT
    )
    struct_call.addBody(
        (f"call B_{call_module_name.upper()}", ElementsTypes.PROTOCOL_ELEMENT)
    )
    self.module.out_of_block_elements.addElement(struct_call)
