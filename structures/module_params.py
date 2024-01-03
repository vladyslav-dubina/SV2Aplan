class Parametr():
    def __init__(self, name:str, value:str ):
        self.name = name
        self.value = value
    
    def __str__(self):
        return "{0} = {1} ".format(self.name, self.value)