class LexicalError(Exception):
    pass


class ParsingError(Exception):
    pass


class TokenType:
    INTEGER = "INTEGER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"

TOKEN_MAP = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MUL,
    "/": TokenType.DIV,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
}


class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return f"Token({self.type}, {repr(self.value)})"


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[0] if self.text else None

    def advance(self):
        self.pos += 1

        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_whitespace(self):
        while (
            self.current_char is not None
            and self.current_char.isspace()
        ):
            self.advance()

    def integer(self):
        result = ""

        while (
            self.current_char is not None
            and self.current_char.isdigit()
        ):
            result += self.current_char
            self.advance()

        return int(result)

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(
                    TokenType.INTEGER,
                    self.integer()
                )

            if self.current_char in TOKEN_MAP:
                char = self.current_char
                self.advance()
                return Token(
                    TOKEN_MAP[char],
                    char
                )

            raise LexicalError(
                "Помилка лексичного аналізу"
            )

        return Token(TokenType.EOF, None)


class AST:
    pass


class BinOp(AST):
    def __init__(
        self,
        left,
        op,
        right
    ):
        self.left = left
        self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value


class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = (
            self.lexer.get_next_token()
        )

    def error(self):
        raise ParsingError(
            "Помилка синтаксичного аналізу"
        )

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = (
                self.lexer.get_next_token()
            )
        else:
            self.error()

    def factor(self):
        token = self.current_token

        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Num(token)

        if token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)

            node = self.expr()

            self.eat(TokenType.RPAREN)

            return node

        self.error()

    def term(self):
        node = self.factor()

        while self.current_token.type in (
            TokenType.MUL,
            TokenType.DIV
        ):
            token = self.current_token

            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            else:
                self.eat(TokenType.DIV)

            node = BinOp(
                left=node,
                op=token,
                right=self.factor()
            )

        return node

    def expr(self):
        node = self.term()

        while self.current_token.type in (
            TokenType.PLUS,
            TokenType.MINUS
        ):
            token = self.current_token

            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            else:
                self.eat(TokenType.MINUS)

            node = BinOp(
                left=node,
                op=token,
                right=self.term()
            )

        return node


class Interpreter:
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        if node.op.type == TokenType.PLUS:
            return (
                self.visit(node.left)
                + self.visit(node.right)
            )

        if node.op.type == TokenType.MINUS:
            return (
                self.visit(node.left)
                - self.visit(node.right)
            )

        if node.op.type == TokenType.MUL:
            return (
                self.visit(node.left)
                * self.visit(node.right)
            )

        if node.op.type == TokenType.DIV:
            return (
                self.visit(node.left)
                / self.visit(node.right)
            )

    def visit_Num(self, node):
        return node.value

    def interpret(self):
        tree = self.parser.expr()

        if (
            self.parser.current_token.type
            != TokenType.EOF
        ):
            self.parser.error()

        return self.visit(tree)

    def visit(self, node):
        method_name = (
            "visit_"
            + type(node).__name__
        )

        visitor = getattr(
            self,
            method_name,
            self.generic_visit
        )

        return visitor(node)

    def generic_visit(self, node):
        raise Exception(
            f"Немає методу "
            f"visit_{type(node).__name__}"
        )


def calculate(expression):
    lexer = Lexer(expression)
    parser = Parser(lexer)
    interpreter = Interpreter(parser)

    return interpreter.interpret()


def run_test(
    expression,
    expected
):
    try:
        result = calculate(expression)

        status = (
            "УСПІШНО"
            if result == expected
            else "ПОМИЛКА"
        )

        print(
            f"Вираз: {expression}"
        )
        print(
            f"Очікуваний результат: "
            f"{expected}"
        )
        print(
            f"Отриманий результат: "
            f"{result}"
        )
        print(
            f"Статус: {status}"
        )
        print()

    except Exception as error:
        print(
            f"Вираз: {expression}"
        )
        print(
            f"Помилка: {error}"
        )
        print(
            "Статус: ПОМИЛКА"
        )
        print()


def run_tests():
    run_test(
        "(2 + 3) * 4",
        20
    )

    run_test(
        "2 + 3 * 4",
        14
    )

    run_test(
        "(2 + 3) * (4 - 1)",
        15
    )

    run_test(
        "20 / 4",
        5
    )

    run_test(
        "10 - 2 * 3",
        4
    )

    run_test(
        "100 / (5 * 4)",
        5
    )

    run_test(
        "2 * (3 + (4 * 5))",
        46
    )


def main():
    run_tests()

    while True:
        try:
            text = input(
                'Введіть вираз '
                '(або "exit" для виходу): '
            )

            if text.lower() == "exit":
                print(
                    "Вихід із програми."
                )
                break

            result = calculate(text)

            print(
                f"Результат: {result}"
            )

        except Exception as error:
            print(
                f"Помилка: {error}"
            )


if __name__ == "__main__":
    main()