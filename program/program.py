from translator.translator import SystemVerilogFind
from utils import printWithColor, Color, removeTrailingComma
from structures.aplan import Module
import os


class Program:
    def __init__(self, path_to_result: str = None) -> None:
        self.path_to_result = path_to_result
        self.module: Module
        self.finder = SystemVerilogFind()

    def setUp(self, path):
        printWithColor("Set up tranlator environment \n", Color.ORANGE)
        f = open(path, "r")
        data = f.read()
        f.close()
        self.finder.setUp(data)
        self.createResDir()

    def setData(self, input):
        self.module = input

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
        print()

        if not os.path.exists(self.path_to_result[:-1]):
            os.mkdir(self.path_to_result[:-1])

    def writeToFile(self, path, data):
        f = open(path, "w")
        f.write(data)
        f.close()

    def createEVT(self):
        evt = "events(\n"
        for elem in self.module.getInputPorts():
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

        env += "\t\tENVIRONMENT:obj(Nil),\n"

        if (
            self.module.isIncludeInputPorts()
            or self.module.isIncludeOutputPorts()
            or self.module.isIncludeWires()
            or self.module.isIncludeRegs()
        ):

            env += "\t\t{0} : obj (\n".format(self.module.identifier)

            regs = self.module.getRegs()
            for index, elem in enumerate(regs):
                if index > 0:
                    env += ",\n"
                env += "\t\t\t{0}:{1}".format(elem.identifier, elem.getAplanDecltype())
                if index + 1 == len(regs):
                    if (
                        self.module.isIncludeWires()
                        or self.module.isIncludeInputPorts()
                        or self.module.isIncludeOutputPorts()
                    ):
                        env += ",\n"
                    else:
                        env += "\n"

            wires = self.module.getWires()
            for index, elem in enumerate(wires):
                if index > 0:
                    env += ",\n"
                env += "\t\t\t{0}:{1}".format(elem.identifier, elem.getAplanDecltype())
                if index + 1 == len(wires):
                    if (
                        self.module.isIncludeInputPorts()
                        or self.module.isIncludeOutputPorts()
                    ):
                        env += ",\n"
                    else:
                        env += "\n"

            include_ports = self.module.getInputPorts()
            for index, elem in enumerate(include_ports):
                if index > 0:
                    env += ",\n"
                env += "\t\t\t{0}:{1}".format(elem.identifier, elem.getAplanDecltype())
                if index + 1 == len(include_ports):
                    if self.module.isIncludeOutputPorts():
                        env += ",\n"
                    else:
                        env += "\n"

            output_ports = self.module.getOutputPorts()
            for index, elem in enumerate(output_ports):
                if index > 0:
                    env += ",\n"
                env += "\t\t\t{0}:{1}".format(elem.identifier, elem.getAplanDecltype())
                if index + 1 == len(output_ports):
                    env += "\n"

            env += "\t\t)\n"

        env += "\t);\n"

        # ----------------------------------
        # Agents
        # ----------------------------------
        env += "\tagents : obj (\n"
        if (
            self.module.isIncludeInputPorts
            or self.module.isIncludeOutputPorts()
            or self.module.isIncludeWires()
            or self.module.isIncludeRegs()
        ):
            env += "\t\t{0} : obj ({1}),\n".format(
                self.module.identifier, self.module.ident_uniq_name
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

        actions = self.module.getActionsInStrFormat()
        self.writeToFile(self.path_to_result + "project.act", actions)
        printWithColor(".act file created \n", Color.PURPLE)

    def createBeh(self):
        # ----------------------------------
        # Behaviour
        # ----------------------------------
        behaviour = ""
        behaviour += "B = ({})".format(self.module.getBehInitProtocols())
        behaviour += "," + self.module.getStructuresInStrFormat()

        if self.module.isIncludeNonBlockElements():
            behaviour += "," + self.module.getNotBlockElementsInStrFormat() + "\n"
        else:
            behaviour += "\n"
        self.writeToFile(self.path_to_result + "project.behp", behaviour)
        printWithColor(".beh file created \n", Color.PURPLE)

    def createAplanFiles(self):
        self.createEVT()
        self.createENV()
        self.createAction()
        self.createBeh()
        printWithColor("The translation was successfully completed! \n", Color.ORANGE)
