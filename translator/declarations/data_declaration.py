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
            types = self.module.declarations.getElementsForTypes()
            packages = self.module.packages_and_objects.getElementsIE(
                include=ElementsTypes.PACKAGE_ELEMENT
            )
            packages += self.module.packages_and_objects.getElementsIE(
                include=ElementsTypes.OBJECT_ELEMENT
            )
            for package in packages.getElements():
                types += package.declarations.getElementsForTypes()
            data_check_type = DeclTypes.checkType(data_type, types)
            aplan_vector_size = [0]
            size_expression = data_type
            data_type = replaceParametrsCalls(self.module.parametrs, data_type)
            vector_size = extractVectorSize(data_type)
            if vector_size is not None:
                aplan_vector_size = vectorSize2AplanVectorSize(
                    vector_size[0], vector_size[1]
                )
            if isinstance(ctx, SystemVerilogParser.Data_declarationContext):
                declaration = (
                    ctx.list_of_variable_decl_assignments().variable_decl_assignment()
                )

            for elem in declaration:
                if isinstance(ctx, SystemVerilogParser.Data_declarationContext):
                    original_identifier = (
                        elem.variable_identifier().identifier().getText()
                    )

                identifier = original_identifier
                if name_space != ElementsTypes.NONE_ELEMENT:
                    identifier += f"_{Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER)}"
                    Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)

                if isinstance(ctx, SystemVerilogParser.Data_declarationContext):
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

                if isinstance(ctx, SystemVerilogParser.Data_declarationContext):
                    expression = elem.expression()

                declaration = self.module.declarations.getElementByIndex(decl_index)

                if sv_structure is not None:
                    sv_structure.elements.addElement(declaration)

                if expression is not None:
                    expression = expression.getText()
                    if listener == False:
                        if sv_structure is not None:
                            beh_index = sv_structure.getLastBehaviorIndex()
                            (
                                action_pointer,
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
                                    (
                                        action_pointer,
                                        assign_name,
                                        ElementsTypes.ACTION_ELEMENT,
                                    )
                                )
                    else:
                        if decl_unique:
                            (
                                action_pointer,
                                assign_name,
                                source_interval,
                                uniq_action,
                            ) = self.expression2Aplan(
                                elem.getText(),
                                ElementsTypes.ASSIGN_ELEMENT,
                                elem.getSourceInterval(),
                                sv_structure=sv_structure,
                            )
                            declaration.expression = assign_name
                            declaration.action = action_pointer

            return identifier
    type_declaration = ctx.type_declaration()
    if type_declaration is not None:
        data_type = type_declaration.data_type()
        if data_type.ENUM():
            for type_identifier in type_declaration.type_identifier():
                enum_type_identifier = "{0}".format(type_identifier.getText())
                elements = ""
                for index, enum_name_decl in enumerate(
                    data_type.enum_name_declaration()
                ):
                    if index != 0:
                        elements += ","
                    identifier = enum_name_decl.enum_identifier().getText()
                    elements += identifier

                new_decl = Declaration(
                    DeclTypes.ENUM_TYPE,
                    enum_type_identifier,
                    elements,
                    "",
                    0,
                    "",
                    0,
                    enum_name_decl.getSourceInterval(),
                )

                decl_unique, decl_index = self.module.declarations.addElement(new_decl)
