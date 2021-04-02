import sys
from lex import *
from emit import *

# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer, emitter):
        self.Lexer = lexer
        self.Symbols = set() # variables declared so far
        self.LabelsDeclared = set() # labels declared so far
        self.LabelsGotoed = set() # labels gotoed so far
        self.CurToken = None
        self.PeekToken = None
        self.Emitter = emitter
        self.NextToken()
        self.NextToken() # Call this twice to initialize current and peek

    # Return true if the current token matches.
    def CheckToken(self, kind):
        return kind == self.CurToken.Kind

    # Return true if the next token matches
    def CheckPeek(self, kind):
        return kind == self.PeekToken.Kind

    # Try to match current token. If not, error. Advances the current token.
    def Match(self, kind):
        if not self.CheckToken(kind):
            self.Abort("Expected " + kind.name + ", got " + self.CurToken.Kind.name)
        self.NextToken()

    # Advances the current token
    def NextToken(self):
        self.CurToken = self.PeekToken
        self.PeekToken = self.Lexer.GetToken()
        # No need to worry about passing the EOF, lexer handles that

    def Abort(self, message):
        sys.exit("Error: " + message)

    # Production rules

    def Parse(self):
        self.Program()

    def Program(self):
        self.Emitter.HeaderLine("#include <stdio.h>")
        self.Emitter.HeaderLine(("int main(void){"))

        while (self.CheckToken(TokenType.NEWLINE)):
            self.NextToken()

        while not self.CheckToken(TokenType.EOF):
            self.Statement()

        # Check that each label referenced in a GOT is declared.
        for label in self.LabelsGotoed:
            if label not in self.LabelsDeclared:
                self.Abort("Attempting to GOTO to undeclared label: " + label)

        self.Emitter.EmitLine("return 0;")
        self.Emitter.EmitLine("}")

    def Statement(self):
        # "PRINT (expresion | string)"
        if self.CheckToken(TokenType.PRINT):
            self.NextToken()
            if self.CheckToken(TokenType.STRING):
                self.Emitter.EmitLine("printf(\"" + self.CurToken.Text + "\\n\");")
                self.NextToken()
            else:
                self.Emitter.Emit("printf(\"%" + ".2f\\n\", (float)(")
                self.Expression()
                self.Emitter.EmitLine("));")
        
        # "IF" comparison "THEN" nl {statement} "ENDIF" nl
        elif self.CheckToken(TokenType.IF):
            self.NextToken()
            self.Emitter.emit("if (")
            self.Comparison()
            self.Match(TokenType.THEN)
            self.Nl()
            self.Emitter.EmitLine("){")
            # Zero or more statements in the body
            while not self.CheckToken(TokenType.ENDIF):
                self.Statement()
            self.Match(TokenType.ENDIF)
            self.Emitter.EmitLine("}")

        # "WHILE" comparison "REPEAT" nl {statement nl} "ENDWHILE" nl
        elif self.CheckToken(TokenType.WHILE):
            self.NextToken()
            self.Emitter.Emit("while (")
            self.Comparison()
            self.Match(TokenType.REPEAT)
            self.Nl()
            self.Emitter.Emit("){")
            while not self.CheckToken(TokenType.ENDWHILE):
                self.Statement()
            self.Match(TokenType.ENDWHILE)
            self.Emitter.EmitLine("}")

        # "LABEL" ident nl
        elif self.CheckToken(TokenType.LABEL):
            self.NextToken()
            if self.CurToken.Text in self.LabelsDeclared:
                self.Abort("Label already exists: " + self.CurToken.Text)
            self.LabelsDeclared.add(self.CurToken.Text)
            self.Emitter.EmitLine(self.CurToken.text + ":")
            self.Match(TokenType.IDENT)

        # "GOTO" ident nl
        elif self.CheckToken(TokenType.GOTO):
            self.NextToken()
            self.LabelsGotoed.add(self.CurToken.Text)
            self.Emitter.EmitLine("goto " + self.CurToken.Text + ";")
            self.Match(TokenType.IDENT)

        # "LET" ident "=" expression nl
        elif self.CheckToken(TokenType.LET):
            self.NextToken()
            if self.CurToken.Text not in self.Symbols:
                self.Symbols.add(self.CurToken.Text)
                self.Emitter.HeaderLine("float " + self.CurToken.Text + ";")
            self.Emitter.Emit(self.CurToken.Text + " = ")
            self.Match(TokenType.IDENT)
            self.Match(TokenType.ASSIGN)
            self.Expression()   
            self.Emitter.EmitLine(";")

        # "INPUT" ident
        elif self.CheckToken(TokenType.INPUT):
            self.NextToken()
            if self.CurToken.Text not in self.Symbols:
                self.Symbols.add(self.CurToken.Text)
                self.Emitter.HeaderLine("float " + self.CurToken.Text + ";")
            # Emit scanf but also validate the input. If invalid, set the variable to 0 and clear the input.
            self.Emitter.EmitLine("if (0 == scanf(\"%" + "f\", &" + self.CurToken.Text + ")) {")
            self.Emitter.EmitLine(self.CurToken.Text + " = 0;")
            self.Emitter.Emit("scanf(\"%")
            self.Emitter.EmitLine("*s\");")
            self.Emitter.EmitLine("}")
            self.Match(TokenType.IDENT)
        
        else:
            self.Abort("Invalid statement at " + self.CurToken.Text + " (" + self.CurToken.Kind.name +")")

        # Newline.
        self.Nl()

    # nl ::== '\n\+
    def Nl(self):
        self.Match(TokenType.NEWLINE)
        while self.CheckToken(TokenType.NEWLINE):
            self.NextToken()

    # expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
    def Comparison(self):
        self.Expression()
        if self.IsComparisonOperator():
            self.Emitter.Emit(self.CurToken.Text)
            self.NextToken()
            self.Expression()
            while self.IsComparisonOperator():
                self.Emitter.Emit(self.CurToken.Text)
                self.NextToken()
                self.Expression()
        else:
            self.Abort("Expected comparison operator")

    def IsComparisonOperator(self):
        return self.CheckToken(TokenType.EQ) or self.CheckToken(TokenType.NEQ) or self.CheckToken(TokenType.GT) or self.CheckToken(TokenType.GTEQ) or self.CheckToken(TokenType.LT) or self.CheckToken(TokenType.LTEQ)

    # term {("-"|"+") term}
    def Expression(self):
        self.Term()
        while self.CheckToken(TokenType.MINUS) or self.CheckToken(TokenType.PLUS):
            self.Emitter.Emit(self.CurToken.Text)
            self.NextToken()
            self.Term()

    # unary {("/"|"*") unary}
    def Term(self):
        self.Unary()
        while self.CheckToken(TokenType.ASTERISK) or self.CheckToken(TokenType.SLASH):
            self.Emitter.Emit(self.CurToken.Text)
            self.NextToken()
            self.Unary()

    # ["+" | "-"] primary
    def Unary(self):
        if self.CheckToken(TokenType.PLUS) or self.CheckToken(TokenType.MINUS):
            self.Emitter.Emit(self.CurToken.Text)
            self.NextToken()
        self.Primary()

    def Primary(self):
        if self.CheckToken(TokenType.NUMBER):
            self.Emitter.Emit(self.CurToken.Text)
            self.NextToken()
        elif self.CheckToken(TokenType.IDENT):
            # Ensure the variable already exists
            if self.CurToken.Text not in self.Symbols:
                self.Abort("Referencing variable before assignment: " + self.CurToken.Text)
            self.Emitter.Emit(self.CurToken.Text)
            self.NextToken()
        else:    
            self.Abort("Unexpected token at " + self.CurToken.Text)
