Followed the tutorial at http://web.eecs.utk.edu/~azh/blog/teenytinycompiler1.html

A compiler translastes code from one language into another. 
This compiles a fake language, Teeny Tiny, into C. Teeny Tiny will be a dialect of BASIC.

Any notes taken are below:

Compiling is a 3 step process:
    1.) Source code goes into the Lexer, which breaks it up into tokens.
        - Kinda like words in english.
    2.) Tokens are passed into the parser, which checks if the order of tokens is valid.
        - This is like checking the grammer to ensure it's sensible
    3.) The parser generates a program tree. That's passed to the emitter, which spits out our C code

Lexer:
    Iterates character by character to decide where each token starts/stops, and what kind of token it is.
    Combining characters together to form a token is a kind of state machine

    Main rules:
        Operator: one or two consecutive characters that match: +-*/=!<>
        String: Duuble quotes followed by zero or more characters and another double quotes
        Number: One or more numeric characters, followed by an optional decimal point and one or more numeric characters.
        Identifier: Alphabetical character followed by zero or more alphanumeric characters
        KeywordL Exact text match of: LABEL, GOTO, PRINT, INPUT, LET, IF, THEN, ENDIF, WHILE, REPEAT, ENDWHILE

Parser:
    Looks at tokens one at a time, deciding if the order is legal as defined by input language
    Input: The sequence of tokens
    Output: A parse tree. We will use the call stack to implicitly build the parse tree as we go.

    Compiler needs to generate errors when the input doesn't follow the code's defined grammar
    If you look at a sentence, you can build a tree that represents the structure. The parser does the same kind of thing.
    The grammar of a language is partly technical, and partly creative

    Rules:
        program ::= {statement} - Defines a grammar rule called program. A program is made up of one or more statements

        statement ::= "PRINT" (expression | string) nl - Defines a grammar rule for a valid statement. 
            - It must have the print keyword, followed by an expression (which is defined by another grammar rule) or a string, followed by a newline

    For TeenyTiny, the rules are:  
        program ::= {statement}
        statement ::= "PRINT" (expression | string) nl
            | "IF" comparison "THEN" nl {statement} "ENDIF" nl
            | "WHILE" comparison "REPEAT" nl {statement} "ENDWHILE" nl
            | "LABEL" ident nl
            | "GOTO" ident nl
            | "LET" ident "=" expression nl
            | "INPUT" ident nl
        comparison ::= expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)+
        expression ::= term {( "-" | "+" ) term}
        term ::= unary {( "/" | "*" ) unary}
        unary ::= ["+" | "-"] primary
        primary ::= number | ident
        nl ::= '\n'+

    There's a 1:1 mapping between py functions in the parser and grammar rules.
    {} -> 0 or more
    [] -> 0 or 1
    + -> one or more of whatever is to the left
    () -> logical grouping
    | -> logical or
    <word> -> either a reference to another grammar rule, or tokens defined in the lexer.
        - Author is surrounding keywords and operators as the quoted strings of text

Emitter:
    This produces the C code.
    Each function of the parser calls the emitter to produce the corresponding C code. Emitter utilizes the parse tree to emit C code in fragments