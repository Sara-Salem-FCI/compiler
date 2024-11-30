from typing import List, Tuple
from source_code_to_tokens_and_lexems import tokens
class Parser:
    def __init__(self, tokens: List[Tuple[str, str]]):
        self.tokens = tokens
        self.index = 0

    def current_token(self):
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def advance(self):
        if self.index < len(self.tokens):
            self.index += 1

    def match(self, expected_type):
        token = self.current_token()
        if token and token[0] == expected_type:
            self.advance()
            return token
        raise SyntaxError(f"Expected {expected_type}, but got {token}")

    def parse(self):
        return self.parse_program()

    def parse_program(self):
        self.match('KEYWORD')  # 'begin'
        self.match('CURLY_BRACKET')  # '{'
        node = ParseNode("Program")
        node.children = self.parse_statement_list()
        self.match('CURLY_BRACKET')  # '}'
        self.match('KEYWORD')  # 'end'
        return node

    def parse_statement_list(self):
        statements = []
        while self.current_token() and self.current_token()[0] != 'CURLY_BRACKET':
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        token = self.current_token()
        if token[0] == 'KEYWORD':
            if token[1] in ['int', 'float', 'char', 'string', 'double']:
                return self.parse_declaration()
            elif token[1] == 'if':
                return self.parse_conditional()
            elif token[1] == 'print':
                return self.parse_print_statement()
            elif token[1] in ['pass', 'noop']:
                return self.parse_pass()
            elif token[1] == 'return':
                return self.parse_return()
            elif token[1] in ['break', 'continue']:
                return self.parse_loop_control()
            elif token[1] == 'while':
                return self.parse_while()
            elif token[1] == 'for':
                return self.parse_for()
        elif token[0] == 'IDENTIFIER':
            return self.parse_assignment()
        raise SyntaxError(f"Unexpected token {token} in statement")

    def parse_declaration(self):
        keyword = self.match('KEYWORD')
        identifier = self.match('IDENTIFIER')
        if self.current_token()[0] == 'OPERATOR' and self.current_token()[1] == '=':
            self.match('OPERATOR')
            value = self.parse_expression()
            self.match('SEMICOLON')
            return ParseNode("Declaration", [keyword, identifier, value])
        else:
            self.match('SEMICOLON')
            return ParseNode("Declaration", [keyword, identifier])

    def parse_assignment(self):
        identifier = self.match('IDENTIFIER')
        if self.current_token()[0] == 'COMPOUND_OPERATOR':
            operator = self.match('COMPOUND_OPERATOR')
        else:
            operator = self.match('OPERATOR')  # '='
        expression = self.parse_expression()
        self.match('SEMICOLON')
        return ParseNode("Assignment", [identifier, operator, expression])

    def parse_conditional(self):
        self.match('KEYWORD')  # 'if'
        self.match('PAREN')
        condition = self.parse_boolean_expression()
        self.match('PAREN')
        self.match('CURLY_BRACKET')
        if_body = self.parse_statement_list()
        self.match('CURLY_BRACKET')
        elif_statements = []
        while self.current_token() and self.current_token()[1] == 'elif':
            self.match('KEYWORD')  # 'elif'
            self.match('PAREN')
            elif_condition = self.parse_boolean_expression()
            self.match('PAREN')
            self.match('CURLY_BRACKET')
            elif_body = self.parse_statement_list()
            self.match('CURLY_BRACKET')
            elif_statements.append((elif_condition, elif_body))
        else_body = None
        if self.current_token() and self.current_token()[1] == 'else':
            self.match('KEYWORD')  # 'else'
            self.match('CURLY_BRACKET')
            else_body = self.parse_statement_list()
            self.match('CURLY_BRACKET')
        return ParseNode("Conditional", [condition, if_body, elif_statements, else_body])

    def parse_boolean_expression(self):
        expr = self.parse_expression()
        if self.current_token()[0] == 'COMPARISON_OPERATOR':
            operator = self.match('COMPARISON_OPERATOR')
            right = self.parse_expression()
            expr = ParseNode("BooleanExpression", [expr, operator, right])
        while self.current_token() and self.current_token()[1] in ['and', 'or']:
            logical_op = self.match('KEYWORD')
            right = self.parse_boolean_expression()
            expr = ParseNode("LogicalExpression", [expr, logical_op, right])
        return expr

    def parse_print_statement(self):
        self.match('KEYWORD')  # 'print'
        self.match('PAREN')
        if self.current_token()[0] == 'IDENTIFIER':
            content = self.match('IDENTIFIER')
        elif self.current_token()[0] == 'STRING':
            content = self.match('STRING')
        else:
            raise SyntaxError("Expected IDENTIFIER or STRING in print statement")
        self.match('PAREN')
        self.match('SEMICOLON')
        return ParseNode("PrintStatement", [content])

    def parse_while(self):
        self.match('KEYWORD')  # 'while'
        self.match('PAREN')
        condition = self.parse_boolean_expression()
        self.match('PAREN')
        self.match('CURLY_BRACKET')
        body = self.parse_statement_list()
        self.match('CURLY_BRACKET')
        return ParseNode("WhileLoop", [condition, body])

    def parse_for(self):
        self.match('KEYWORD')  # 'for'
        identifier = self.match('IDENTIFIER')
        self.match('KEYWORD')  # 'in'
        target_list = self.parse_expression()
        self.match('CURLY_BRACKET')
        body = self.parse_statement_list()
        self.match('CURLY_BRACKET')
        return ParseNode("ForLoop", [identifier, target_list, body])

    def parse_pass(self):
        keyword = self.match('KEYWORD')  # 'pass' or 'noop'
        self.match('SEMICOLON')
        return ParseNode("Pass", [keyword])

    def parse_return(self):
        self.match('KEYWORD')  # 'return'
        if self.current_token()[0] != 'SEMICOLON':
            expr_list = self.parse_expression()
        else:
            expr_list = None
        self.match('SEMICOLON')
        return ParseNode("Return", [expr_list])

    def parse_loop_control(self):
        keyword = self.match('KEYWORD')  # 'break' or 'continue'
        self.match('SEMICOLON')
        return ParseNode("LoopControl", [keyword])

    def parse_expression(self):
        term = self.parse_term()
        while self.current_token() and self.current_token()[0] in ['OPERATOR', 'COMPARISON_OPERATOR']:
            operator = self.match(self.current_token()[0])
            right = self.parse_term()
            term = ParseNode("BinaryExpression", [term, operator, right])
        return term

    def parse_term(self):
        if self.current_token()[0] == 'IDENTIFIER':
            return ParseNode("Identifier", [self.match('IDENTIFIER')])
        elif self.current_token()[0] in ['NUMBER', 'FLOAT']:
            return ParseNode("Number", [self.match(self.current_token()[0])])
        elif self.current_token()[0] == 'STRING':
            return ParseNode("String", [self.match('STRING')])
        elif self.current_token()[0] == 'PAREN' and self.current_token()[1] == '(':
            self.match('PAREN')
            expr = self.parse_expression()
            self.match('PAREN')
            return expr
        elif self.current_token()[0] == 'SQUARE_BRACKET' and self.current_token()[1] == '[':
            return self.parse_list()
        raise SyntaxError(f"Unexpected token {self.current_token()} in term")

    def parse_list(self):
        self.match('SQUARE_BRACKET')  # '['
        elements = []
        if self.current_token()[0] != 'SQUARE_BRACKET':
            elements.append(self.parse_expression())
            while self.current_token()[0] == 'COMMA':
                self.match('COMMA')
                elements.append(self.parse_expression())
        self.match('SQUARE_BRACKET')  # ']'
        return ParseNode("List", elements)

class ParseNode:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []

    def pretty_print(self, prefix="", is_last=True):
        result = prefix + ("└── " if is_last else "├── ") + self.name + "\n"
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            if isinstance(child, ParseNode):
                result += child.pretty_print(new_prefix, is_last=(i == len(self.children) - 1))
            else:
                result += new_prefix + ("└── " if i == len(self.children) - 1 else "├── ") + str(child) + "\n"
        return result

    def __str__(self):
        return self.pretty_print()

# Example usage
if __name__ == "__main__":
    # Assuming you have already run your tokenizer and have the tokens
    # Replace this with your actual tokens from the tokenizer

    parser = Parser(tokens)
    try:
        parse_tree = parser.parse()
        print("Parse Tree:")
        print(parse_tree)
    except SyntaxError as e:
        print(f"Syntax Error: {e}")