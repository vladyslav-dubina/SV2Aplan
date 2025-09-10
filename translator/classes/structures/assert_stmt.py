import typing
from antlr4_verilog.systemverilog import SystemVerilogParser

from Core.src.classes.element_types import ElementsTypes
from Core.src.classes.protocols import BodyElement, Protocol
from translator.classes.base_translator import BaseTranslator


class AssertPropertyTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self, ctx: SystemVerilogParser.Assert_property_statementContext
    ) -> None:
        expression = ctx.property_spec()
        if not expression:
            return

        self.last_element_type = ElementsTypes.ASSERT_ELEMENT
        self.last_operator = None
        self._translator_ptr.translate("expr", expression)

    def exit(self, ctx: SystemVerilogParser.Assert_property_statementContext) -> None:
        expression = ctx.property_spec()
        if not expression:
            return

        (
            action_pointer,
            assert_name,
            source_interval,
            uniq_action,
        ) = self._translator_ptr.getTranslator("expr").exit()

        if not assert_name:
            return

        assert_b = "ASSERT_B_{}".format(
            self.counters.get(self.counters.types.ASSERT_COUNTER)
        )
        self.counters.incriese(self.counters.types.ASSERT_COUNTER)
        struct_assert = Protocol(
            assert_b,
            ctx.getSourceInterval(),
        )

        struct_assert.addBodyElement(
            BodyElement(
                "{0}.Delta + !{0}.0".format(assert_name),
                action_pointer,
                ElementsTypes.ACTION_ELEMENT,
            )
        )
        self.design_unit.out_of_block_elements.addElement(struct_assert)


class AssertInBlockTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self, ctx: SystemVerilogParser.Simple_immediate_assert_statementContext
    ) -> None:
        expression = ctx.expression()
        if not expression:
            return

        self.last_element_type = ElementsTypes.ASSERT_ELEMENT
        self.last_operator = None
        self._translator_ptr.translate("expr", expression)

    def exit(
        self, ctx: SystemVerilogParser.Simple_immediate_assert_statementContext
    ) -> None:
        self.findStruct()
        (
            action_pointer,
            assert_name,
            source_interval,
            uniq_action,
        ) = self._translator_ptr.getTranslator("expr").exit(
            ElementsTypes.ASSERT_ELEMENT
        )
        if not assert_name:
            return

        protocol_params = ""
        if self.inside_the_task == True:
            task = self.design_unit.tasks.getLastTask()
            if task is not None:
                protocol_params = "({0})".format(task.parametrs)
        assert_b = "ASSERT_B_{0}_{1}{2}".format(
            self.last_struct.number,
            self.counters.get(self.counters.types.ASSERT_COUNTER),
            protocol_params,
        )

        self.counters.incriese(self.counters.types.ASSERT_COUNTER)
        beh_index = self.last_struct.addProtocol(
            assert_b,
            inside_the_task=self.inside_the_task,
        )
        self.last_struct.behavior[beh_index].addBodyElement(
            BodyElement(
                "{0}.Delta + !{0}.0".format(assert_name),
                action_pointer,
                ElementsTypes.ACTION_ELEMENT,
            )
        )
        if beh_index != 0:
            self.last_struct.behavior[beh_index - 1].addBodyElement(
                BodyElement(assert_b, action_pointer, ElementsTypes.PROTOCOL_ELEMENT)
            )
