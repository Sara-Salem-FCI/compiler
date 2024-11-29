# Utility functions for identifying character types
def is_digit(char):
    return '0' <= char <= '9'

def is_whitespace(char):
    return char in ' \t\n\r'  # Includes newlines and carriage returns

def is_operator(char):
    return char in '+-*/='

def is_comparison_operator(char):
    return char in ['==', '!=', '<', '>', '<=', '>=']

def is_square_bracket(char):
    return char in '[]'

def is_paren(char):
    return char in '()'

def is_comma(char):
    return char == ','

def is_qoutes(char):
    return char == '"' or char == '\''


def is_identifier(string):
    # Check if the string is not empty and starts with a letter
    if not string or not string[0].isalpha():
        return False
    # Check if all characters are letters or digits
    return all(char.isalnum() for char in string)

# List of Python keywords
KEYWORDS = {'if', 'print', 'in', 'else', 'for', 'while', 'return', 'int', 'float', 
            'range', 'string', 'char', 'elif', 'pass', 'break', 'continue', 'True', 
            'False', 'and', 'or', 'not', 'begin', 'end'}  # Added 'begin' and 'end'

# Function to check if a string is a keyword
def is_keyword(string):
    return string in KEYWORDS

# Add the check for curly braces
def is_curly_brace(char):
    return char in '{}'

# Lexing function
def lex(source_code):
    tokens = []  # List to store tokens
    i = 0
    
    while i < len(source_code):
        char = source_code[i]
        print(f"Processing character '{char}' at index {i}")
        
        # Ignore whitespace
        if is_whitespace(char):
            i += 1
            continue

        # Parse numbers (Integers and Floats)
        if is_digit(char) or (char == '.' and i + 1 < len(source_code) and is_digit(source_code[i + 1])):
            num = char
            is_float = char == '.'  # Check if the number starts as a float
            while i + 1 < len(source_code) and (is_digit(source_code[i + 1]) or (source_code[i + 1] == '.' and not is_float)):
                if source_code[i + 1] == '.':
                    is_float = True
                num += source_code[i + 1]
                i += 1
            tokens.append(('FLOAT' if is_float else 'NUMBER', num))
            i += 1
            continue

        # Parse square brackets
        if is_square_bracket(char):
            tokens.append(('SQUARE_BRACKET', char))
            i += 1
            continue

        # Parse curly braces
        if is_curly_brace(char):
            tokens.append(('CURLY_BRACKET', char))
            i += 1
            continue

        # Parse comparison operators (==, !=, <, >, <=, >=)
        if i + 1 < len(source_code) and is_comparison_operator(source_code[i:i+2]):
            tokens.append(('COMPARISON_OPERATOR', source_code[i:i+2]))
            i += 2
            continue
        elif is_comparison_operator(char):
            tokens.append(('COMPARISON_OPERATOR', char))
            i += 1
            continue

        # Parse compound operators (+=, -=, *=, /=)
        if i + 1 < len(source_code) and source_code[i:i+2] in ['+=', '-=', '*=', '/=']:
            tokens.append(('COMPOUND_OPERATOR', source_code[i:i+2]))
            i += 2
            continue

        # Parse operators (+, -, *, /, =)
        if is_operator(char):
            tokens.append(('OPERATOR', char))
            i += 1
            continue

        # Parse commas
        if is_comma(char):
            tokens.append(('COMMA', char))
            i += 1
            continue

        # Parse semicolons
        if char == ';':
            tokens.append(('SEMICOLON', char))  # Token type for semicolon
            i += 1
            continue

        # Parse string and char literals
        if is_qoutes(char):
            string_value = char  # Start capturing the string
            i += 1
            while i < len(source_code) and not is_qoutes(source_code[i]):
                string_value += source_code[i]
                i += 1
            if i < len(source_code):
                string_value += source_code[i]  # Add the closing quote
            if len(string_value) == 3:
                tokens.append(('CHAR', string_value))    
            else: 
                tokens.append(('STRING', string_value))
            i += 1
            continue

        # Parse parentheses
        if is_paren(char):
            tokens.append(('PAREN', char))
            i += 1
            continue

        # Parse colons (':')
        if char == ':':
            tokens.append(('COLON', char))
            i += 1
            continue

        # Parse identifiers (variables and function names)
        if char.isalpha():  # Start with a letter
            identifier = char
            while i + 1 < len(source_code) and source_code[i + 1].isalnum():
                identifier += source_code[i + 1]
                i += 1
            # Check if the identifier is a keyword
            if is_keyword(identifier):
                tokens.append(('KEYWORD', identifier))
            else:
                tokens.append(('IDENTIFIER', identifier))
            i += 1
            continue

        # Handle comments
        if char == '#':  # Single line comment
            while i < len(source_code) and source_code[i] != '\n':  # Ignore everything till end of line
                i += 1
            continue

        # Unexpected character
        print(f"Error at index {i}: '{char}'")
        raise SyntaxError(f'Unexpected character: {char}')

    return tokens



# Function to read source code from a file
def read_source_code(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# Main execution

source_file_path = 'source_code.txt'  # Specify the path to your file
source_code = read_source_code(source_file_path)

try:
    print(f"Source Code:\n{source_code}")
    tokens = lex(source_code)
    print("Tokens:", tokens)
except SyntaxError as e:
    print(e)
