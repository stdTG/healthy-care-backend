import ply.lex as lex
import ply.yacc as yacc


class FormulaParserError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class FormulaCompileError(FormulaParserError):
    def __init__(self, message: str):
        super().__init__(message)


class Parser:
    """
    Base class for a lexer/parser that has the rules defined as methods
    """
    tokens = ()
    precedence = ()

    def __init__(self, **kwargs):
        self.debug = kwargs.get("debug", False)
        self.lookup_variables = kwargs.get("lookup_variables", {})
        self.result = None

        # Build the lexer and parser
        lex.lex(module=self, debug=self.debug)
        yacc.yacc(module=self,
                  debug=self.debug, )

    def run(self, formula: str):
        yacc.parse(formula)


class Calc(Parser):
    tokens = (
        "VAR", "NUMBER",
        "PLUS", "MINUS", "EXP", "TIMES", "DIVIDE",
        "LPAREN", "RPAREN",
    )

    # Tokens

    t_PLUS = r"\+"
    t_MINUS = r"-"
    t_EXP = r"\*\*"
    t_TIMES = r"\*"
    t_DIVIDE = r"/"
    t_LPAREN = r"\("
    t_RPAREN = r"\)"

    t_ignore = " \t"
    t_ignore_COMMENT = r"\#.*"

    # Parsing rules

    precedence = (
        ("left", "PLUS", "MINUS"),
        ("left", "TIMES", "DIVIDE"),
        ("left", "EXP"),
        ("right", "UMINUS"),
    )

    def t_NUMBER(self, t):
        r"\d+"
        try:
            t.value = int(t.value)
        except ValueError as e:
            raise FormulaParserError(message="Integer value too large %s" % t.value) from e

        return t

    def symbol_lookup(self, var_name: str) -> int:
        try:
            return self.lookup_variables[var_name.lower()]
        except KeyError as e:
            raise FormulaCompileError(
                message="Formula is not valid, '%s' is not found" % var_name) from e

    def t_VAR(self, t):
        r"[a-zA-Z_][a-zA-Z0-9_]*"

        # Look up symbol table information and return a tuple
        t.value = (t.value, self.symbol_lookup(t.value))
        return t

    def t_newline(self, t):
        r"\n+"

        t.lexer.lineno += t.value.count("\n")

    def t_error(self, t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)

    def p_statement_expr(self, p):
        """
        statement : expression
        """
        self.result = p[1]

    def p_expression_binop(self, p):
        """
        expression : expression PLUS expression
                  | expression MINUS expression
                  | expression TIMES expression
                  | expression DIVIDE expression
                  | expression EXP expression
        """
        if p[2] == "+":
            p[0] = p[1] + p[3]
        elif p[2] == "-":
            p[0] = p[1] - p[3]
        elif p[2] == "*":
            p[0] = p[1] * p[3]
        elif p[2] == "/":
            p[0] = p[1] / p[3]
        elif p[2] == "**":
            p[0] = p[1] ** p[3]

    def p_expression_uminus(self, p):
        """expression : MINUS expression %prec UMINUS"""
        p[0] = -p[2]

    def p_expression_group(self, p):
        """expression : LPAREN expression RPAREN"""
        p[0] = p[2]

    def p_expression_number(self, p):
        """expression : NUMBER"""
        p[0] = p[1]

    def p_expression_VAR(self, p):
        """expression : VAR"""
        try:
            p[0] = p[1][1]
        except LookupError as e:
            raise FormulaParserError(message="Undefined variable '%s'" % p[1]) from e

    def p_error(self, p):
        if p:
            raise FormulaParserError(message="Syntax error at '%s'" % p.value)
        else:
            raise FormulaParserError(message="Syntax error at EOF")


def calculate_formula_handler(formula: str, variables: dict):
    calc = Calc(lookup_variables=variables, debug=False, )
    calc.run(formula)

    return calc.result


if __name__ == "__main__":
    s = "8 * 2/var2"
    variables = {"var2": 2}

    calc = Calc(lookup_variables=variables, debug=True, )
    calc.run(s)
    print(calc.result)
