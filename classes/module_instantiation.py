from classes.basic import Basic, BasicArray
import re


class ModuleInstantiation(Basic):
    def extractParametrsAndValues(self, expression):
        result = []
        matches = re.findall(r"\.(.+?)\b\s*\((.+?)\)", expression)
        for element in matches:
            result.append(element)

        return result

    def __init__(
        self,
        source_identifier: str,
        destination_identifier: str,
        parameter_value_assignment: str,
    ):
        super().__init__(
            "",
            (0, 0),
        )
        self.source_identifier = source_identifier
        self.destination_identifier = destination_identifier
        self.parametrs_for_assignment = self.extractParametrsAndValues(
            parameter_value_assignment
        )

    def __repr__(self):
        return "\tModuleInstantiation(\n\t\t{0},\n\t\t{1},\n\t\t{2}\n\t)\n".format(
            self.source_identifier,
            self.destination_identifier,
            self.parametrs_for_assignment,
        )


class ModuleInstantiationArray(BasicArray):
    def __init__(self):
        super().__init__(ModuleInstantiation)

    def __repr__(self):
        return f"ModuleInstantiationArray(\n{self.elements!r}\n)"
