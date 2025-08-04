from os import name
from antlr4_verilog.systemverilog import SystemVerilogParser
from antlr4.tree import Tree
from typing import List, Literal, Tuple, overload

from AppModule.app.classes.case_stmt import CaseStmt
from AppModule.app.classes.typedef import Typedef
from AppModule.app.utils.counters import CounterTypes, Counters
from AppModule.app.classes.declarations import DeclType, DeclTypeArray
from AppModule.app.classes.if_stmt import IfStmt
from AppModule.app.classes.loop_stmt import ForeverStmt, LoopStmt, WhileStmt
from AppModule.app.classes.design_unit_call import DesignUnitCall
from AppModule.app.classes.node import NodeArray
from AppModule.app.classes.parametrs import ParametrArray
from AppModule.app.classes.protocols import BodyElement
from AppModule.app.classes.structure import Structure, StructureArray
from AppModule.app.classes.design_unit import DesignUnit
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.tasks import TaskStmt

from translator.classes.arrays.array import ArrayTranslator
from translator.classes.arrays.methods.push_back import PushBackTranslator
from translator.classes.arrays.parametr import ParametrArrayTranslator
from translator.classes.assignments.assignment import AssignmentTranslator
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
from translator.classes.declarations.struct import (
    StructDeclTranslator,
    StructUnionMemberContextTranlator,
)
from translator.classes.declarations.task import TaskBodyDeclTranslator
from translator.classes.declarations.typedef import (
    EnumNameDeclTranslator,
    TypedefDeclTranslator,
)
from translator.classes.arrays.dynamic import DynamicArrayNewTranslator
from translator.classes.assignments.variable import VariableDeclTranslator
from translator.classes.expressions.variable_l_value import VariableLValueTranslator
from translator.classes.expressions.bit_selection import BitSelectionTranslator
from translator.classes.expressions.expression import ExpressionTranslator
from translator.classes.assignments.parameters import (
    ParametrsAssignmentTranslator,
)
from translator.classes.expressions.identifier import IdentifierTranslator
from translator.classes.expressions.number import NumberTranslator
from translator.classes.expressions.operator import OperatorTranslator
from translator.classes.expressions.range import ConstantRangeSelectionTranslator
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


TRANSLATOR_NAMES = Literal[
    "interface_decl",
    "interface_call",
    "module_decl",
    "module_call",
    "package_decl",
    "genvar_decl",
    "struct_decl",
    "struct_union_member",
    "data_decl",
    "net_decl",
    "obj_decl",
    "ansi_port_decl",
    "package_import_decl",
    "expr",
    "net_assign",
    "assignment",
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
    "constant_range_select",
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
    "var_decl",
    "var_l_val",
    "enum_name_decl",
]


class Translator:
    counters = Counters()
    design_unit_call: DesignUnitCall | None = None
    _design_unit: DesignUnit | None = None
    _structure_pointer_list: StructureArray = StructureArray()
    _cache = {}
    decl_type_array: DeclTypeArray | None = DeclTypeArray()
    last_node_array: NodeArray | None = None
    _current_genvar_value: Tuple[str, int] | None = None
    last_element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT
    last_operator: str | None = None
    last_dot_operator: str | None = None
    last_typedef: Typedef | None = None

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
        "struct_union_member": StructUnionMemberContextTranlator,
        "data_decl": DataDeclTranslator,
        "net_decl": NewDeclTranslator,
        "obj_decl": ObjectDeclTranslator,
        "ansi_port_decl": AnsiPortDeclTranslator,
        "package_import_decl": PackageImportDeclTranslator,
        "expr": ExpressionTranslator,
        "net_assign": NetAssignmentTranslator,
        "assignment": AssignmentTranslator,
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
        "constant_range_select": ConstantRangeSelectionTranslator,
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
        "var_decl": VariableDeclTranslator,
        "var_l_val": VariableLValueTranslator,
        "enum_name_decl": EnumNameDeclTranslator,
    }

    def __init__(self):
        pass

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

    def exit(self, trnslt_name: TRANSLATOR_NAMES, *args, **kwargs):
        translator = self.getTranslator(trnslt_name)
        return translator.exit(*args, **kwargs)

    def isInsideTheTask(self):
        structure: Structure | None = self._structure_pointer_list.getLastElement()
        if isinstance(structure, TaskStmt):
            return True

        return False

    def getProtocolParams(self):
        protocol_params = None
        if self.isInsideTheTask() == True:
            task = self._design_unit.tasks.getLastTask()
            if task is not None:
                protocol_params = task.parametrs
        return protocol_params

    def getLastNameSpaceLevel(self):
        struct: Structure | None = self._structure_pointer_list.getLastElement()
        if struct:
            return struct.number
        else:
            if self._design_unit:
                number = self._design_unit.number
            else:
                number = self.counters.get(self.counters.types.STRUCT_COUNTER)
            return number

    def removeLastStructPointer(self):
        if len(self._structure_pointer_list) > 0:
            self._structure_pointer_list.removeElementByIndex(
                len(self._structure_pointer_list) - 1
            )
            # Counters_Object.decriese(CounterTypes.STRUCT_COUNTER)

    def createStatement(
        self,
        name,
        element_type: ElementsTypes,
        sensetive: str | None = None,
    ):
        sv_structure: Structure | None = self._structure_pointer_list.getLastElement()
        out_of_block: bool = True
        protocol_params = self.getProtocolParams()
        tmp: ParametrArray = ParametrArray()
        inside_the_task = False
        if sv_structure:
            out_of_block = False
            if isinstance(sv_structure, TaskStmt):
                inside_the_task = True

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
            )

        elif element_type == ElementsTypes.IF_STATEMENT_ELEMENT:
            struct = IfStmt(
                name,
                (0, 0),
            )
        elif element_type == ElementsTypes.FOREVER_ELEMENT:
            struct = ForeverStmt(
                name,
                (0, 0),
            )

        elif element_type == ElementsTypes.WHILE_ELEMENT:
            struct = WhileStmt(
                name,
                (0, 0),
            )

        elif element_type == ElementsTypes.LOOP_ELEMENT:
            struct = LoopStmt(
                name,
                (0, 0),
            )
        else:
            struct = Structure(
                name,
                (0, 0),
                element_type,
            )

        struct.parametrs = tmp
        struct.inside_the_task = inside_the_task
        struct.addInitProtocol()
        if out_of_block:
            beh_index = struct.getLastBehaviorIndex()
            self._design_unit.out_of_block_elements.addElement(struct.behavior[0])
            self._structure_pointer_list.addElement(struct)
        elif sv_structure:
            beh_index = sv_structure.getLastBehaviorIndex()
            if beh_index is not None:
                if element_type == ElementsTypes.FOREVER_ELEMENT:
                    sv_structure.behavior[beh_index].addBodyElement(
                        BodyElement(
                            identifier="Sensetive({0}, {2})".format(
                                struct.getName(False),
                                sensetive,
                            ),
                            element_type=ElementsTypes.PROTOCOL_ELEMENT,
                            parametrs=protocol_params,
                        )
                    )
                else:
                    sv_structure.behavior[beh_index].addBodyElement(
                        BodyElement(
                            identifier="{0}".format(
                                struct.getName(False),
                            ),
                            element_type=ElementsTypes.PROTOCOL_ELEMENT,
                            parametrs=protocol_params,
                        )
                    )

            sv_structure.behavior.append(struct)
            self._structure_pointer_list.addElement(struct)

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
                packages = self._design_unit.packages_and_objects.getElementsIE(
                    include=ElementsTypes.PACKAGE_ELEMENT
                )
                res += self._design_unit.findAndChangeNamesToAgentAttrCall(
                    child.getText(), packages.getElements()
                )
            else:
                res += self.extractSensetive(child)
        return res
