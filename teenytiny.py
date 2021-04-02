from lex import *
from parse import *
from emit import *

def main():
    # Checkpoint 1: Make sure nextChar/peekWork
    """
    input = "LET foobar = 123"
    lexer = Lexer(input)

    while lexer.Peek() != '\0':
        print(lexer.CurChar)
        lexer.NextChar()
    """

    # Checkpoint 2: Make sure that we can parse single character operators
    """
    input = "+- */!== == >>=<=<"
    lexer = Lexer(input)

    token = lexer.GetToken()
    while token.Kind != TokenType.EOF:
        print(token.Kind)
        token = lexer.GetToken()
    """
    
    # Checkpoint 3: Comments, strings, numbers,
    """ 
    input = "+-123 89.767 */!==#This is a comment == \n >\"THIS IS A STRING\">=<=<"
    lexer = Lexer(input)

    token = lexer.GetToken()
    while token.Kind != TokenType.EOF:
        print(str(token.Kind) + " " + token.Text)
        token = lexer.GetToken()
    """

    # Checkpoint 4: Finished Lexer
    """
    input = "IF+-123foo*THEN/"
    lexer = Lexer(input)

    token = lexer.GetToken()
    while token.Kind != TokenType.EOF:
        print(str(token.Kind) + " " + token.Text)
        token = lexer.GetToken()
    """

    # Checkpoint 5: Starting Parser
    """
    print("Teeny Tiny Compiler")

    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    with open(sys.argv[1], 'r') as inputFile:
        input = inputFile.read()

    # Initialize the lexer and the parser
    lexer = Lexer(input)
    parser = Parser(lexer)

    parser.Parse()
    print("Parsing completed.")
    """

    # Checkpoint 6: Starting emitter
    print("Teeny Tiny Compiler")

    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument.")
    with open(sys.argv[1], 'r') as inputFile:
        input = inputFile.read()

    # Initialize the lexer and the parser and the emitter
    lexer = Lexer(input)
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)

    parser.Parse()
    emitter.WriteFile()
    print("Compiling completed.")

main()