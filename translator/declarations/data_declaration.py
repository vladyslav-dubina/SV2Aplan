from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.name_change import NameChange
from classes.structure import Structure
from translator.system_verilog_to_aplan import SV2aplan
from utils.string_formating import replaceParametrsCalls
from utils.utils import (
    Counters_Object,
    CounterTypes,
    extractDimentionSize,
    extractVectorSize,
    vectorSize2AplanVectorSize,
)


def dataDecaration2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Data_declarationContext,
    listener: bool,
    sv_structure: Structure | None = None,
    name_space: ElementsTypes = ElementsTypes.NONE_ELEMENT,
):
    """The function `dataDecaration2AplanImpl` processes SystemVerilog data declarations and converts them
    to Aplan format, handling variable assignments and expressions.

    Parameters
    ----------
    self : SV2aplan
        The `self` parameter in the `dataDecaration2AplanImpl` method refers to the instance of the
    `SV2aplan` class to which the method belongs. It is a common convention in Python to use `self` as
    the first parameter in instance methods to refer to the
    ctx : SystemVerilogParser.Data_declarationContext
        The `ctx` parameter in the `dataDecaration2AplanImpl` function is of type
    `SystemVerilogParser.Data_declarationContext`. It represents the context of a data declaration in
    SystemVerilog code. This context provides information about the data type, variable names,
    dimensions, and expressions
    listener : bool
        The `listener` parameter in the `dataDecaration2AplanImpl` function is a boolean flag that
    indicates whether a listener is being used or not. It is used to control certain behavior within the
    function based on whether a listener is active or not.
    sv_structure : Structure | None
        The `sv_structure` parameter is an optional parameter of type `Structure`. It is used to pass
    information about the structure of the SystemVerilog code being translated to Aplan. This parameter
    allows the translation process to keep track of the structure of the code, such as behaviors and
    actions within the code
    name_space : ElementsTypes
        The `name_space` parameter in the `dataDecaration2AplanImpl` function is used to specify the
    namespace or scope of the elements being processed. It is of type `ElementsTypes` which is an enum
    representing different types of elements. By providing a `name_space` value,

    Returns
    -------
        The function `dataDecaration2AplanImpl` is returning the identifier of the last variable
    declaration processed in the given context `ctx`.

    """
    data_type = ctx.data_type_or_implicit()
    if data_type is not None:
        data_type = data_type.getText()
        if len(data_type) > 0:
            data_check_type = DeclTypes.checkType(data_type)
            aplan_vector_size = [0]
            size_expression = data_type
            data_type = replaceParametrsCalls(self.module.parametrs, data_type)
            vector_size = extractVectorSize(data_type)
            if vector_size is not None:
                aplan_vector_size = vectorSize2AplanVectorSize(
                    vector_size[0], vector_size[1]
                )

            for (
                elem
            ) in ctx.list_of_variable_decl_assignments().variable_decl_assignment():
                original_identifier = elem.variable_identifier().identifier().getText()
                identifier = original_identifier
                if name_space != ElementsTypes.NONE_ELEMENT:
                    identifier += f"_{Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER)}"
                    Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
                unpacked_dimention = elem.variable_dimension(0)
                dimension_size = 0
                dimension_size_expression = ""
                if unpacked_dimention is not None:
                    dimension = unpacked_dimention.getText()
                    dimension_size_expression = dimension
                    dimension = replaceParametrsCalls(self.module.parametrs, dimension)
                    dimension_size = extractDimentionSize(dimension)

                assign_name = ""
                new_decl = Declaration(
                    data_check_type,
                    identifier,
                    assign_name,
                    size_expression,
                    aplan_vector_size[0],
                    dimension_size_expression,
                    dimension_size,
                    elem.getSourceInterval(),
                )
                decl_unique, decl_index = self.module.declarations.addElement(new_decl)
                if listener == False and (
                    name_space != ElementsTypes.NONE_ELEMENT
                    or name_space != ElementsTypes.LOOP_ELEMENT
                    or name_space != ElementsTypes.GENERATE_ELEMENT
                ):
                    self.module.declarations.elements[decl_index] = new_decl

                if listener == False:
                    self.module.name_change.addElement(
                        NameChange(
                            identifier, ctx.getSourceInterval(), original_identifier
                        )
                    )

                if elem.expression() is not None:
                    expression = elem.expression().getText()
                    if listener == False:
                        if sv_structure is not None:
                            beh_index = sv_structure.getLastBehaviorIndex()
                            (
                                assign_name,
                                source_interval,
                                uniq_action,
                            ) = self.expression2Aplan(
                                elem.getText(),
                                ElementsTypes.ASSIGN_ELEMENT,
                                elem.getSourceInterval(),
                                sv_structure=sv_structure,
                            )
                            if beh_index is not None and assign_name is not None:
                                sv_structure.behavior[beh_index].addBody(
                                    (assign_name, ElementsTypes.ACTION_ELEMENT)
                                )
                    else:
                        if decl_unique:
                            (
                                assign_name,
                                source_interval,
                                uniq_action,
                            ) = self.expression2Aplan(
                                elem.getText(),
                                ElementsTypes.ASSIGN_ELEMENT,
                                elem.getSourceInterval(),
                                sv_structure=sv_structure,
                            )
                            declaration = self.module.declarations.getElementByIndex(
                                decl_index
                            )
                            declaration.expression = assign_name

            return identifier
    type_declaration = ctx.type_declaration()
    if type_declaration is not None:
        data_type = type_declaration.data_type()
        if data_type.ENUM():
            base_type = data_type.enum_base_type()
            base_type = base_type.getText()
            data_check_type = DeclTypes.checkType(base_type)
            aplan_vector_size = [0]
            size_expression = base_type
            base_type = replaceParametrsCalls(self.module.parametrs, base_type)
            vector_size = extractVectorSize(base_type)
            if vector_size is not None:
                aplan_vector_size = vectorSize2AplanVectorSize(
                    vector_size[0], vector_size[1]
                )

            for index, enum_name_decl in enumerate(data_type.enum_name_declaration()):
                identifier = enum_name_decl.enum_identifier().getText()
                assign_txt = "{0}={1}".format(identifier, index)
                (
                    assign_name,
                    source_interval,
                    uniq_action,
                ) = self.expression2Aplan(
                    assign_txt,
                    ElementsTypes.ASSIGN_ELEMENT,
                    enum_name_decl.getSourceInterval(),
                    sv_structure=sv_structure,
                )

                new_decl = Declaration(
                    data_check_type,
                    identifier,
                    assign_name,
                    size_expression,
                    aplan_vector_size[0],
                    "",
                    0,
                    enum_name_decl.getSourceInterval(),
                )

                decl_unique, decl_index = self.module.declarations.addElement(new_decl)
