import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.loop_stmt import LoopStmt
from classes.protocols import BodyElement
from classes.structure import Structure
from utils.string_formating import replaceValueParametrsCalls
from utils.utils import Counters_Object
from antlr4_verilog.systemverilog import SystemVerilogParser
from translator.classes.base_translator import BaseTranslator


class RepeatStructTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self,
        ctx: SystemVerilogParser.Loop_statementContext,
    ) -> None:
        self.findStruct()
        if not isinstance(self.last_struct, Structure):
            return
        identifier = "repeat_var_{0}".format(
            Counters_Object.getCounter(CounterTypes.STRUCT_COUNTER)
        )
        expression = ctx.expression().getText()
        expression_source_interval = ctx.expression().getSourceInterval()
        expression = replaceValueParametrsCalls(self.module.value_parametrs, expression)

        assing_expr = "{0} = {1}".format(identifier, 0)

        uniq, decl_index = self.module.declarations.addElement(
            Declaration(
                DeclTypes.INT,
                identifier,
                "",
                "",
                0,
                "",
                0,
                source_interval=ctx.getSourceInterval(),
                element_type=ElementsTypes.NONE_ELEMENT,
                name_space_level=self.getLastNameSpaceLevel(),
            )
        )

        (
            action_pointer,
            assign_name,
            source_interval,
            uniq_action,
        ) = self._translator_ptr.getTranslator("expr").actionFromNodeStr(
            self,
            assing_expr,
            ctx.getSourceInterval(),
            ElementsTypes.ASSIGN_ELEMENT,
            sv_structure=self.last_struct,
        )

        decl = self.module.declarations.getElementByIndex(decl_index)

        decl.action = action_pointer

        self.last_struct.elements.addElement(decl)

        beh_index = self.last_struct.getLastBehaviorIndex()
        if beh_index is not None:
            self.last_struct.behavior[beh_index].addBody(
                BodyElement(assign_name, action_pointer, ElementsTypes.ACTION_ELEMENT)
            )
        else:
            raise ValueError("sv_structure is empty")

        self.createStatement("REPEAT_LOOP", ElementsTypes.LOOP_ELEMENT)
        self.findStruct()
        if not isinstance(self.last_struct, LoopStmt):
            return

        repeat_iteration = "REPEAT_ITERATION_{}".format(
            Counters_Object.getCounter(CounterTypes.STRUCT_COUNTER)
        )

        condition_expr = "{0} < {1}".format(decl.identifier, expression)
        (
            action_pointer,
            assign_name,
            source_interval,
            uniq_action,
        ) = self._translator_ptr.getTranslator("expr").actionFromNodeStr(
            self,
            condition_expr,
            expression_source_interval,
            ElementsTypes.CONDITION_ELEMENT,
            sv_structure=self.last_struct,
        )

        beh_index = self.last_struct.getLastBehaviorIndex()
        self.last_struct.behavior[beh_index].addBody(
            BodyElement(
                "{0}.{1} + !{0}".format(assign_name, repeat_iteration),
                action_pointer,
                ElementsTypes.ACTION_ELEMENT,
            )
        )

        repeat_iteration = "REPEAT_ITERATION_{}".format(
            Counters_Object.getCounter(CounterTypes.STRUCT_COUNTER)
        )

        increase_expr = "{0} = {0} + 1".format(identifier)
        (
            action_pointer,
            assign_name,
            source_interval,
            uniq_action,
        ) = self._translator_ptr.getTranslator("expr").actionFromNodeStr(
            self,
            increase_expr,
            ctx.getSourceInterval(),
            ElementsTypes.REPEAT_ELEMENT,
            sv_structure=self.last_struct,
        )

        sensetive = self.extractSensetive(ctx.statement_or_null())
        protocol_call = "Sensetive({0}, {1})".format(
            self.last_struct.getName(), sensetive
        )

        beh_index = self.last_struct.addProtocol(
            repeat_iteration,
            inside_the_task=self.inside_the_task,
        )

        self.last_struct.behavior[beh_index].addBody(
            BodyElement(
                "{0}.{1}".format(assign_name, protocol_call),
                action_pointer,
                ElementsTypes.ACTION_ELEMENT,
            )
        )

        copy = self.last_struct.behavior[beh_index].copy()
        self.last_struct.behavior[beh_index] = self.last_struct.behavior[
            beh_index - 1
        ].copy()
        self.last_struct.behavior[beh_index - 1] = copy

        self._translator_ptr.body2Aplan(ctx.statement_or_null(), self.last_struct)
