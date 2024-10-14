from typing import List, Tuple
from classes.actions import Action
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.parametrs import Parametr, ParametrArray
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from classes.typedef import Typedef
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


def createDeclaration(
    self: SV2aplan,
    name_part,
    type: DeclTypes,
    counter_type: CounterTypes,
    source_interval: Tuple[int, int],
    size_expression: str = "",
):

    decl = Declaration(
        type,
        "{0}_{1}".format(name_part, Counters_Object.getCounter(counter_type)),
        "",
        size_expression,
        0,
        "",
        0,
        source_interval,
    )
    uniq, index = self.module.declarations.addElement(decl)
    if uniq:
        Counters_Object.incrieseCounter(counter_type)

    return self.module.declarations.getElementByIndex(index)


def createParametrArray(self: SV2aplan, parametrs: List[str]):
    result: ParametrArray = ParametrArray()
    for element in parametrs:
        result.addElement(
            Parametr(
                element,
                "var",
            )
        )
    return result


def createTypedef(
    self: SV2aplan,
    identifier: str,
    source_interval: Tuple[int, int],
    arguments: List[Tuple[str, DeclTypes]],
):
    typedef = Typedef(
        identifier,
        identifier,
        source_interval,
        self.program.file_path,
        DeclTypes.STRUCT_TYPE,
    )

    element_source_interval = (0, 0)
    for element in arguments:
        new_decl = Declaration(
            element[1],
            element[0],
            "",
            "",
            0,
            "",
            0,
            element_source_interval,
        )
        element_source_interval = (
            element_source_interval[0],
            element_source_interval[1] + 1,
        )
        typedef.declarations.addElement(new_decl)

    if self.module:
        decl_unique, decl_index = self.module.typedefs.addElement(typedef)
    else:
        decl_unique, decl_index = self.program.typedefs.addElement(typedef)
