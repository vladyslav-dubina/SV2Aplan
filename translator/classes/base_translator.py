import typing

from AppModule.app.utils.counters import Counters
from AppModule.app.utils.file_manager import FilesMngr
from AppModule.app.utils.logger import Logger
from AppModule.app.utils.string_formater import StringFormater
from AppModule.app.utils.unsorted import UnsortedUnils

from AppModule.app.classes.declarations import DeclType, DeclTypeArray
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.node import NodeArray
from AppModule.app.classes.structure import Structure, StructureArray
from AppModule.app.classes.tasks import TaskStmt
from AppModule.app.classes.typedef import Typedef

from AppModule.app.classes.module import Module, ModuleArray
from AppModule.app.program.program import Program
from AppModule.app.classes.module_call import ModuleCall

if typing.TYPE_CHECKING:
    from translator.translator import Translator


class BaseTranslator:
    counters = Counters()
    str_formater = StringFormater()
    utils = UnsortedUnils()
    file_mngr = FilesMngr()
    logger = Logger()

    def __init__(self, translator: "Translator"):

        self._translator_ptr = translator
        self._program = Program()
        self.inside_the_task = False
        self.last_struct: Structure | None = None

    def translate(self, ctx) -> None:
        raise TypeError("Run base translator")

    def exit(self) -> None:
        raise TypeError("Run base exit")

    def findStruct(
        self,
    ) -> None:
        self.last_struct: Structure | None = (
            self.structure_pointer_list.getLastElement()
        )
        if self.last_struct:
            if isinstance(self.last_struct, TaskStmt):
                self.inside_the_task = True
            else:
                self.inside_the_task = self.last_struct.inside_the_task

    def createStatement(
        self,
        name,
        element_type: ElementsTypes,
        sensetive: str | None = None,
    ):
        self._translator_ptr.createStatement(name, element_type, sensetive)

    def extractSensetive(self, ctx):
        return self._translator_ptr.extractSensetive(ctx)

    @property
    def module_call(self) -> ModuleCall:
        return self._translator_ptr.module_call

    @property
    def modules(self) -> ModuleArray:
        return self._program.modules

    @property
    def module(self) -> Module:
        return self._translator_ptr._module

    @module.setter
    def module(self, value: Module):
        self._translator_ptr._module = value

    @property
    def structure_pointer_list(self) -> StructureArray:
        return self._translator_ptr._structure_pointer_list

    @property
    def decl_type_array(self) -> DeclTypeArray:
        return self._translator_ptr.decl_type_array

    @decl_type_array.setter
    def decl_type_array(self, value: DeclTypeArray | None):
        self._translator_ptr.decl_type_array = value

    @property
    def last_node_array(self) -> NodeArray:
        return self._translator_ptr.last_node_array

    @last_node_array.setter
    def last_node_array(self, value: NodeArray | None):
        self._translator_ptr.last_node_array = value

    @property
    def last_element_type(self) -> ElementsTypes:
        return self._translator_ptr.last_element_type

    @last_element_type.setter
    def last_element_type(self, value: ElementsTypes | None):
        self._translator_ptr.last_element_type = value

    @property
    def last_operator(self) -> str | None:
        return self._translator_ptr.last_operator

    @last_operator.setter
    def last_operator(self, value: str | None):
        self._translator_ptr.last_operator = value

    def getLastNameSpaceLevel(self) -> bool:
        return self._translator_ptr.getLastNameSpaceLevel()

    def getProtocolParams(self):
        self.findStruct()
        if self.last_struct:
            return self.last_struct.parametrs

    @property
    def current_genvar_value(self) -> bool:
        return self._translator_ptr._current_genvar_value

    @current_genvar_value.setter
    def current_genvar_value(self, value: typing.Tuple[str, int] | None):
        self._translator_ptr._current_genvar_value = value

    def getLastTypedef(self) -> Typedef | None:
        if self.module:
            return self.module.typedefs.getLastElement()
        else:
            return self._program.typedefs.getLastElement()

    def addTypedef(self, typedef: Typedef):
        if self.module:
            return self.module.typedefs.addElement(typedef)
        else:
            return self._program.typedefs.addElement(typedef)
