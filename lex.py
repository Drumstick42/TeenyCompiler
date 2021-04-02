import enum
import sys

class Lexer:
    def __init__(self, input):
        self.Source = input + '\n' #Source code to lex. \n just makes it easier to parse last statement.
        self.CurChar = '' # Current character in the string
        self.CurPos = -1 # Current position in the string
        self.NextChar()

    # Process next character.
    def NextChar(self):
        self.CurPos += 1
        if self.CurPos >= len(self.Source):
            self.CurChar = '\0' #EOF
        else:
            self.CurChar = self.Source[self.CurPos]

    # Return the lookahead character.
    def Peek(self):
        if self.CurPos + 1 >= len(self.Source):
            return '\0'
        return self.Source[self.CurPos + 1]

    # Invalid token found, print error message and exit
    def Abort(self, message):
        sys.exit("Lexing error. " + message)

    # Skip whitespace except newlines, which we will use to indicate the end of a statement
    def SkipWhitespace(self):
        while self.CurChar == ' ' or self.CurChar == '\t' or self.CurChar == '\r':
            self.NextChar()

    # Skip comments in the code
    def SkipComment(self):
        if self.CurChar == '#':
            while self.CurChar != '\n':
                self.NextChar()

    # Return the next token
    def GetToken(self):
        self.SkipWhitespace()
        self.SkipComment()
        token = None

        # Check the first character of this token to see if we can decide what it is.
        # If it is a multiple character operator (e.g., !=), number, identifier, or keyword then we will process the rest.
        
        # Operators
        if self.CurChar == '+':
            token = Token(self.CurChar, TokenType.PLUS)
        
        elif self.CurChar == '-':
            token = Token(self.CurChar, TokenType.MINUS)
        
        elif self.CurChar == '*':
            token = Token(self.CurChar, TokenType.ASTERISK)
        
        elif self.CurChar == '/':
            token = Token(self.CurChar, TokenType.SLASH)
        
        elif self.CurChar == '=':
            if self.Peek() == '=':
                self.NextChar()
                token = Token('==', TokenType.EQ)
            else:
                token = Token(self.CurChar, TokenType.ASSIGN)
        
        elif self.CurChar == '!':
            if self.Peek() == '=':
                prevChar = self.CurChar
                self.NextChar()
                token = Token(prevChar + self.CurChar, TokenType.NEQ)
        
        elif self.CurChar == '<':
            if self.Peek() == '=':
                prevChar = self.CurChar
                self.NextChar()
                token = Token(prevChar + self.CurChar, TokenType.LTEQ)
            else:
                token = Token(self.CurChar, TokenType.LT)

        elif self.CurChar == '>':
            if self.Peek() == '=':
                prevChar = self.CurChar
                self.NextChar()
                token = Token(prevChar + self.CurChar, TokenType.GTEQ)
            else:
                token = Token(self.CurChar, TokenType.GT)        

        # String
        elif self.CurChar == '\"':
            self.NextChar()
            startPos = self.CurPos
            while self.CurChar != '\"':
                if self.CurChar == '\r' or self.CurChar == '\n' or self.CurChar == '\t' or self.CurChar == '\\' or self.CurChar == '%':
                    self.Abort("Illegal character in string: " + self.CurChar)
                self.NextChar()
            token = Token(self.Source[startPos : self.CurPos], TokenType.STRING)

        # Number
        elif self.CurChar.isdigit():
            startPos = self.CurPos
            while self.Peek().isdigit():
                self.NextChar()
            if self.Peek() == ".":
                self.NextChar()
                if not self.Peek().isdigit():
                    self.Abort("Decimal must be followed by atleast one number")
                while self.Peek().isdigit():
                    self.NextChar()
            
            tokText = self.Source[startPos:self.CurPos + 1]
            token = Token(tokText, TokenType.NUMBER)

        # Identifiers and keywords
        elif self.CurChar.isalpha():
            startPos = self.CurPos
            while self.Peek().isalnum():
                self.NextChar()
            tokText = self.Source[startPos:self.CurPos + 1]
            keyword = Token.CheckIfKeyword(tokText)
            if keyword is None:
                token = Token(tokText, TokenType.IDENT)
            else:
                token = Token(tokText, keyword)

        elif self.CurChar == '\n':
            token = Token(self.CurChar, TokenType.NEWLINE)
        
        elif self.CurChar == '\0':
            token = Token('', TokenType.EOF)

        if token == None:
            # Unknown token
            self.Abort("Unknown token: " + self.CurChar)
            pass
        
        self.NextChar() # token is parsed. Go to the next one.
        return token

# Token contains the original text, and the type of token. Both of which we'll need later on
class Token:
    def __init__(self, tokenText, tokenKind): 
        self.Text = tokenText # tokens actual text need for numbers, identifiers and strings
        self.Kind = tokenKind # type

    @staticmethod
    def CheckIfKeyword(tokenText):
        for kind in TokenType:
            if kind.name == tokenText and kind.value >= 100 and kind.value < 200:
                return kind
        return None   

class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    
    # Keywords.
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111

    # Operators
    ASSIGN = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQ = 206
    NEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211