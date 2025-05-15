from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.protocols import BodyElement
from classes.structure import Structure
from utils.utils import Counters_Object
from translator.translator import Translator


def createLoopBeh(self: Translator, loop_stmt: Structure, condition):

    protocol_params = self.getProtocolParams()

    loop_identifier = "{0}_{1}".format(
        loop_stmt.identifier,
        Counters_Object.getCounter(CounterTypes.LOOP_COUNTER) - 1,
    )
    iteration_name = "{0}_ITERATION".format(loop_identifier)

    body_name = "{0}_BODY".format(loop_identifier)

    loop_stmt.behavior[0].addBody(
        BodyElement(
            identifier=iteration_name,
            element_type=ElementsTypes.PROTOCOL_ELEMENT,
            parametrs=protocol_params,
        )
    )

    beh_index = loop_stmt.addProtocol(
        iteration_name,
        inside_the_task=(self.inside_the_task or self.inside_the_function),
    )

    
    (
        action_pointer,
        condition_name,
        source_interval,
        uniq_action,
    ) = self.expression2Aplan(condition, ElementsTypes.CONDITION_ELEMENT, loop_stmt)

    loop_stmt.behavior[beh_index].addBody(
        BodyElement(
            "{0}.({2}{1};{3}) + !{0}".format(
                condition_name,
                protocol_params if protocol_params is not None else "",
                body_name,
                iteration_name,
            ),
            action_pointer,
            ElementsTypes.ACTION_ELEMENT,
        )
    )

    beh_index = loop_stmt.addProtocol(
        body_name,
        inside_the_task=(self.inside_the_task or self.inside_the_function),
    )
