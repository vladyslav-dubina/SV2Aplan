from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.action_parametr import ActionParametr
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def returnToAssign2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.ExpressionContext,
    sv_structure: Structure | None = None,
):

    action_pointer, action_name, source_interval, uniq_action = self.expression2Aplan(
        ctx, ElementsTypes.ASSIGN_ELEMENT, sv_structure=sv_structure
    )

    task = self.module.tasks.getLastTask()

    return_var_name = f"return_{task.identifier}"
    task.parametrs.addElement(
        ActionParametr(
            f"{return_var_name}",
            "var",
        )
    )

    action_pointer.postcondition.elements.insert(
        0, Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT)
    )

    action_pointer.postcondition.elements.insert(
        0, Node(return_var_name, (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
    )

    action_pointer.parametrs.addElement(
        ActionParametr(
            f"{return_var_name}",
            "var",
        )
    )
    action_pointer.findParametrInBodyAndSetParametrs(task)
    action_parametrs_count = action_pointer.parametrs.getLen()
    action_name = f"{action_pointer.identifier}{action_pointer.parametrs.getIdentifiersListString(action_parametrs_count)}"
    
    beh_index = sv_structure.getLastBehaviorIndex()
    sv_structure.behavior[beh_index].addBody(
        (action_pointer, action_name, ElementsTypes.ACTION_ELEMENT)
    )
