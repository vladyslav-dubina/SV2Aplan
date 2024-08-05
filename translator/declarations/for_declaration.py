from typing import List, Tuple
from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.actions import Action
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.element_types import ElementsTypes
from classes.name_change import NameChange
from classes.structure import Structure
from translator.expression.expression import actionFromNodeStr
from translator.system_verilog_to_aplan import SV2aplan
from utils.utils import Counters_Object


def loopVars2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Loop_variablesContext,
    sv_structure: Structure,
):
    """This function processes loop variables in SystemVerilog code by generating unique identifiers and
    adding declarations to the module.

    Parameters
    ----------
    self : SV2aplan
        The `self` parameter refers to an instance of the `SV2aplan` class.
    ctx : SystemVerilogParser.Loop_variablesContext
        The `ctx` parameter in the `loopVars2AplanImpl` function is of type
    `SystemVerilogParser.Loop_variablesContext`. It is used to extract loop variables from a
    SystemVerilog code snippet. The function processes each `index_variable_identifier` within the
    context to generate unique identifiers

    Returns
    -------
        The function `loopVars2AplanImpl` is returning a tuple containing two lists: `idenifier_list` and
    `source_interval_list`. The `idenifier_list` contains the modified identifiers for each index
    variable, while the `source_interval_list` contains the source intervals for each index variable
    identifier in the input context `ctx`.

    """
    idenifier_list: List[str] = []
    source_interval_list: List[Tuple[int, int]] = []
    for index_variable_identifier in ctx.index_variable_identifier():
        original_identifier = index_variable_identifier.identifier().getText()
        identifier = (
            original_identifier
            + f"_{Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER)}"
        )
        Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
        data_type = "int"
        size_expression = data_type
        packages = self.module.packages_and_objects.getElementsIE(
            include=ElementsTypes.PACKAGE_ELEMENT
        )
        packages += self.module.packages_and_objects.getElementsIE(
            include=ElementsTypes.OBJECT_ELEMENT
        )
        data_type = DeclTypes.checkType(data_type, packages.getElements())
        assign_name = ""
        decl_unique, decl_index = self.module.declarations.addElement(
            Declaration(
                data_type,
                identifier,
                assign_name,
                size_expression,
                0,
                "",
                0,
                index_variable_identifier.getSourceInterval(),
            )
        )

        declaration = self.module.declarations.getElementByIndex(decl_index)
        sv_structure.elements.addElement(declaration)

        self.module.name_change.addElement(
            NameChange(
                identifier,
                index_variable_identifier.getSourceInterval(),
                original_identifier,
            )
        )
        idenifier_list.append(identifier)
        source_interval_list.append(index_variable_identifier.getSourceInterval())

    return (idenifier_list, source_interval_list)


def loopVarsDeclarations2AplanImpl(
    self: SV2aplan,
    vars_names: List[str],
    source_intervals: List[Tuple[int, int]],
    sv_structure: Structure,
):
    """The function `loopVarsDeclarations2AplanImpl` takes a list of variable names and source intervals,
    creates assignment actions for each variable, and returns a list of assign names.

    Parameters
    ----------
    self : SV2aplan
        SV2aplan - an instance of a class
    vars_names : List[str]
        The `vars_names` parameter is a list of strings containing the names of variables that need to be
    declared and initialized to 0 in the function `loopVarsDeclarations2AplanImpl`.
    source_intervals : List[Tuple[int, int]]
        The `source_intervals` parameter is a list of tuples where each tuple represents an interval. Each
    tuple contains two integers, the start and end points of the interval.

    Returns
    -------
        The function `loopVarsDeclarations2AplanImpl` is returning a list of assign names that are
    generated based on the input variables names and source intervals provided.

    """
    assign_names: List[str] = []
    action_pointers = []
    for index, identifier in enumerate(vars_names):
        action_txt = f"{identifier} = 0"
        (
            action_pointer,
            assign_name,
            source_interval,
            uniq_action,
        ) = actionFromNodeStr(
            self,
            action_txt,
            source_intervals[index],
            ElementsTypes.ASSIGN_ELEMENT,
            sv_structure,
        )
        assign_names.append(assign_name)
        action_pointers.append(action_pointer)

    return (assign_names, action_pointers)


def loopVarsToIteration2AplanImpl(
    self: SV2aplan,
    vars_names: List[str],
    source_intervals: List[Tuple[int, int]],
    sv_structure: Structure,
):
    """The function `loopVarsToIteration2AplanImpl` takes a list of variable names and source intervals,
    generates assignment actions for each variable, and returns a list of assignment names.

    Parameters
    ----------
    self : SV2aplan
        SV2aplan instance that the method belongs to
    vars_names : List[str]
        The `vars_names` parameter is a list of strings representing the names of variables that you want
    to increment by 1 in the loop.
    source_intervals : List[Tuple[int, int]]
        The `source_intervals` parameter is a list of tuples representing intervals. Each tuple contains
    two integers, indicating the start and end points of a specific interval.

    Returns
    -------
        The function `loopVarsToIteration2AplanImpl` is returning a list of assign names generated from the
    input variables and source intervals provided.

    """
    assign_names: List[str] = []
    action_pointers = []
    for index, identifier in enumerate(vars_names):
        action_txt = f"{identifier} = {identifier} + 1"
        (
            action_pointer,
            assign_name,
            source_interval,
            uniq_action,
        ) = actionFromNodeStr(
            self,
            action_txt,
            source_intervals[index],
            ElementsTypes.ASSIGN_ELEMENT,
            sv_structure,
        )
        assign_names.append(assign_name)
        action_pointers.append(action_pointer)

    return (assign_names, action_pointers)


def loopVarsAndArrayIdentifierToCondition2AplanImpl(
    self: SV2aplan,
    vars_names: List[str],
    ctx: SystemVerilogParser.Ps_or_hierarchical_array_identifierContext,
    sv_structure: Structure,
):
    """This function generates a condition based on variable names and array identifier size in
    SystemVerilog.

    Parameters
    ----------
    self : SV2aplan
        The `self` parameter refers to an instance of the `SV2aplan` class. It is used to access methods
    and attributes within the class.
    vars_names : List[str]
        The `vars_names` parameter is a list of strings that represent the names of variables. In the
    provided code snippet, this list is used in a loop to generate a condition based on the size of a
    hierarchical array identifier. Each element in the `vars_names` list is compared to the size of
    ctx : SystemVerilogParser.Ps_or_hierarchical_array_identifierContext
        The `ctx` parameter in your function `loopVarsAndArrayIdentifierToCondition2AplanImpl` seems to be
    of type `SystemVerilogParser.Ps_or_hierarchical_array_identifierContext`. This parameter likely
    represents the context or information related to a hierarchical array identifier in a SystemVerilog
    parser

    Returns
    -------
        The function `loopVarsAndArrayIdentifierToCondition2AplanImpl` returns the name of the condition
    generated based on the input variables and array identifier.

    """
    array_identifier = ctx.hierarchical_array_identifier().getText()
    condition = ""
    decl = self.module.declarations.findElement(array_identifier)

    for index, element in enumerate(vars_names):
        if index != 0:
            condition += " && "
        condition = "{0} < {1}".format(element, decl.size)
    (
        action_pointer,
        condition_name,
        source_interval,
        uniq_action,
    ) = actionFromNodeStr(
        self,
        condition,
        ctx.getSourceInterval(),
        ElementsTypes.CONDITION_ELEMENT,
        sv_structure,
    )
    return (action_pointer, condition_name)


def forInitialization2ApanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.For_initializationContext,
    sv_structure: Structure,
):
    """This function initializes a variable in SystemVerilog code with a unique identifier and data type.

    Parameters
    ----------
    self : SV2aplan
        The `self` parameter in the `forInitialization2ApanImpl` function refers to an instance of the
    `SV2aplan` class. It is used to access attributes and methods within the class.
    ctx : SystemVerilogParser.For_initializationContext
        The `ctx` parameter in the `forInitialization2ApanImpl` function is of type
    `SystemVerilogParser.For_initializationContext`. This parameter is used to access information
    related to the for loop initialization context in a SystemVerilog parser. It allows you to extract
    details such as variable declarations

    Returns
    -------
        The function `forInitialization2ApanImpl` is returning the `identifier` variable, which is a unique
    identifier generated based on the original identifier and a counter value.

    """
    assign_name = ""
    expression = ctx.for_variable_declaration(0)
    if expression is not None:
        original_identifier = expression.variable_identifier(0).getText()
        identifier = (
            original_identifier
            + f"_{Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER)}"
        )
        Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
        data_type = expression.data_type().getText()
        size_expression = data_type
        packages = self.module.packages_and_objects.getElementsIE(
            include=ElementsTypes.PACKAGE_ELEMENT
        )
        packages += self.module.packages_and_objects.getElementsIE(
            include=ElementsTypes.OBJECT_ELEMENT
        )
        data_type = DeclTypes.checkType(data_type, packages.getElements())
        decl_unique, decl_index = self.module.declarations.addElement(
            Declaration(
                data_type,
                identifier,
                assign_name,
                size_expression,
                0,
                "",
                0,
                expression.getSourceInterval(),
            )
        )

        declaration = self.module.declarations.getElementByIndex(decl_index)
        sv_structure.elements.addElement(declaration)

        self.module.name_change.addElement(
            NameChange(identifier, expression.getSourceInterval(), original_identifier)
        )

        return identifier
    return None


def forDeclaration2ApanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.For_variable_declarationContext,
    sv_structure: Structure,
):
    """This function processes a SystemVerilog for loop variable declaration and adds it to a module's
    declarations.

    Parameters
    ----------
    self : SV2aplan
        The `self` parameter in the `forDeclaration2ApanImpl` method refers to an instance of the
    `SV2aplan` class. It is used to access the attributes and methods of the class within the method
    implementation.
    ctx : SystemVerilogParser.For_variable_declarationContext
        The `ctx` parameter in the `forDeclaration2ApanImpl` function is of type
    `SystemVerilogParser.For_variable_declarationContext`. It is used to extract information about the
    variable declaration within a for loop in a SystemVerilog code snippet. This context object provides
    access to the data type

    """
    assign_name = ""
    data_type = ctx.data_type().getText()
    size_expression = data_type
    if ctx.expression(0) is not None:
        action_txt = (
            f"{ctx.variable_identifier(0).getText()} = {ctx.expression(0).getText()}"
        )
        (
            action_pointer,
            assign_name,
            source_interval,
            uniq_action,
        ) = self.expression2Aplan(
            ctx, ElementsTypes.ASSIGN_ELEMENT, sv_structure, ElementsTypes.LOOP_ELEMENT
        )

    data_type = DeclTypes.checkType(data_type, [])
    identifier = ctx.variable_identifier(0).getText()
    decl_unique, decl_index = self.module.declarations.addElement(
        Declaration(
            data_type,
            identifier,
            assign_name,
            size_expression,
            0,
            "",
            0,
            ctx.getSourceInterval(),
            ElementsTypes.NONE_ELEMENT,
            action_pointer,
        )
    )
    declaration = self.module.declarations.getElementByIndex(decl_index)
    sv_structure.elements.addElement(declaration)
