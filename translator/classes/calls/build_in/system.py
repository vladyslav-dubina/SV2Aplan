from typing import List
import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.actions import Action
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.node import Node, NodeArray
from AppModule.app.classes.parametrs import Parametr, ParametrArray
from translator.classes.base_translator import BaseTranslator


class SystemTaskCallTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:

        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    # TODO Change sv_structure to get struct from list and similar for dest_node
    def translate(
        self,
        ctx: SystemVerilogParser.System_tf_callContext,
    ) -> None:
        action = self.module.actions.isUniqActionBySourceInterval(
            ctx.getSourceInterval()
        )
        action_name = ""
        precondition: NodeArray = NodeArray(ElementsTypes.PRECONDITION_ELEMENT)
        postcondition: NodeArray = NodeArray(ElementsTypes.POSTCONDITION_ELEMENT)
        description_start: List[str] = []
        description_end: List[str] = []
        description_action_name: str = ""
        parametrs: ParametrArray = ParametrArray()
        body = ""
        name_part = ""
        system_tf_identifier = ctx.system_tf_identifier().getText()
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT
        if system_tf_identifier == "$display":
            return
        elif system_tf_identifier == "$time":
            return
        elif system_tf_identifier == "$finish" or system_tf_identifier == "$stop":
            action_name = system_tf_identifier.replace("$", "")
            description_start.append(
                f"{self.module.identifier}#{self.module.ident_uniq_name}"
            )
            description_action_name = action_name
            name_part = action_name
            precondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))
            body = f"goal {action_name}"
        elif system_tf_identifier == "$ceil":
            self._translator_ptr.translate("ceil", ctx)
            return
        elif system_tf_identifier == "$floor":
            self._translator_ptr.translate("floor", ctx)
            return
        elif system_tf_identifier == "$pow":
            self._translator_ptr.translate("pow", ctx)
            return
        elif system_tf_identifier == "$sqrt":
            self._translator_ptr.translate("sqrt", ctx)
            return
        elif system_tf_identifier == "$size":

            (
                name_part,
                element_type,
                action_name,
                parametrs,
                description_start,
                description_end,
                description_action_name,
                precondition,
                postcondition,
                body,
            ) = self._translator_ptr.translate(
                "size",
                ctx,
                parametrs,
                description_start,
                description_end,
                precondition,
                postcondition,
            )

            if self.last_node_array:
                node = Node("return_size", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
                node.module_name = self.module.ident_uniq_name
                self.last_node_array.addElement(node.copy())

        elif system_tf_identifier == "&pow":
            action_name = "pow"
            parametrs.addElement(
                Parametr(
                    "x",
                    "var",
                )
            )
            parametrs.addElement(
                Parametr(
                    "y",
                    "var",
                )
            )

        action = Action(action_name, ctx.getSourceInterval(), element_type=element_type)
        action.parametrs = parametrs
        action.precondition = precondition
        action.postcondition = postcondition
        action.description_start = description_start
        action.description_end = description_end
        action.description_action_name = description_action_name

        action_pointer: Action = action
        (
            action_pointer,
            action_check_result,
            source_interval,
        ) = self.module.actions.isUniqAction(action)

        if action_check_result is None:
            action_pointer: Action = action
            self.module.actions.addElement(action)

        self._translator_ptr.translate(
            "protocol",
            action_pointer,
            body,
            action_name,
            None,
        )
