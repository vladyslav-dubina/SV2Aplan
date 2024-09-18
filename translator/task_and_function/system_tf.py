from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.node import Node, NodeArray
from classes.parametrs import Parametr, ParametrArray
from classes.protocols import BodyElement
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


embeaded_tf_list = ["$display", "$time"]


def systemTF2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.System_tf_callContext,
    destination_node_array: NodeArray | None = None,
    sv_structure: Structure | None = None,
):
    action = self.module.actions.isUniqActionBySourceInterval(ctx.getSourceInterval())
    action_name = ""
    precondition: NodeArray = NodeArray(ElementsTypes.PRECONDITION_ELEMENT)
    postcondition: NodeArray = NodeArray(ElementsTypes.POSTCONDITION_ELEMENT)
    description: str = ""
    parametrs: ParametrArray = ParametrArray()
    body = ""
    system_tf_identifier = ctx.system_tf_identifier().getText()
    if system_tf_identifier == "$display":
        return
    elif system_tf_identifier == "$time":
        return
    elif system_tf_identifier == "$finish" or system_tf_identifier == "$stop":
        action_name = system_tf_identifier.replace("$", "")
        description = f"{self.module.identifier}#{self.module.ident_uniq_name}:action '{action_name}'"
        precondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))
        body = f"goal {action_name}"
    elif system_tf_identifier == "$size":

        self.module.declarations.addElement(
            Declaration(
                DeclTypes.INT,
                "return_size",
                "",
                "",
                0,
                "",
                0,
                ctx.getSourceInterval(),
            )
        )

        parametrs.addElement(
            Parametr(
                "result",
                "var",
            )
        )

        array = ctx.list_of_arguments().getText()
        decl = self.module.declarations.findElement(array)
        if decl is None:
            return

        node = Node(
            array,
            ctx.list_of_arguments().getSourceInterval(),
            ElementsTypes.ARRAY_SIZE_ELEMENT,
        )

        action_name = f"size_{array}"
        node.module_name = self.module.ident_uniq_name
        description = f"{self.module.identifier}#{self.module.ident_uniq_name}:action 'result = {array}.size'"
        precondition.addElement(Node(1, (0, 0), ElementsTypes.NUMBER_ELEMENT))
        postcondition.addElement(Node("result", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT))
        postcondition.addElement(Node("=", (0, 0), ElementsTypes.OPERATOR_ELEMENT))
        postcondition.addElement(node)
        body = f"{action_name}(return_size)"

        if destination_node_array:
            destination_node_array.addElement(
                Node("return_size", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
            )

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

    action = Action(
        action_name,
        ctx.getSourceInterval(),
    )
    action.parametrs = parametrs
    action.precondition = precondition
    action.postcondition = postcondition
    action.description = description
    (
        action_pointer,
        action_check_result,
        source_interval,
    ) = self.module.actions.isUniqAction(action)
    if action_check_result is None:
        self.module.actions.addElement(action)
    if sv_structure is not None:
        sv_structure.elements.addElement(action)
        beh_index = sv_structure.getLastBehaviorIndex()
        if beh_index is not None:
            sv_structure.behavior[beh_index].addBody(
                BodyElement(body, action, ElementsTypes.ACTION_ELEMENT)
            )
        else:
            Counters_Object.incrieseCounter(CounterTypes.B_COUNTER)
            b_index = sv_structure.addProtocol(
                "B_{0}".format(action.getName()),
                inside_the_task=(self.inside_the_task or self.inside_the_function),
            )
            sv_structure.behavior[b_index].addBody(
                BodyElement(body, action, ElementsTypes.ACTION_ELEMENT)
            )
