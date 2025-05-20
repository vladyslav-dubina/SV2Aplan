from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator
from utils.utils import Counters_Object


class InBlockAssignmentTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(
        self,
        ctx: (
            SystemVerilogParser.Variable_decl_assignmentContext
            | SystemVerilogParser.Nonblocking_assignmentContext
            | SystemVerilogParser.Net_assignmentContext
            | SystemVerilogParser.Variable_assignmentContext
            | SystemVerilogParser.Operator_assignmentContext
            | SystemVerilogParser.ExpressionContext
        ),
    ) -> None:
        structure: Structure | None = self.structure_pointer_list.getLastElement()
        element_type = ElementsTypes.ASSIGN_ELEMENT
        if type(ctx) is SystemVerilogParser.Nonblocking_assignmentContext:
            element_type = ElementsTypes.ASSIGN_SENSETIVE_ELEMENT
        action_pointer, action_name, source_interval, uniq_action = (
            self._translator_ptr.translate(
                "expr",
                ctx,
                element_type,
                structure=structure,
            )
        )
        if action_name is not None:
            protocol_params = self.getProtocolParams()
            if structure:
                beh_index = structure.getLastBehaviorIndex()

                if beh_index is not None:
                    structure.behavior[beh_index].addBody(
                        BodyElement(
                            action_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                        )
                    )
                else:
                    Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                    b_index = structure.addProtocol(
                        "B_{0}".format(action_pointer.getName()),
                        inside_the_task=(
                            self.inside_the_task or self.inside_the_function
                        ),
                        parametrs=protocol_params,
                    )
                    structure.behavior[b_index].addBody(
                        BodyElement(
                            action_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                        )
                    )
            else:
                Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
                assign_b = "ASSIGN_B_{}".format(
                    Counters_Object.getCounter(CounterTypes.B_COUNTER)
                )
                struct_assign: Protocol = Protocol(
                    assign_b,
                    ctx.getSourceInterval(),
                    ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT,
                )
                struct_assign.addBody(
                    BodyElement(
                        action_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                    )
                )
                self.module.out_of_block_elements.addElement(struct_assign)
