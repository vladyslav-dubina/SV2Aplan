import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.protocols import BodyElement, Protocol
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator
from utils.utils import Counters_Object


class InBlockAssignmentTranslator(BaseTranslator):
    element_type = ElementsTypes.ASSIGN_ELEMENT
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
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

        self.element_type = ElementsTypes.ASSIGN_ELEMENT
        if type(ctx) is SystemVerilogParser.Nonblocking_assignmentContext:
            self.element_type = ElementsTypes.ASSIGN_SENSETIVE_ELEMENT

        self._translator_ptr.translate("expr", ctx, self.element_type)

    def exit(
        self,
        ctx: (
            SystemVerilogParser.Variable_decl_assignmentContext
            | SystemVerilogParser.Nonblocking_assignmentContext
            | SystemVerilogParser.Net_assignmentContext
            | SystemVerilogParser.Variable_assignmentContext
            | SystemVerilogParser.Operator_assignmentContext
            | SystemVerilogParser.ExpressionContext
        ),
    ):
        self.findStruct()

        action_pointer, action_name, source_interval, uniq_action = (
            self._translator_ptr.getTranslator("expr").exit(self.element_type)
        )

        if action_name is not None:
            protocol_params = self.getProtocolParams()
            if self.last_struct:
                beh_index = self.last_struct.getLastBehaviorIndex()

                if beh_index is not None:
                    self.last_struct.behavior[beh_index].addBody(
                        BodyElement(
                            action_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                        )
                    )
                else:
                    b_index = self.last_struct.addProtocol(
                        "B_{0}".format(action_pointer.getName()),
                        inside_the_task=self.inside_the_task,
                        parametrs=protocol_params,
                    )
                    self.last_struct.behavior[b_index].addBody(
                        BodyElement(
                            action_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                        )
                    )
            else:
                assign_b = "ASSIGN_B_{}".format(
                    Counters_Object.getCounter(CounterTypes.STRUCT_COUNTER)
                )
                Counters_Object.incrieseCounter(CounterTypes.STRUCT_COUNTER)
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
