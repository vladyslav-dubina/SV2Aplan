import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.element_types import ElementsTypes
from classes.loop_stmt import LoopStmt
from classes.processed import ProcessedElement
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.classes.base_translator import BaseTranslator
from utils.string_formating import (
    parallelAssignment2Assignment,
    replace_cpp_operators,
    replaceValueParametrsCalls,
)
from utils.utils import Counters_Object


class GenerateStructTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

       from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self, ctx: SystemVerilogParser.Loop_generate_constructContext
    ) -> None:

        generate_name = (
            "GENERATE"
            + "_"
            + str(Counters_Object.getCounter(CounterTypes.LOOP_COUNTER))
        )

        self.createStatement("GENERATE_LOOP", ElementsTypes.LOOP_ELEMENT)
        self.findStruct()
        if not isinstance(self.last_struct, LoopStmt):
            return

        generate_name = "{0}_{1}".format(
            self.last_struct.identifier,
            Counters_Object.getCounter(CounterTypes.LOOP_COUNTER) - 1,
        )

        if self.module.input_parametrs is not None:
            self.last_struct.parametrs += self.module.input_parametrs
        self.last_struct.addProtocol(
            generate_name,
            ElementsTypes.GENERATE_ELEMENT,
            inside_the_task=(self.inside_the_task or self.inside_the_function),
        )
        initialization = ctx.genvar_initialization().getText()
        initialization = self.prepareGenerateExpression(initialization)

        condition = ctx.genvar_expression().getText()
        condition = self.prepareGenerateExpression(condition)

        iteration = ctx.genvar_iteration().getText()
        iteration = self.prepareGenerateExpression(iteration)
        init_var_name = initialization.split("=")[0]
        exec(initialization)
        while eval(condition):
            current_value = eval(init_var_name)
            self.generateBodyToAplan(
                self,
                ctx.generate_block(),
                self.last_struct,
                init_var_name,
                current_value,
            )
            exec(iteration)
        self.module.structures.addElement(self.last_struct)

    def generateBodyToAplan(
        self,
        structure: Structure,
        ctx: SystemVerilogParser.Generate_blockContext,
        init_var_name,
        current_value,
    ):
        if ctx.getChildCount() == 0:
            return

        for child in ctx.getChildren():
            if (
                type(child) is SystemVerilogParser.Variable_decl_assignmentContext
                or type(child) is SystemVerilogParser.Nonblocking_assignmentContext
                or type(child) is SystemVerilogParser.Net_assignmentContext
                or type(child) is SystemVerilogParser.Variable_assignmentContext
            ):
                self.current_genvar_value = (init_var_name, current_value)
                self.module.processed_elements.addElement(
                    ProcessedElement("action", child.getSourceInterval())
                )
                (
                    action_pointer,
                    action_name,
                    source_interval,
                    uniq_action,
                ) = self._translator_ptr.translate(
                    "expr",
                    child,
                    ElementsTypes.ASSIGN_SENSETIVE_ELEMENT,
                    sv_structure=structure,
                )

                self.current_genvar_value = None
                if action_name:

                    structure.behavior[0].addBody(
                        BodyElement(
                            action_name, action_pointer, ElementsTypes.ACTION_ELEMENT
                        )
                    )

            else:
                self.generateBodyToAplan(child, structure, init_var_name, current_value)

    def prepareGenerateExpression(self, expression: str):
        expression = replace_cpp_operators(expression)
        expression = parallelAssignment2Assignment(expression)
        expression = replaceValueParametrsCalls(self.module.value_parametrs, expression)

        return expression
