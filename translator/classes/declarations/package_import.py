import typing
from antlr4_verilog.systemverilog import SystemVerilogParser
from AppModule.app.classes.actions import Action
from AppModule.app.classes.declarations import Declaration
from AppModule.app.classes.element_types import ElementsTypes
from AppModule.app.classes.protocols import BodyElement, Protocol
from AppModule.app.classes.structure import Structure
from AppModule.app.classes.tasks import Task
from AppModule.app.classes.typedef import Typedef
from AppModule.app.classes.value_parametrs import ValueParametr
from translator.classes.base_translator import BaseTranslator
from translator.translation_mngr import TranslationManager


class PackageImportDeclTranslator(BaseTranslator):
    if typing.TYPE_CHECKING:
        from translator.translator import Translator

    def __init__(self, translator: "Translator"):
        super().__init__(translator)

    def translate(
        self, ctx: SystemVerilogParser.Package_import_declarationContext
    ) -> None:
        for element in ctx.package_import_item():
            package_identifier = element.package_identifier()
            package_identifier = package_identifier.getText()
            if package_identifier is not None:
                package_program = self._program.design_units.getElement(
                    package_identifier
                )
                if package_program is None:
                    previous_file_path = self._program.file_path
                    file_path = self.file_mngr.replace_filename(
                        self._program.file_path, f"{package_identifier}.sv"
                    )
                    file_data = self._program.readFileData(file_path)

                    translation_mngr = TranslationManager()
                    translation_mngr.setUp(file_data)
                    translation_mngr.startTranslate()

                    self._program.file_path = previous_file_path

                package = self._program.design_units.findModuleByUniqIdentifier(
                    package_identifier
                )
                if package is not None:
                    identifier = element.identifier()

                    if identifier is not None:
                        identifier = identifier.getText()

                        # Search for imported items
                        result = package.findElementByIdentifier(identifier)
                        for design_unit_element in result:
                            if isinstance(design_unit_element, Declaration):
                                self.design_unit.declarations.addElement(
                                    design_unit_element
                                )
                            elif isinstance(design_unit_element, Action):
                                self.design_unit.actions.addElement(design_unit_element)
                            elif isinstance(design_unit_element, Structure):
                                self.design_unit.structures.addElement(
                                    design_unit_element
                                )
                            elif isinstance(design_unit_element, Task):
                                self.design_unit.tasks.addElement(design_unit_element)
                            elif isinstance(design_unit_element, Protocol):
                                self.design_unit.out_of_block_elements.addElement(
                                    design_unit_element
                                )
                            elif isinstance(design_unit_element, ValueParametr):
                                self.design_unit.value_parametrs.addElement(
                                    design_unit_element
                                )
                            elif isinstance(design_unit_element, Typedef):
                                design_unit_element.file_path = self._program.file_path
                                self.design_unit.typedefs.addElement(
                                    design_unit_element
                                )

                        self._program.design_units.removeElement(
                            package
                        )  # remove after take all needed elements
                    else:
                        if len(package.getBehInitProtocols()) > 0:
                            self.counters.incriese(self.counters.types.B_COUNTER)
                            call_b = "PACKAGE_IMPORT_B_{}".format(
                                self.counters.get(self.counters.types.B_COUNTER)
                            )
                            struct_call = Protocol(
                                call_b,
                                ctx.getSourceInterval(),
                                ElementsTypes.MODULE_CALL_ELEMENT,
                            )
                            struct_call.addBodyElement(
                                BodyElement(
                                    identifier=f"B_{package_identifier.upper()}",
                                    element_type=ElementsTypes.PROTOCOL_ELEMENT,
                                )
                            )
                            self.design_unit.out_of_block_elements.addElement(
                                struct_call
                            )

                        self.design_unit.packages_and_objects.addElement(package)
