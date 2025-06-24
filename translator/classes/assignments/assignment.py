import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.protocols import BodyElement, Protocol
from translator.classes.base_translator import BaseTranslator


class AssignmentTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: (
            SystemVerilogParser.Nonblocking_assignmentContext
            | SystemVerilogParser.Net_assignmentContext
            | SystemVerilogParser.Variable_assignmentContext
            | SystemVerilogParser.Operator_assignmentContext
            | SystemVerilogParser.ExpressionContext
        ),
    ) -> None:
        element_type = ElementsTypes.ASSIGN_ELEMENT
        type_c = type(ctx)
        if (
            type_c is SystemVerilogParser.Nonblocking_assignmentContext
            or type_c is SystemVerilogParser.Net_assignmentContext
        ):
            element_type = ElementsTypes.ASSIGN_SENSETIVE_ELEMENT

        self.last_element_type = element_type

        self.last_operator = "="

        self._translator_ptr.translate(
            "expr",
            ctx,
        )

    def exit(
        self,
        ctx: (
            SystemVerilogParser.Nonblocking_assignmentContext
            | SystemVerilogParser.Net_assignmentContext
            | SystemVerilogParser.Variable_assignmentContext
            | SystemVerilogParser.Operator_assignmentContext
            | SystemVerilogParser.ExpressionContext
        ),
    ):
        self.findStruct()
        (
            action_pointer,
            action_name,
            source_interval,
            uniq_action,
        ) = self._translator_ptr.getTranslator("expr").exit()

        if not action_name:
            return

        protocol_params = self.getProtocolParams()
        assign_b = "{}_B".format(action_pointer.getName(to_upper=True))

        if self.last_struct:
            beh_index = self.last_struct.getLastBehaviorIndex()

            if beh_index is not None:
                self.last_struct.behavior[beh_index].addBodyElement(
                    BodyElement(
                        action_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                    )
                )
            else:
                b_index = self.last_struct.addProtocol(
                    assign_b,
                    inside_the_task=self.inside_the_task,
                    parametrs=protocol_params,
                )
                self.last_struct.behavior[b_index].addBodyElement(
                    BodyElement(
                        action_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                    )
                )
        else:
            struct_assign: Protocol = Protocol(
                assign_b,
                ctx.getSourceInterval(),
                ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT,
            )

            struct_assign.addBodyElement(
                BodyElement(action_name, action_pointer, ElementsTypes.ACTION_ELEMENT)
            )
            self.design_unit.out_of_block_elements.addElement(struct_assign)
