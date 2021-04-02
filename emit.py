# Emitter object keeps track of the generated code and outputs it.
class Emitter:
    def __init__(self, fullPath):
        self.FullPath = fullPath
        self.Header = ""
        self.Code = ""

    def Emit(self, code):
        self.Code += code
    
    def EmitLine(self, code):
        self.Code += code + '\n'

    def HeaderLine(self, code):
        self.Header += code + '\n'

    def WriteFile(self):
        with open(self.FullPath, 'w') as outputFile:
            outputFile.write(self.Header + self.Code)