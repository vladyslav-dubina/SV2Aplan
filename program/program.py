from utils.string_formating import removeTrailingComma
from utils.utils import printWithColor, Color
from classes.module import ModuleArray
from classes.module_call import ModuleCallArray
import os


class Program:
    def __init__(self, path_to_result: str = None) -> None:
        self.path_to_result = path_to_result
        self.modules: ModuleArray = ModuleArray()
        self.module_calls: ModuleCallArray = ModuleCallArray()

    def readFileData(self, path):
        self.file_path = path
        printWithColor(
            f"===============================================================================\n",
            Color.BLUE,
        )
        printWithColor(f"Read SV file {path}\n", Color.BLUE)
        f = open(path, "r")
        data = f.read()
        f.close()
        return data

    def createResDir(self):
        if self.path_to_result is not None:
            last_char = self.path_to_result[-1]
            if last_char != os.sep:
                self.path_to_result += os.sep
        else:
            self.path_to_result = "results" + os.sep
        printWithColor(
            'Path to result: "{0}"\n'.format(self.path_to_result), Color.ORANGE
        )

        if not os.path.exists(self.path_to_result[:-1]):
            os.mkdir(self.path_to_result[:-1])

    def writeToFile(self, path, data):
        f = open(path, "w")
        f.write(data)
        f.close()

    def createEVT(self):
        evt = "events(\n"
        for module in self.modules.getElements():
            for elem in module.declarations.getInputPorts():
                evt += "\ts_{0}:obj(x1:{1});\n".format(
                    elem.identifier, elem.getAplanDecltype()
                )
        evt += ");"
        self.writeToFile(self.path_to_result + "project.evt_descript", evt)
        printWithColor(".evt_descript file created \n", Color.PURPLE)

    def createENV(self):
        env = "environment (\n"  # Open env

        # ----------------------------------
        # Types
        # ----------------------------------
        env += "\ttypes : obj (\n"
        sub_env = ""
        for module in self.modules.getElements():
            decls = module.declarations.getElementsForTypes()

            for index, elem in enumerate(decls):
                if index > 0:
                    sub_env += ",\n"
                sub_env += "\t\t\t{0}:({1})".format(elem.identifier, elem.expression)
                if index + 1 == len(decls):
                    sub_env += "\n"
        if len(sub_env) > 0:
            env += sub_env
        else:
            env += "\t\t\tNil\n"
        env += "\t);\n"

        # ----------------------------------
        # Attributes
        # ----------------------------------

        env += "\tattributes : obj (Nil);\n"

        # ----------------------------------
        # Agents types
        # ----------------------------------

        env += "\tagent_types : obj (\n"

        for module in self.modules.getElements():
            env += "\t\t{0} : obj (\n".format(module.identifier)
            sub_env = ""
            decls = module.declarations.getElementsForAgent()
            for index, elem in enumerate(decls):
                if index > 0:
                    sub_env += ",\n"
                sub_env += "\t\t\t{0}:{1}".format(
                    elem.identifier, elem.getAplanDecltype()
                )
                if index + 1 == len(decls):
                    sub_env += "\n"
            if len(sub_env) > 0:
                env += sub_env
            else:
                env += "\t\t\tNil\n"
            env += "\t\t),\n"
        env += "\t\tENVIRONMENT:obj(Nil)\n"
        env += "\t);\n"

        # ----------------------------------
        # Agents
        # ----------------------------------
        env += "\tagents : obj (\n"
        for module in self.modules.getElements():
            env += "\t\t{0} : obj ({1}),\n".format(
                module.identifier, module.ident_uniq_name
            )
        env += "\t\tENVIRONMENT : obj (env)\n"
        env += "\t);\n"

        # ----------------------------------
        # Axioms
        # ----------------------------------
        env += "\taxioms : obj (Nil);\n"

        # ----------------------------------
        # Logic formula
        # ----------------------------------
        env += "\tlogic_formula : obj (1)\n"
        env += ");"  # Close env

        self.writeToFile(self.path_to_result + "project.env_descript", env)
        printWithColor(".env_descript file created \n", Color.PURPLE)

    def createAction(self):
        # ----------------------------------
        # Actions
        # ----------------------------------
        actions = ""
        for index, module in enumerate(self.modules.getElements()):
            if index != 0:
                actions += ","
            actions += module.actions.getActionsInStrFormat()
        self.writeToFile(self.path_to_result + "project.act", actions)
        printWithColor(".act file created \n", Color.PURPLE)

    def createBeh(self):
        # ----------------------------------
        # Behaviour
        # ----------------------------------
        behaviour = ""
        for index, module in enumerate(self.modules.getElements()):
            if index != 0:
                behaviour += ",\n"
            behaviour += f"{module.getBehInitProtocols()}"
            behaviour += module.structures.getStructuresInStrFormat()

            if module.isIncludeOutOfBlockElements():
                behaviour += module.out_of_block_elements.getProtocolsInStrFormat()
            else:
                behaviour = removeTrailingComma(behaviour)
                #behaviour += "\n"
        self.writeToFile(self.path_to_result + "project.behp", behaviour)
        printWithColor(".beh file created \n", Color.PURPLE)

    def createAplanFiles(self):
        self.createEVT()
        self.createENV()
        self.createAction()
        self.createBeh()
        printWithColor("The translation was successfully completed! \n", Color.ORANGE)
