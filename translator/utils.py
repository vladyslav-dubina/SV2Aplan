from classes.actions import Action
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.parametrs import ParametrArray
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def createProtocol(
    self: SV2aplan,
    action_pointer: Action,
    body: str,
    action_name: str,
    parametrs: ParametrArray = ParametrArray(),
    sv_structure: Structure | None = None,
):

    if sv_structure is not None:
        beh_index = sv_structure.getLastBehaviorIndex()

        sv_structure.elements.addElement(action_pointer)

        if beh_index is not None:
            sv_structure.behavior[beh_index].addBody(
                BodyElement(
                    body,
                    action_pointer,
                    ElementsTypes.ACTION_ELEMENT,
                    parametrs=parametrs,
                )
            )
        else:
            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
            b_index = sv_structure.addProtocol(
                "B_{0}".format(action_pointer.getName()),
                inside_the_task=(self.inside_the_task or self.inside_the_function),
                parametrs=action_pointer.parametrs,
            )
            sv_structure.behavior[b_index].addBody(
                BodyElement(
                    body,
                    action_pointer,
                    ElementsTypes.ACTION_ELEMENT,
                    parametrs=parametrs,
                )
            )
    else:
        protocol_name = "{0}".format(action_name.upper())
        protocol: Protocol | None = self.module.out_of_block_elements.findElement(
            protocol_name
        )
        if isinstance(protocol, Protocol):
            protocol.addBody(
                BodyElement(
                    action_pointer.identifier,
                    action_pointer,
                    ElementsTypes.ACTION_ELEMENT,
                    parametrs=parametrs,
                )
            )
        else:
            protocol = Protocol(
                protocol_name,
                (0, 0),
                parametrs=action_pointer.parametrs,
            )

            protocol.addBody(
                BodyElement(
                    action_pointer.identifier,
                    action_pointer,
                    ElementsTypes.ACTION_ELEMENT,
                    parametrs=parametrs,
                )
            )

            if parametrs:
                protocol.parametrs += parametrs

            self.module.out_of_block_elements.addElement(protocol)
