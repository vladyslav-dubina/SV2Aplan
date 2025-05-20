from antlr4_verilog.systemverilog import SystemVerilogParser
from classes.counters import CounterTypes
from classes.declarations import DeclTypes, Declaration
from classes.typedef import Typedef
from translator.classes.base_translator import BaseTranslator
from utils.utils import (
    Counters_Object,
)


class TypedefDeclTranslator(BaseTranslator):
    from translator.translator import Translator

    def __init__(self, translator: Translator):
        super().__init__(translator)

    def translate(self, ctx: SystemVerilogParser.Data_declarationContext) -> None:
        type_declaration: SystemVerilogParser.Type_declarationContext | None = (
            ctx.type_declaration()
        )
        if type_declaration is not None:
            data_type: SystemVerilogParser.Data_typeContext | None = (
                type_declaration.data_type()
            )
            if data_type.ENUM() or data_type.struct_union():
                for type_identifier in type_declaration.type_identifier():
                    enum_type_identifier = "{0}".format(type_identifier.getText())
                    unique_identifier = "{0}_{1}".format(
                        enum_type_identifier,
                        Counters_Object.getCounter(CounterTypes.UNIQ_NAMES_COUNTER),
                    )
                    Counters_Object.incrieseCounter(CounterTypes.UNIQ_NAMES_COUNTER)
                    decl_type = DeclTypes.ENUM_TYPE

                    if data_type.struct_union():
                        decl_type = DeclTypes.STRUCT_TYPE

                    typedef = Typedef(
                        enum_type_identifier,
                        unique_identifier,
                        type_identifier.getSourceInterval(),
                        self.program.file_path,
                        decl_type,
                    )

                    if data_type.ENUM():
                        for index, enum_name_decl in enumerate(
                            data_type.enum_name_declaration()
                        ):
                            identifier = enum_name_decl.enum_identifier().getText()
                            new_decl = Declaration(
                                DeclTypes.ENUM,
                                identifier,
                                "",
                                "",
                                0,
                                "",
                                0,
                                enum_name_decl.getSourceInterval(),
                            )
                            typedef.declarations.addElement(new_decl)
                    elif data_type.struct_union():
                        self._translator_ptr.getTranslator(
                            "struct_decl"
                        ).structMembersToDeclarations(self, data_type, typedef)

                    if self.module:
                        decl_unique, decl_index = self.module.typedefs.addElement(
                            typedef
                        )
                    else:
                        decl_unique, decl_index = self.program.typedefs.addElement(
                            typedef
                        )
