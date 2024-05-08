from structures.module_params import Parametr
from analyzer import SystemVerilogFind
import os


class Program():
    def __init__(self) -> None:
        self.module_identifier = ''
        self.module_parametrs = []
        self.module_inputs = []
        self.module_outputs = []
        self.internal_signals = []
        self.not_blocked_prot = []
        self.behaviour = ''
        self.actions = ''
        self.identifier = ''
        self.inp_sensetive_list = []
        self.beh_counter = 0
        self.parameters = []

        self.inputs_flag = False
        self.output_flag = False
        self.internal_flag = False
        self.finder = SystemVerilogFind()

    def setUp(self, path):
        print('Set up env')
        f = open(path, "r")
        data = f.read()
        f.close()
        self.finder.setUp(data)
        self.createResDir()

    def setData(self, input):
        self.module_identifier = input[0]
        self.module_parametrs = input[1]
        self.module_inputs = input[2]
        self.module_outputs = input[3]
        self.internal_signals = input[4]
        self.not_blocked_prot = input[5]
        self.identifier = input[6]
        self.actions = input[7]
        self.behaviour = input[8]
        self.inp_sensetive_list = input[9]
        self.beh_counter = input[10]
        self.parameters = input[11]

        if (len(self.module_inputs) > 0):
            self.inputs_flag = True

        if (len(self.module_outputs) > 0):
            self.output_flag = True

        if (len(self.internal_signals) > 0):
            self.internal_flag = True

    def paramsPrint(self):
        result = ''
        for elem in self.module_parametrs:
            result += '\t' + elem.__str__() + '\n'
        return result

    def printArray(self, array, assignmentFlag):
        result = ''
        for elem in array:
            if (assignmentFlag):
                result += '\t{0} = {1}\n'.format(elem[0], elem[1])
            else:
                result += '\t{0}\n'.format(elem)
        return result

    def createResDir(self):
        if (not os.path.exists('results')):
            os.mkdir('results')

    def writeToFile(self, path, data):
        f = open(path, "w")
        f.write(data)
        f.close()

    def createEVT(self):
        evt = 'events(\n'
        for elem in self.module_inputs:
            evt += '\ts_{0}:obj(x1:Bits 64);\n'.format(elem)
        evt += ');'
        self.writeToFile('results/project.evt_descript', evt)

    def createENV(self):
        env = 'environment (\n'  # Open env

        # ----------------------------------
        # Types
        # ----------------------------------
        env += '\ttypes : obj (Nil);\n'

        # ----------------------------------
        # Attributes
        # ----------------------------------

        env += '\tattributes : obj (Nil);\n'

        # ----------------------------------
        # Agents types
        # ----------------------------------

        env += '\tagent_types : obj (\n'

        if (self.inputs_flag or self.output_flag or self.internal_flag):

            env += '\t\t{0} : obj (\n'.format(self.identifier.upper())

            for index, elem in enumerate(self.internal_signals):
                if (index > 0):
                    env += ',\n'
                env += '\t\t\t{0}:bool'.format(elem)
                if (index + 1 == len(self.internal_signals)):
                    if (len(self.module_inputs) > 0):
                        env += ',\n'
                    else:
                        env += '\n'

            for index, elem in enumerate(self.module_inputs):
                if (index > 0):
                    env += ',\n'
                env += '\t\t\t{0}:Bits 64'.format(elem)
                if (index + 1 == len(self.module_inputs)):
                    if (len(self.module_outputs) > 0):
                        env += ',\n'
                    else:
                        env += '\n'

            for index, elem in enumerate(self.module_outputs):
                if (index > 0):
                    env += ',\n'
                env += '\t\t\t{0}:Bits 64'.format(elem)
                if (index + 1 == len(self.module_outputs)):
                    env += '\n'

            env += '\t\t)\n'

        env += '\t);\n'

        # ----------------------------------
        # Agents
        # ----------------------------------
        env += '\tagents : obj (\n'
        if (self.inputs_flag or self.output_flag or self.internal_flag):
            env += '\t\t{0} : obj (code),\n'.format(self.identifier.upper())
        env += '\t\tENVIRONMENT : obj (env)\n'
        env += '\t);\n'

        # ----------------------------------
        # Axioms
        # ----------------------------------
        env += '\taxioms : obj (Nil);\n'

        # ----------------------------------
        # Logic formula
        # ----------------------------------
        env += '\tlogic_formula : obj (1)\n'
        env += ');'  # Close env

        self.writeToFile('results/project.env_descript', env)

    def createAction(self):
        # ----------------------------------
        # Actions
        # ----------------------------------
        act = ''
        act += self.actions
        remove_index = act.rfind(',')
        act = act[:remove_index] + act[remove_index+1:]
        self.writeToFile('results/project.act', act)

    def createBeh(self):
        # ----------------------------------
        # Behaviour
        # ----------------------------------
        beh = self.behaviour
        beh_part2 = ''
        for i in range(self.beh_counter - 1):
            beh_part2 += '\n\t\t\t\tSensetive({0}'.format(self.inp_sensetive_list[i])
            beh_part2 += ')'
            if (i+1 < self.beh_counter - 1):
                beh_part2 += ' ||'

        if (len(beh_part2) > 0):
            beh_part2 = '{ ' + beh_part2 + '\n\t}'

        beh_part1 = ''
        self.not_blocked_prot = self.not_blocked_prot[::-1]
        for i in range(len(self.not_blocked_prot)):
            beh_part1 += self.not_blocked_prot[i]
            if (i+1 != len(self.not_blocked_prot)):
                beh_part2 += '.'
        beh = 'B0 = ({0}.{1}),\n'.format(
            beh_part1, beh_part2) + beh
        remove_index = beh.rfind(',')
        beh = beh[:remove_index] + beh[remove_index+1:]
        self.parameters = list(dict.fromkeys(self.parameters))
        params_str = ''
        for i in range(len(self.parameters)):
            params_str += self.parameters[i]
            if (i+1 != len(self.parameters)):
                params_str += ', '
        self.writeToFile('results/project.behp', beh)

    def createAplan(self):
        self.createEVT()
        self.createENV()
        self.createAction()
        self.createBeh()


program = Program()
program.setUp("example.sv")
analyze_result = program.finder.start_analyze()
program.setData(analyze_result)
program.createAplan()
