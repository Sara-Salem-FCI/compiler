def is_digit(char):
    return '0' <= char <= '9'

def is_whitespace(char):
    return char in ' \t\n\r'

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
    if not string or not string[0].isalpha():
        return False
    return all(char.isalnum() for char in string)

KEYWORDS = {'if', 'print', 'in', 'else', 'for', 'while', 'return', 'int', 'float',
            'range', 'string', 'elif', 'pass', 'break', 'continue', 'True', 
            'False', 'and', 'or', 'not', 'begin', 'end'} 

def is_keyword(string):
    return string in KEYWORDS

def is_curly_brace(char):
    return char in '{}'

def lex(source_code):
    tokens = []  
    i = 0
    
    while i < len(source_code):
        char = source_code[i]
        print(f"Processing character '{char}' at index {i}")
        
        if is_whitespace(char):
            i += 1
            continue

        if is_digit(char) or (char == '.' and i + 1 < len(source_code) and is_digit(source_code[i + 1])):
            num = char
            is_float = char == '.' 
            while i + 1 < len(source_code) and (is_digit(source_code[i + 1]) or (source_code[i + 1] == '.' and not is_float)):
                if source_code[i + 1] == '.':
                    is_float = True
                num += source_code[i + 1]
                i += 1
            tokens.append(('FLOAT' if is_float else 'NUMBER', num))
            i += 1
            continue

        if is_square_bracket(char):
            tokens.append(('SQUARE_BRACKET', char))
            i += 1
            continue

        if is_curly_brace(char):
            tokens.append(('CURLY_BRACKET', char))
            i += 1
            continue

        if i + 1 < len(source_code) and is_comparison_operator(source_code[i:i+2]):
            tokens.append(('COMPARISON_OPERATOR', source_code[i:i+2]))
            i += 2
            continue
        elif is_comparison_operator(char):
            tokens.append(('COMPARISON_OPERATOR', char))
            i += 1
            continue

        if i + 1 < len(source_code) and source_code[i:i+2] in ['+=', '-=', '*=', '/=']:
            tokens.append(('COMPOUND_OPERATOR', source_code[i:i+2]))
            i += 2
            continue

        if is_operator(char):
            tokens.append(('OPERATOR', char))
            i += 1
            continue

        if is_comma(char):
            tokens.append(('COMMA', char))
            i += 1
            continue

        if char == ';':
            tokens.append(('SEMICOLON', char)) 
            i += 1
            continue

        if is_qoutes(char):
            string_value = char 
            i += 1
            while i < len(source_code) and not is_qoutes(source_code[i]):
                string_value += source_code[i]
                i += 1
            if i < len(source_code):
                string_value += source_code[i]  
            tokens.append(('STRING', string_value))
            i += 1
            continue

        if is_paren(char):
            tokens.append(('PAREN', char))
            i += 1
            continue

        if char == ':':
            tokens.append(('COLON', char))
            i += 1
            continue

        if char.isalpha():  
            identifier = char
            while i + 1 < len(source_code) and source_code[i + 1].isalnum():
                identifier += source_code[i + 1]
                i += 1
            if is_keyword(identifier):
                tokens.append(('KEYWORD', identifier))
            else:
                tokens.append(('IDENTIFIER', identifier))
            i += 1
            continue

        if char == '#':  
            while i < len(source_code) and source_code[i] != '\n':
                i += 1
            continue

        print(f"Error at index {i}: '{char}'")
        raise SyntaxError(f'Unexpected character: {char}')

    return tokens

#========================================================

def read_source_code(file_path):
    with open(file_path, 'r') as file:
        return file.read()

source_file_path = 'source_code.txt'  
source_code = read_source_code(source_file_path)

try:
    print(f"Source Code:\n{source_code}")
    tokens = lex(source_code)
    print("Tokens:", tokens)
except SyntaxError as e:
    print(e)
