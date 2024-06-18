from translator.translator import SystemVerilogFinder
from utils import printWithColor, Color, removeTrailingComma
from classes.aplan import Module
from typing import List
import os


class Program:
    def __init__(self, path_to_result: str = None) -> None:
        self.path_to_result = path_to_result
        self.modules: List[Module]
        self.finder = SystemVerilogFinder()

    def setUp(self, path):
        printWithColor("Set up tranlator environment \n", Color.ORANGE)
        f = open(path, "r")
        data = f.read()
        f.close()
        self.finder.setUp(data)

    def setData(self, input):
        self.modules = input

    def createResDir(self):
        if self.path_to_result is not None:
            last_char = self.path_to_result[-1]
            if last_char != os.sep:
                self.path_to_result += os.sep
        else:
            self.path_to_result = "results" + os.sep
        printWithColor(
            'Path to result: "{0}"'.format(self.path_to_result), Color.ORANGE
        )

        if not os.path.exists(self.path_to_result[:-1]):
            os.mkdir(self.path_to_result[:-1])

    def writeToFile(self, path, data):
        f = open(path, "w")
        f.write(data)
        f.close()

    def createEVT(self):
        evt = "events(\n"
        for module in self.modules:
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
        env += "\ttypes : obj (Nil);\n"

        # ----------------------------------
        # Attributes
        # ----------------------------------

        env += "\tattributes : obj (Nil);\n"

        # ----------------------------------
        # Agents types
        # ----------------------------------

        env += "\tagent_types : obj (\n"

        for module in self.modules:
            env += "\t\t{0} : obj (\n".format(module.identifier)
            decls = module.declarations.getElements()
            for index, elem in enumerate(decls):
                if index > 0:
                    env += ",\n"
                env += "\t\t\t{0}:{1}".format(elem.identifier, elem.getAplanDecltype())
                if index + 1 == len(decls):
                    env += "\n"

            env += "\t\t),\n"
        env += "\t\tENVIRONMENT:obj(Nil)\n"
        env += "\t);\n"

        # ----------------------------------
        # Agents
        # ----------------------------------
        env += "\tagents : obj (\n"
        for module in self.modules:
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
        for module in self.modules:
            actions += module.actions.getActionsInStrFormat()
        self.writeToFile(self.path_to_result + "project.act", actions)
        printWithColor(".act file created \n", Color.PURPLE)

    def createBeh(self):
        # ----------------------------------
        # Behaviour
        # ----------------------------------
        behaviour = ""
        for module in self.modules:
            behaviour += f"{module.getBehInitProtocols()}"
            behaviour += module.structures.getStructuresInStrFormat()

            if module.isIncludeOutOfBlockElements():
                behaviour += module.out_of_block_elements.getProtocolsInStrFormat() + "\n"
            else:
                behaviour = removeTrailingComma(behaviour)
                behaviour += "\n"
        self.writeToFile(self.path_to_result + "project.behp", behaviour)
        printWithColor(".beh file created \n", Color.PURPLE)
        
    def prepareToTranslation(self):
        for module in self.modules:
            module.declarations.recalculateSizeExpressions(module.parametrs)

    def createAplanFiles(self):
        self.prepareToTranslation()
        self.createEVT()
        self.createENV()
        self.createAction()
        self.createBeh()
        printWithColor("The translation was successfully completed! \n", Color.ORANGE)
