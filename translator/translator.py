from os import name
from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from classes.case_stmt import CaseStmt
from classes.counters import CounterTypes
from classes.if_stmt import IfStmt
from classes.loop_stmt import ForeverStmt, LoopStmt, WhileStmt
from classes.module_call import ModuleCall
from classes.node import NodeArray
from classes.parametrs import ParametrArray
from classes.protocols import BodyElement
from classes.structure import Structure, StructureArray
from classes.module import Module
from classes.element_types import ElementsTypes
from typing import Literal, Tuple, overload
from classes.tasks import TaskStmt
from translator.classes.arrays.array import ArrayTranslator
from translator.classes.arrays.methods.push_back import PushBackTranslator
from translator.classes.arrays.parametr import ParametrArrayTranslator
from translator.classes.assignments.in_block import InBlockAssignmentTranslator
from translator.classes.assignments.net import NetAssignmentTranslator
from translator.classes.calls.build_in.mathematic.ceil import CeilTranslator
from translator.classes.calls.build_in.mathematic.floor import FloorTranslator
from translator.classes.calls.build_in.mathematic.modf import ModfTranslator
from translator.classes.calls.build_in.mathematic.pow import PowTranslator
from translator.classes.calls.build_in.mathematic.sqrt import SqrtTranslator
from translator.classes.calls.build_in.size import SizeTranslator
from translator.classes.calls.build_in.system import SystemTaskCallTranslator
from translator.classes.calls.interface import InterfaceCallTranslator
from translator.classes.calls.method import MethodCallTranslator
from translator.classes.calls.module import ModuleCallTranslator
from translator.classes.calls.params import ParametrsCallTranslator
from translator.classes.calls.task import TaskCallTranslator
from translator.classes.declarations.ansi_port import AnsiPortDeclTranslator
from translator.classes.declarations.class_decl import ClassDeclTranslator

from translator.classes.declarations.data import DataDeclTranslator
from translator.classes.declarations.declaration import DeclarationTranslator
from translator.classes.declarations.genvar import GenvarDeclTranslator
from translator.classes.declarations.interface import (
    InterfaceDeclTranslator,
)
from translator.classes.declarations.module import (
    ModuleDeclTranslator,
)
from translator.classes.declarations.net import NewDeclTranslator
from translator.classes.declarations.object import ObjectDeclTranslator
from translator.classes.declarations.package import PackageDeclTranslator
from translator.classes.declarations.package_import import PackageImportDeclTranslator
from translator.classes.declarations.struct import StructDeclTranslator
from translator.classes.declarations.task import TaskBodyDeclTranslator
from translator.classes.declarations.typedef import TypedefDeclTranslator
from translator.classes.arrays.dynamic import DynamicArrayNewTranslator
from translator.classes.expressions.bit_selection import BitSelectionTranslator
from translator.classes.expressions.expression import ExpressionTranslator
from translator.classes.assignments.parameters import (
    ParametrsAssignmentTranslator,
)
from translator.classes.expressions.identifier import IdentifierTranslator
from translator.classes.expressions.number import NumberTranslator
from translator.classes.expressions.operator import OperatorTranslator
from translator.classes.expressions.range import RangeSelectionTranslator
from translator.classes.expressions.unpacked_dimention import (
    UnpackedDimentionTranslator,
)
from translator.classes.jump.return_to_assign import ReturnTranslator
from translator.classes.expressions.protocol import ProtocolTranslator
from translator.classes.structures.always import AlwaysStructureTranslator
from translator.classes.structures.assert_stmt import (
    AssertInBlockTranslator,
    AssertPropertyTranslator,
)
from translator.classes.structures.case_stmt import (
    CaseItemExprTranslator,
    CaseItemTranslator,
    CaseStmtTranslator,
)
from translator.classes.structures.class_new import ClassNewTranslator
from translator.classes.structures.generate import GenerateStructTranslator
from translator.classes.structures.if_stmt import (
    IfCondPredicateTranslator,
    IfSequenceBlockTranslator,
    IfStmtTranslator,
)
from translator.classes.structures.initial import InitialStructTranslator
from translator.classes.structures.loops.forever import (
    ForeverIterationTranslator,
    ForeverStructTranslator,
)
from translator.classes.structures.loops.loop import (
    LoopIterationTranslator,
    LoopStructTranslator,
)
from translator.classes.structures.loops.repeat import RepeatStructTranslator
from translator.classes.structures.loops.while_stmt import WhileStructTranslator
from utils.utils import Counters_Object


TRANSLATOR_NAMES = Literal[
    "interface_decl",
    "interface_call",
    "module_decl",
    "module_call",
    "package_decl",
    "genvar_decl",
    "struct_decl",
    "data_decl",
    "net_decl",
    "obj_decl",
    "ansi_port_decl",
    "package_import_decl",
    "expr",
    "net_assign",
    "in_block_assign",
    "params_assign",
    "generate_struct",
    "alaways_struct",
    "if_seq_block",
    "if_stmt",
    "if_cond_predicate",
    "case_stmt",
    "case_item",
    "case_item_expr",
    "assert_property",
    "assert_block",
    "initial",
    "repeat",
    "forever",
    "forever_iteration",
    "loop",
    "loop_iteration",
    "while",
    "typedef",
    "task_body_decl",
    "task_call",
    "system_task_call",
    "method_call",
    "class_new",
    "dynamic_array_new",
    "operator",
    "return",
    "param_call",
    "range_select",
    "number",
    "unpkt_dmntn",
    "bit_select",
    "identifyer",
    "protocol",
    "ceil",
    "floor",
    "modf",
    "size",
    "pow",
    "sqrt",
    "declaration",
    "parametr_array",
    "class_decl",
    "array",
    "push_back",
]


class Translator:
    module_call: ModuleCall | None = None
    _module: Module | None = None
    _structure_pointer_list: StructureArray = StructureArray()
    _cache = {}

    _current_genvar_value: Tuple[str, int] | None = None

    @property
    def current_genvar_value(self) -> bool:
        return self._current_genvar_value

    @current_genvar_value.setter
    def current_genvar_value(self, value: Tuple[str, int] | None):
        self._current_genvar_value = value

    _translators: dict[str, type] = {
        "interface_decl": InterfaceDeclTranslator,
        "interface_call": InterfaceCallTranslator,
        "module_decl": ModuleDeclTranslator,
        "module_call": ModuleCallTranslator,
        "package_decl": PackageDeclTranslator,
        "genvar_decl": GenvarDeclTranslator,
        "struct_decl": StructDeclTranslator,
        "data_decl": DataDeclTranslator,
        "net_decl": NewDeclTranslator,
        "obj_decl": ObjectDeclTranslator,
        "ansi_port_decl": AnsiPortDeclTranslator,
        "package_import_decl": PackageImportDeclTranslator,
        "expr": ExpressionTranslator,
        "net_assign": NetAssignmentTranslator,
        "in_block_assign": InBlockAssignmentTranslator,
        "params_assign": ParametrsAssignmentTranslator,
        "generate_struct": GenerateStructTranslator,
        "alaways_struct": AlwaysStructureTranslator,
        "if_seq_block": IfSequenceBlockTranslator,
        "if_stmt": IfStmtTranslator,
        "if_cond_predicate": IfCondPredicateTranslator,
        "case_stmt": CaseStmtTranslator,
        "case_item": CaseItemTranslator,
        "case_item_expr": CaseItemExprTranslator,
        "assert_property": AssertPropertyTranslator,
        "assert_block": AssertInBlockTranslator,
        "initial": InitialStructTranslator,
        "repeat": RepeatStructTranslator,
        "forever": ForeverStructTranslator,
        "forever_iteration": ForeverIterationTranslator,
        "loop": LoopStructTranslator,
        "loop_iteration": LoopIterationTranslator,
        "while": WhileStructTranslator,
        "typedef": TypedefDeclTranslator,
        "task_body_decl": TaskBodyDeclTranslator,
        "task_call": TaskCallTranslator,
        "system_task_call": SystemTaskCallTranslator,
        "method_call": MethodCallTranslator,
        "class_new": ClassNewTranslator,
        "dynamic_array_new": DynamicArrayNewTranslator,
        "operator": OperatorTranslator,
        "return": ReturnTranslator,
        "param_call": ParametrsCallTranslator,
        "range_select": RangeSelectionTranslator,
        "number": NumberTranslator,
        "unpkt_dmntn": UnpackedDimentionTranslator,
        "bit_select": BitSelectionTranslator,
        "identifyer": IdentifierTranslator,
        "protocol": ProtocolTranslator,
        "ceil": CeilTranslator,
        "floor": FloorTranslator,
        "modf": ModfTranslator,
        "size": SizeTranslator,
        "pow": PowTranslator,
        "sqrt": SqrtTranslator,
        "declaration": DeclarationTranslator,
        "parametr_array": ParametrArrayTranslator,
        "class_decl": ClassDeclTranslator,
        "array": ArrayTranslator,
        "push_back": PushBackTranslator,
    }

    def __init__(self):
        pass

    @overload
    def getTranslator(self, key: Literal["push_back"]) -> PushBackTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["system_task_call"]
    ) -> SystemTaskCallTranslator: ...
    @overload
    def getTranslator(self, key: Literal["sqrt"]) -> SqrtTranslator: ...
    @overload
    def getTranslator(self, key: Literal["pow"]) -> PowTranslator: ...
    @overload
    def getTranslator(self, key: Literal["size"]) -> SizeTranslator: ...
    @overload
    def getTranslator(self, key: Literal["modf"]) -> ModfTranslator: ...
    @overload
    def getTranslator(self, key: Literal["array"]) -> ArrayTranslator: ...
    @overload
    def getTranslator(self, key: Literal["class_decl"]) -> ClassDeclTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["parametr_array"]
    ) -> ParametrArrayTranslator: ...
    @overload
    def getTranslator(self, key: Literal["declaration"]) -> DeclarationTranslator: ...
    @overload
    def getTranslator(self, key: Literal["floor"]) -> FloorTranslator: ...
    @overload
    def getTranslator(self, key: Literal["ceil"]) -> CeilTranslator: ...
    @overload
    def getTranslator(self, key: Literal["protocol"]) -> ProtocolTranslator: ...
    @overload
    def getTranslator(self, key: Literal["identifyer"]) -> IdentifierTranslator: ...
    @overload
    def getTranslator(self, key: Literal["bit_select"]) -> BitSelectionTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["unpkt_dmntn"]
    ) -> UnpackedDimentionTranslator: ...
    @overload
    def getTranslator(self, key: Literal["number"]) -> NumberTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["range_select"]
    ) -> RangeSelectionTranslator: ...
    @overload
    def getTranslator(self, key: Literal["param_call"]) -> ParametrsCallTranslator: ...
    @overload
    def getTranslator(self, key: Literal["return"]) -> ReturnTranslator: ...
    @overload
    def getTranslator(self, key: Literal["operator"]) -> OperatorTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["dynamic_array_new"]
    ) -> DynamicArrayNewTranslator: ...
    @overload
    def getTranslator(self, key: Literal["class_new"]) -> ClassNewTranslator: ...
    @overload
    def getTranslator(self, key: Literal["method_call"]) -> MethodCallTranslator: ...
    @overload
    def getTranslator(self, key: Literal["task_call"]) -> TaskCallTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["task_body_decl"]
    ) -> TaskBodyDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["typedef"]) -> TypedefDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["while"]) -> WhileStructTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["loop_iteration"]
    ) -> LoopIterationTranslator: ...
    @overload
    def getTranslator(self, key: Literal["loop"]) -> LoopStructTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["forever_iteration"]
    ) -> ForeverIterationTranslator: ...
    @overload
    def getTranslator(self, key: Literal["forever"]) -> ForeverStructTranslator: ...
    @overload
    def getTranslator(self, key: Literal["repeat"]) -> RepeatStructTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["interface_decl"]
    ) -> InterfaceDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["module_decl"]) -> ModuleDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["package_decl"]) -> PackageDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["genvar_decl"]) -> GenvarDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["struct_decl"]) -> StructDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["data_decl"]) -> DataDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["net_decl"]) -> NewDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["obj_decl"]) -> ObjectDeclTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["ansi_port_decl"]
    ) -> AnsiPortDeclTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["package_import_decl"]
    ) -> PackageImportDeclTranslator: ...
    @overload
    def getTranslator(self, key: Literal["expr"]) -> ExpressionTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["interface_call"]
    ) -> InterfaceCallTranslator: ...
    @overload
    def getTranslator(self, key: Literal["net_assign"]) -> NetAssignmentTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["in_block_assign"]
    ) -> InBlockAssignmentTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["params_assign"]
    ) -> ParametrsAssignmentTranslator: ...
    @overload
    def getTranslator(self, key: Literal["module_call"]) -> ModuleCallTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["generate_struct"]
    ) -> GenerateStructTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["alaways_struct"]
    ) -> AlwaysStructureTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["if_seq_block"]
    ) -> IfSequenceBlockTranslator: ...
    @overload
    def getTranslator(self, key: Literal["if_stmt"]) -> IfStmtTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["if_cond_predicate"]
    ) -> IfCondPredicateTranslator: ...
    @overload
    def getTranslator(self, key: Literal["case_stmt"]) -> CaseStmtTranslator: ...
    @overload
    def getTranslator(self, key: Literal["case_item"]) -> CaseItemTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["case_item_expr"]
    ) -> CaseItemExprTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["assert_property"]
    ) -> AssertPropertyTranslator: ...
    @overload
    def getTranslator(
        self, key: Literal["assert_block"]
    ) -> AssertInBlockTranslator: ...
    @overload
    def getTranslator(self, key: Literal["initial"]) -> InitialStructTranslator: ...

    def getTranslator(self, key: TRANSLATOR_NAMES):
        cls = self._selectTranlator(key)
        if key not in self._cache:
            self._cache[key] = cls(self)
        return self._cache[key]

    def _selectTranlator(self, name: TRANSLATOR_NAMES):
        if name not in self._translators:
            raise ValueError(f"Unknown translator name: {name}")
        return self._translators[name]

    def translate(self, trnslt_name: TRANSLATOR_NAMES, *args, **kwargs):
        translator = self.getTranslator(trnslt_name)
        return translator.translate(*args, **kwargs)

    def getProtocolParams(self):
        protocol_params = None
        if self._inside_the_task == True:
            task = self._module.tasks.getLastTask()
            if task is not None:
                protocol_params = task.parametrs
        return protocol_params

    def getLastNameSpaceLevel(self):

        struct: Structure | None = self._structure_pointer_list.getLastElement()
        if struct:
            return struct.number
        else:
            return self._module.number

    def removeLastStructPointer(self):
        if self._structure_pointer_list.getLen() > 0:
            self._structure_pointer_list.removeElementByIndex(
                self._structure_pointer_list.getLen() - 1
            )
            # Counters_Object.decrieseCounter(CounterTypes.STRUCT_COUNTER)

    def body2Aplan(
        self,
        ctx,
        sv_structure: Structure | None = None,
        destination_node_array: NodeArray | None = None,
    ):
        names_for_change = []
        if ctx is None:
            return names_for_change
        if ctx.getChildCount() == 0:
            return names_for_change
        for child in ctx.getChildren():
            # print(type(child), child.getText())
            # Assert handler
            # if (
            #    type(child)
            #    is SystemVerilogParser.Simple_immediate_assert_statementContext
            # ):
            #    self.assertInBlock2Aplan(child, sv_structure)
            # ---------------------------------------------------------------------------
            if type(child) is SystemVerilogParser.System_tf_callContext:
                self.translate(
                    "system_task_call", child, destination_node_array, sv_structure
                )
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.IdentifierContext:
                self.translate("identifyer", child, destination_node_array)
            # ---------------------------------------------------------------------------
            elif (
                type(child) is SystemVerilogParser.Bit_selectContext
                or type(child) is SystemVerilogParser.Constant_bit_selectContext
            ):
                self.translate("bit_select", child, destination_node_array)
            elif type(child) is SystemVerilogParser.Unpacked_dimensionContext:
                self.translate("unpkt_dmntn", child, destination_node_array)
            elif type(child) is SystemVerilogParser.Part_select_rangeContext:
                self.translate("range_select", child, destination_node_array)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.NumberContext:
                self.translate("number", child, destination_node_array)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.Jump_statementContext:
                if child.RETURN and child.expression():
                    self.translate("return", child.expression(), sv_structure)
            # ---------------------------------------------------------------------------
            # Task and function handler
            elif type(child) is SystemVerilogParser.Tf_callContext:
                self.translate("task_call", child, sv_structure, destination_node_array)
            # ---------------------------------------------------------------------------
            # Dynamic_array new[] handler
            elif type(child) is SystemVerilogParser.Dynamic_array_newContext:
                self.translate(
                    "dynamic_array_new", child, sv_structure, destination_node_array
                )
            # ---------------------------------------------------------------------------
            # Class new() handler
            elif type(child) is SystemVerilogParser.Class_newContext:
                self.translate("class_new", child, sv_structure, destination_node_array)
            # ---------------------------------------------------------------------------
            elif type(child) is SystemVerilogParser.Method_call_bodyContext:
                self.translate(
                    "method_call", child, sv_structure, destination_node_array
                )
            # ---------------------------------------------------------------------------

            elif type(child) is Tree.TerminalNodeImpl:
                self.translate("operator", child, destination_node_array)
            # ---------------------------------------------------------------------------
            else:
                names_for_change += self.body2Aplan(
                    child, sv_structure, destination_node_array
                )

        return names_for_change

    def createStatement(
        self,
        name,
        element_type: ElementsTypes,
        sensetive: str | None = None,
    ):
        counter_type: CounterTypes = CounterTypes.STRUCT_COUNTER
        sv_structure: Structure | None = self._structure_pointer_list.getLastElement()
 
        
        if sv_structure:
            protocol_params = self.getProtocolParams()
            beh_index = sv_structure.getLastBehaviorIndex()
            if beh_index is not None:
                if element_type == ElementsTypes.FOREVER_ELEMENT:
                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(
                            identifier="Sensetive({0}_{1}, {2})".format(
                                name,
                                Counters_Object.getCounter(counter_type),
                                sensetive,
                            ),
                            element_type=ElementsTypes.PROTOCOL_ELEMENT,
                            parametrs=protocol_params,
                        )
                    )
                else:
                    sv_structure.behavior[beh_index].addBody(
                        BodyElement(
                            identifier="{0}_{1}".format(
                                name,
                                Counters_Object.getCounter(counter_type),
                            ),
                            element_type=ElementsTypes.PROTOCOL_ELEMENT,
                            parametrs=protocol_params,
                        )
                    )

            tmp: ParametrArray = ParametrArray()
            if isinstance(sv_structure, TaskStmt):
                inside_the_task = True
            else:
                inside_the_task = False
            if (inside_the_task) is False:
                if sv_structure.parametrs is not None:
                    tmp += sv_structure.parametrs
                if protocol_params is not None:
                    tmp += protocol_params
            else:
                tmp = protocol_params

            if element_type == ElementsTypes.CASE_STATEMENT_ELEMENT:
                struct = CaseStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )

            elif element_type == ElementsTypes.IF_STATEMENT_ELEMENT:
                struct = IfStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )
            elif element_type == ElementsTypes.FOREVER_ELEMENT:
                struct = ForeverStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )

            elif element_type == ElementsTypes.WHILE_ELEMENT:
                struct = WhileStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )

            elif element_type == ElementsTypes.LOOP_ELEMENT:
                struct = LoopStmt(
                    name,
                    (0, 0),
                    Counters_Object.getCounter(counter_type),
                )
            else:
                struct = Structure(
                    name,
                    (0, 0),
                    element_type,
                    Counters_Object.getCounter(counter_type),
                )

            struct.addInitProtocol()
            struct.parametrs = tmp
            struct.inside_the_task = inside_the_task
            sv_structure.behavior.append(struct)
            self._structure_pointer_list.addElement(struct)
            Counters_Object.incrieseCounter(counter_type)

    def extractSensetive(self, ctx):
        res = ""
        for child in ctx.getChildren():
            if type(child) is SystemVerilogParser.Edge_identifierContext:
                index = child.getText().find("negedge")
                if index != -1:
                    res += "!"
            elif type(child) is Tree.TerminalNodeImpl:
                index = child.getText().find("or")
                if index != -1:
                    res += " || "
                index = child.getText().find("and")
                if index != -1:
                    res += " && "
            elif type(child) is SystemVerilogParser.IdentifierContext:
                packages = self._module.packages_and_objects.getElementsIE(
                    include=ElementsTypes.PACKAGE_ELEMENT
                )
                res += self._module.findAndChangeNamesToAgentAttrCall(
                    child.getText(), packages.getElements()
                )
            else:
                res += self.extractSensetive(child)
        return res
