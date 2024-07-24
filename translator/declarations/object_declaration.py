from typing import Tuple
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from program.program import Program
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def objectDeclaration2AplanImpl(
    self: SV2aplan,
    class_name: str,
    identifier: str,
    source_interval: Tuple[int, int],
    program: Program,
):
    class_module = program.modules.findElement(class_name.upper())
    class_module = class_module.copy()
    index = program.modules.addElement(class_module)
    object = program.modules.getElementByIndex(index)
    object.element_type = ElementsTypes.OBJECT_ELEMENT
    object.identifier = class_name.upper()
    object.identifier_upper = object.identifier
    object.ident_uniq_name = identifier
    object.ident_uniq_name_upper = object.ident_uniq_name.upper()
    object.source_interval = source_interval
    object.replaceNamesInActions()
    object.setClassNumber(Counters_Object.getCounter(CounterTypes.OBJECT_COUNTER))
    Counters_Object.incrieseCounter(CounterTypes.OBJECT_COUNTER)
