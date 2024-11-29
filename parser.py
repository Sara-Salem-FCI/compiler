from source_code_to_tokens_and_lexems import tokens


class Parser:
    def __init__(self, tokens):  # Fixed constructor name
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
        """Parse the program with the new grammar: begin { StatementList } end."""
        self.match('KEYWORD')  # 'begin'
        self.match('CURLY_BRACKET')    # '{'
        node = ParseNode("Program")

        # Parse StatementList inside {}
        while self.current_token() and not (self.current_token()[0] == 'CURLY_BRACKET' and self.current_token()[1] == '}'):
            node.children.append(self.parse_statement())

        self.match('CURLY_BRACKET')  # '}'
        self.match('KEYWORD')  # 'end'

        return node

    def parse_statement(self):
        token = self.current_token()
        
        if token[0] == 'KEYWORD':
            if token[1] == 'begin':
                self.match('KEYWORD')  # 'begin'
                block_node = self.parse_block()  # Parse the block inside 'begin'
                self.match('SEMICOLON')  # Match the semicolon at the end of the statement
                return block_node
            elif token[1] == 'end':
                self.match('KEYWORD')  # 'end'
                self.match('SEMICOLON')  # Match the semicolon at the end of the statement
                return ParseNode("EndStatement")
            elif token[1] == 'if':
                if_node = self.parse_if_statement()
                self.match('SEMICOLON')  # Match the semicolon at the end of the statement
                return if_node
            elif token[1] == 'print':
                print_node = self.parse_print_statement()
                self.match('SEMICOLON')  # Match the semicolon at the end of the statement
                return print_node
            elif token[1] == 'declare':
                declaration_node = self.parse_declaration()  # Handle declaration
                return declaration_node
        elif token[0] == 'IDENTIFIER':
            assignment_node = self.parse_assignment()
            self.match('SEMICOLON')  # Match the semicolon at the end of the statement
            return assignment_node
        else:
            raise SyntaxError(f"Unexpected token {token} in statement")


    def parse_declaration(self):
        token = self.current_token()
        
        if token[0] == 'KEYWORD' and token[1] == 'declare':
            self.match('KEYWORD')  # 'declare'
            identifier_token = self.current_token()
            
            if identifier_token[0] == 'IDENTIFIER':
                self.match('IDENTIFIER')  # Match the identifier
                self.match('SEMICOLON')   # Match the semicolon at the end of the declaration
                return ParseNode("Declaration", identifier_token[1])
            else:
                raise SyntaxError(f"Expected identifier after 'declare', found {identifier_token}")
        else:
            raise SyntaxError(f"Unexpected token {token} in declaration")


    def parse_print_statement(self):
        self.match('KEYWORD')  # 'print'
        self.match('PAREN')    # '('
        expr_node = self.parse_expression()
        self.match('PAREN')    # ')'
        return ParseNode("PrintStatement", [expr_node])

    def parse_if_statement(self):
        self.match('KEYWORD')  # Match 'if'
        condition = self.parse_expression()  # Parse the condition (which can include comparisons like '==')
        self.match('COLON')  # Match ':'
        body = self.parse_block()  # Parse the body
        node = ParseNode("IfStatement", [condition, body])

        # Optional 'else'
        if self.current_token() and self.current_token()[1] == 'else':
            self.match('KEYWORD')  # Match 'else'
            self.match('COLON')    # Match ':'
            else_body = self.parse_block()
            node.children.append(ParseNode("ElseStatement", [else_body]))

        return node

    def parse_while_statement(self):
        self.match('KEYWORD')  # 'while'
        condition = self.parse_expression()
        self.match('COLON')    # ':'
        body = self.parse_block()
        return ParseNode("WhileStatement", [condition, body])

    def parse_for_statement(self):
        self.match('KEYWORD')  # 'for'
        iterator = self.match('IDENTIFIER')  # e.g., variable in 'for x in range(...)'
        
        self.match('KEYWORD')  # 'in'
        
        # نضيف هنا التحقق من 'range' والتعامل معه كـ expression
        if self.current_token() and self.current_token()[1] == 'range':
            self.match('KEYWORD')  # 'range'
            self.match('PAREN')    # '('
            iterable = self.parse_expression()  # e.g., '5' in 'range(5)'
            self.match('PAREN')    # ')'
        else:
            iterable = self.parse_expression()  # other expressions, like a list or range
         
        self.match('COLON')    # ':' تأكد من وجود الكولون بعد التكرار
        body = self.parse_block()  # الجسم الذي سيقوم بالتكرار

        return ParseNode("ForStatement", [
            ParseNode(f"Iterator({iterator[1]})"),
            iterable,
            body
        ])

    def parse_block(self):
        """Parse a block of statements (e.g., indented after 'if', 'while')."""
        node = ParseNode("Block")
        while self.current_token() and self.current_token()[0] not in {'KEYWORD', 'IDENTIFIER'}:
            node.children.append(self.parse_statement())
        return node

    def parse_expression(self):
        node = self.parse_add_sub()
        while self.current_token() and self.current_token()[0] == 'COMPARISON_OPERATOR':
            operator = self.match('COMPARISON_OPERATOR')  # Match comparison operator (like ==, !=)
            right = self.parse_add_sub()
            node = ParseNode(f"BinaryOp({operator[1]})", [node, right])
        return node

    def parse_assignment(self):
        identifier = self.match('IDENTIFIER')
        self.match('OPERATOR')  # '='
        expr_node = self.parse_expression()
        return ParseNode("Assignment(=)", [
            ParseNode(f"Identifier({identifier[1]})"),
            expr_node
        ])

    def parse_add_sub(self):
        """Parse addition, subtraction, and compound assignments like += and -=."""
        node = self.parse_mul_div()

        # Handle compound operators like +=, -= first
        while self.current_token() and self.current_token()[0] == 'COMPOUND_OPERATOR':
            operator = self.match('COMPOUND_OPERATOR')  # مثل += أو -=
            left = node  # الجهة اليسرى من العملية المركبة (مثل x في x += 1)
            right = self.parse_mul_div()  # الجهة اليمنى (مثل 1)

            # نتحقق من نوع العملية المركبة ونعيد تشكيلها كعملية عادية.
            node = self.handle_compound_operator(left, operator[1], right)

        # Handle simple addition and subtraction operations
        while self.current_token() and self.current_token()[0] == 'OPERATOR' and self.current_token()[1] in '+-':
            operator = self.match('OPERATOR')
            right = self.parse_mul_div()
            node = ParseNode(f"BinaryOp({operator[1]})", [node, right])

        return node

    def parse_mul_div(self):
        """Parse multiplication, division, and compound assignments like *= and /=."""  
        node = self.parse_primary()

        # Handle multiplication and division operations
        while self.current_token() and self.current_token()[0] == 'OPERATOR' and self.current_token()[1] in '*/':
            operator = self.match('OPERATOR')
            right = self.parse_primary()
            node = ParseNode(f"BinaryOp({operator[1]})", [node, right])

        # Handle compound operators like *=, /= 
        while self.current_token() and self.current_token()[0] == 'COMPOUND_OPERATOR':
            operator = self.match('COMPOUND_OPERATOR')  # مثل *= أو /=
            left = node  # الجهة اليسرى من العملية المركبة (مثل x في x *= 2)
            right = self.parse_primary()  # الجهة اليمنى (مثل 2)
            
            # تحويل العمليات المركبة إلى عمليات عادية
            node = self.handle_compound_operator(left, operator[1], right)

        return node

    def handle_compound_operator(self, left, operator, right):
        """Helper function to handle compound operators and transform them into regular assignments."""
        if operator == '+=':
            return ParseNode(f"Assignment(=)", [
                ParseNode(f"Identifier({left.name})"),  # x
                ParseNode("BinaryOp(+)", [left, right])  # x + 1
            ])
        elif operator == '-=':
            return ParseNode(f"Assignment(=)", [
                ParseNode(f"Identifier({left.name})"),  # x
                ParseNode("BinaryOp(-)", [left, right])  # x - 1
            ])
        elif operator == '*=':
            return ParseNode(f"Assignment(=)", [
                ParseNode(f"Identifier({left.name})"),  # x
                ParseNode("BinaryOp(*)", [left, right])  # x * 1
            ])
        elif operator == '/=':
            return ParseNode(f"Assignment(=)", [
                ParseNode(f"Identifier({left.name})"),  # x
                ParseNode("BinaryOp(/)", [left, right])  # x / 1
            ])

    def parse_primary(self):
        """Parse primary expressions like numbers, identifiers, and parentheses."""
        token = self.current_token()
        if token[0] == 'NUMBER':
            self.advance()
            return ParseNode(f"Number({token[1]})")
        elif token[0] == 'IDENTIFIER':
            self.advance()
            return ParseNode(f"Identifier({token[1]})")
        elif token[0] == 'PAREN':
            self.match('PAREN')  # '('
            node = self.parse_expression()
            self.match('PAREN')  # ')'
            return node
        else:
            raise SyntaxError(f"Unexpected token {token} in primary expression")

class ParseNode:
    def __init__(self, name, children=None):
        self.name = name
        self.children = children or []

    def pretty_print(self, prefix="", is_last=True):
        result = prefix + ("└── " if is_last else "├── ") + self.name + "\n"
        new_prefix = prefix + ("    " if is_last else "│   ")
        for i, child in enumerate(self.children):
            result += child.pretty_print(new_prefix, is_last=(i == len(self.children) - 1))
        return result

    def __str__(self):
        """Override the __str__ method to print the parse tree."""
        return self.pretty_print()

# Example usage
if __name__ == "__main__":
    parser = Parser(tokens)
    try:
        parse_tree = parser.parse()
        print("Parse Tree:")
        print(parse_tree)  # سيتم الآن طباعة الشجرة التحليلية
    except SyntaxError as e:
        print("Parsing Error:", e)
