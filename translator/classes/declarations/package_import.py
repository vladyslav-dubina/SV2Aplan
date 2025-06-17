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
                package_program = self._program.modules.getElement(package_identifier)
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

                package = self._program.modules.findModuleByUniqIdentifier(
                    package_identifier
                )
                if package is not None:
                    identifier = element.identifier()

                    if identifier is not None:
                        identifier = identifier.getText()

                        # Search for imported items
                        result = package.findElementByIdentifier(identifier)
                        for module_element in result:
                            if isinstance(module_element, Declaration):
                                self.module.declarations.addElement(module_element)
                            elif isinstance(module_element, Action):
                                self.module.actions.addElement(module_element)
                            elif isinstance(module_element, Structure):
                                self.module.structures.addElement(module_element)
                            elif isinstance(module_element, Task):
                                self.module.tasks.addElement(module_element)
                            elif isinstance(module_element, Protocol):
                                self.module.out_of_block_elements.addElement(
                                    module_element
                                )
                            elif isinstance(module_element, ValueParametr):
                                self.module.value_parametrs.addElement(module_element)
                            elif isinstance(module_element, Typedef):
                                module_element.file_path = self._program.file_path
                                self.module.typedefs.addElement(module_element)

                        self._program.modules.removeElement(
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
                            struct_call.addBody(
                                BodyElement(
                                    identifier=f"B_{package_identifier.upper()}",
                                    element_type=ElementsTypes.PROTOCOL_ELEMENT,
                                )
                            )
                            self.module.out_of_block_elements.addElement(struct_call)

                        self.module.packages_and_objects.addElement(package)
