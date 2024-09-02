from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.declarations import DeclTypes, Declaration
from translator.system_verilog_to_aplan import SV2aplan


def enumDecaration2AplanImpl(
    self: SV2aplan,
    ctx: SystemVerilogParser.Data_declarationContext,
):

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

                if self.module:
                    decl_unique, decl_index = self.module.declarations.addElement(
                        new_decl
                    )
                else:
                    decl_unique, decl_index = self.program.typedefs.addElement(new_decl)
