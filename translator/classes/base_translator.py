import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from Core.src.utils.counters import Counters
from Core.src.utils.file_manager import FilesMngr
from Core.src.logger.logger import Logger, LoggerManager
from Core.src.utils.string_formater import StringFormater
from Core.src.utils.unsorted import UnsortedUnils

from Core.src.classes.declarations import (
    DeclType,
    DeclTypeArray,
    DeclTypes,
    Declaration,
)
from Core.src.classes.element_types import ElementsTypes
from Core.src.classes.node import NodeArray
from Core.src.classes.structure import Structure, StructureArray
from Core.src.classes.tasks import TaskStmt
from Core.src.classes.typedef import Typedef

from Core.src.classes.design_unit import DesignUnit, DesignUnitArray
from Core.src.program.program import Program
from Core.src.classes.design_unit_call import DesignUnitCall

if typing.TYPE_CHECKING:
    from translator.translator import Translator


class BaseTranslator:
    counters = Counters()
    str_formater = StringFormater()
    utils = UnsortedUnils()
    file_mngr = FilesMngr()

    def __init__(self, translator: "Translator"):
        self._translator_ptr = translator
        self._program = Program()
        self.inside_the_task = False
        self.last_struct: Structure | None = None
        self.logger: Logger = LoggerManager().getLogger(self.__class__.__qualname__)

    def translate(self, ctx) -> None:
        raise TypeError("Run base translator")

    def exit(self, ctx) -> None:
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
    def design_unit_call(self) -> DesignUnitCall:
        return self._translator_ptr.design_unit_call

    @property
    def design_units(self) -> DesignUnitArray:
        return self._program.design_units

    @property
    def design_unit(self) -> DesignUnit:
        return self._translator_ptr._design_unit

    @design_unit.setter
    def design_unit(self, value: DesignUnit):
        self._translator_ptr._design_unit = value

    @property
    def last_typedef(self) -> Typedef:
        return self._translator_ptr.last_typedef

    @last_typedef.setter
    def last_typedef(self, value: Typedef):
        self._translator_ptr.last_typedef = value

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

    @property
    def last_dot_operator(self) -> str | None:
        return self._translator_ptr.last_dot_operator

    @last_dot_operator.setter
    def last_dot_operator(self, value: str | None):
        self._translator_ptr.last_dot_operator = value

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
        if self.design_unit:
            return self.design_unit.typedefs.getLastElement()
        else:
            return self._program.typedefs.getLastElement()

    def findEnumConst(self, identifier) -> str | None:
        for typedef in self.design_unit.typedefs.getElementsIE().getElements():
            decl: Declaration = typedef.declarations.getElement(identifier)
            if decl:
                return decl.expression

    def addTypedef(self, typedef: Typedef):
        if self.design_unit:
            return self.design_unit.typedefs.addElement(typedef)
        else:
            return self._program.typedefs.addElement(typedef)

    def _process_dimensions(
        self,
        unpacked_dimension_ctx: typing.Optional[
            SystemVerilogParser.Variable_dimensionContext
        ],
        packed_dimension_ctx: typing.Optional[
            SystemVerilogParser.Packed_dimensionContext
        ],
    ) -> tuple[str, int, str, int, typing.List[int]]:
        """
        Обробляє контексти вимірів та повертає підготовлені дані для Declaration.
        Повертає:
            (size_expression, aplan_vector_size, dimension_size_expression, dimension_size, vector_size_tuple)
        """
        dimension_size = 0
        dimension_size_expression = ""
        size_expression = ""
        aplan_vector_size = [0]
        vector_size_tuple = None  # (msb, lsb)

        # Обробка unpacked_dimension
        if unpacked_dimension_ctx is not None:
            dimension = unpacked_dimension_ctx.getText()
            dimension_size_expression = dimension
            # Заміна параметрів значень
            dimension = self.str_formater.replaceValueParametrsCalls(
                self.design_unit.value_parametrs, dimension
            )
            dimension_size = self.utils.extractDimentionSize(dimension)
            if (
                dimension_size is None
            ):  # Обробка випадку, коли extractDimentionSize може повернути None
                dimension_size = 0

        # Обробка packed_dimension (векторного розміру)
        if packed_dimension_ctx is not None:
            vector_size_text = packed_dimension_ctx.getText()
            size_expression = vector_size_text
            # Заміна параметрів значень
            processed_vector_size = self.str_formater.replaceValueParametrsCalls(
                self.design_unit.value_parametrs, vector_size_text
            )
            vector_size_tuple = self.utils.extractVectorSize(processed_vector_size)

            if vector_size_tuple is not None:
                aplan_vector_size = self.utils.vectorSize2AplanVectorSize(
                    vector_size_tuple[0], vector_size_tuple[1]
                )

        return (
            size_expression,
            aplan_vector_size[0],
            dimension_size_expression,
            dimension_size,
            vector_size_tuple,
        )
