import enum
from typing import Optional


class TokenType(enum.Enum):
    NUMBER = 1
    STRING = 2
    IDENTIFIER = 3

    EQUALS = 10
    PLUS = 11
    MINUS = 12
    MULTIPLY = 13
    DIVIDE = 14
    BANG = 15
    MODULO = 16

    LPARENT = 20
    RPARENT = 21
    REL_LT = 22
    REL_LTEQ = 23
    REL_NOTEQ = 24
    REL_EQ = 24
    REL_GTEQ = 25
    REL_GT = 26

    BLOCK_IF = 30
    BLOCK_THEN = 31
    BLOCK_ELSE = 32
    BLOCK_ELSEIF = 33
    BLOCK_ENDIF = 34

    LET = 40
    LSQBRACKET = 41
    RSQBRACKET = 42
    COMMA = 43
    CONST = 44

    LOOP_REPEAT = 50
    LOOP_FOREVER = 51
    LOOP_BREAK = 52
    LOOP_UNTIL = 53

    LOG_NOT = 60
    LOG_AND = 61
    LOG_OR = 62

    # Procedures
    PROC_SUB = 200
    PROC_ENDSUB = 201
    PROC_RETURN = 202

    # Functions
    PROC_FUNC = 210
    PROC_ENDFUNC = 211

    # External / C-API
    API_EXTERN = 400

    IMPORT = 600

    EOF = 999


class Token(object):
    def __init__(self, ttype: TokenType, cn: int, value=None):
        self.ttype = ttype
        self.value = value
        self.meta_cn = cn  # Character number (for better error printing)

    def __str__(self):
        return 'Token of type {t} with value {v}'.format(t=self.ttype, v=self.value)

    def __repr__(self):
        return self.__str__()


class ScanWrongTokenException(Exception):
    pass


class Scanner:
    """
    Tokenizer
    """

    def __init__(self):
        self._str_stream: str = ''
        self._char_offset: int = 0
        self._cur_char: str = ''
        self._str_len: int = 0
        self._opening_str: bool = False

    def scan_str(self, input_str: str) -> None:
        """
        Tokenize given input stream of type str
        :param input_str: Stream
        """
        self._str_stream = input_str
        self._str_len = len(self._str_stream)
        self._char_offset = 0
        self._cur_char = self._str_stream[self._char_offset]

    def next_token(self, peek: bool = False) -> Optional[Token]:
        """
        Get next available token
        :return: Token instance
        """
        while self._cur_char is not None:
            if self._cur_char.isspace():
                self._skip_whitespace()
                if self._cur_char is None:
                    return

            if self._cur_char == '(':
                self._advance(peek)
                return Token(TokenType.LPARENT, cn=self._char_offset)

            if self._cur_char == ')':
                self._advance(peek)
                return Token(TokenType.RPARENT, cn=self._char_offset)

            if self._cur_char == '#':
                while self._cur_char not in [None, '\n']:
                    self._advance(peek)
                self._advance()
                continue

            if self._cur_char == '+':
                self._advance(peek)
                return Token(TokenType.PLUS, cn=self._char_offset)

            if self._cur_char == '-':
                self._advance(peek)
                return Token(TokenType.MINUS, cn=self._char_offset)

            if self._cur_char == '/':
                self._advance(peek)
                return Token(TokenType.DIVIDE, cn=self._char_offset)

            if self._cur_char == '*':
                self._advance(peek)
                return Token(TokenType.MULTIPLY, cn=self._char_offset)

            if self._cur_char == '%':
                self._advance(peek)
                return Token(TokenType.MODULO, cn=self._char_offset)

            if self._cur_char == '=':
                self._advance(peek)
                return Token(TokenType.EQUALS, cn=self._char_offset)

            if self._cur_char == '!':
                self._advance(peek)
                return Token(TokenType.BANG, cn=self._char_offset)

            if self._cur_char == '[':
                self._advance(peek)
                return Token(TokenType.LSQBRACKET, cn=self._char_offset)

            if self._cur_char == ']':
                self._advance(peek)
                return Token(TokenType.RSQBRACKET, cn=self._char_offset)

            if self._cur_char == ',':
                self._advance(peek)
                return Token(TokenType.COMMA, cn=self._char_offset)

            if self._cur_char == '<':
                self._advance(peek)
                if self._peek() == '=':
                    self._advance(peek)
                    return Token(TokenType.REL_LTEQ, cn=self._char_offset)
                elif self._peek() == '>':
                    self._advance(peek)
                    return Token(TokenType.REL_NOTEQ, cn=self._char_offset)
                else:
                    return Token(TokenType.REL_LT, cn=self._char_offset)

            if self._cur_char == '>':
                self._advance(peek)
                if self._peek() == '=':
                    self._advance(peek)
                    return Token(TokenType.REL_GTEQ, cn=self._char_offset)
                else:
                    return Token(TokenType.REL_GT, cn=self._char_offset)

            if self._cur_char.isdigit() or self._cur_char == '.':
                return Token(TokenType.NUMBER, cn=self._char_offset, value=self._scan_number())

            if self._cur_char == '\"':
                if self._opening_str:
                    raise ScanWrongTokenException('Missing closing quotes')
                return Token(TokenType.STRING, cn=self._char_offset, value=self._scan_string())

            if self._cur_char.isalpha() or self._cur_char == '_':
                return self._scan_identifier_or_keyword()

            raise ScanWrongTokenException('Wrong character {c} at {o}'.format(c=self._cur_char, o=self._char_offset))

    def _advance(self, peek: bool = False) -> None:
        if peek:
            return
        if self._char_offset + 1 < self._str_len:
            self._char_offset += 1
            self._cur_char = self._str_stream[self._char_offset]
        else:
            self._scan_complete()

    def _peek(self) -> Optional[str]:
        if self._char_offset < self._str_len:
            return self._str_stream[self._char_offset]
        else:
            return None

    def _scan_complete(self) -> None:
        self._cur_char = None

    def _skip_whitespace(self) -> None:
        while self._cur_char is not None and self._cur_char.isspace():
            self._advance()

    def _scan_number(self) -> float:
        tmp_num = ''
        scan_float = False
        while self._cur_char is not None and (self._cur_char.isdigit() or self._cur_char == '.'):
            if self._cur_char == '.':
                # Leading dot without digit (.3)
                if not scan_float:
                    scan_float = True
                else:
                    raise ScanWrongTokenException()

            tmp_num += self._cur_char
            self._advance()
        return float(tmp_num)

    def _scan_string(self) -> str:
        self._opening_str = True
        tmp_str = ''
        self._advance()
        while self._cur_char is not None and self._cur_char != '\"':
            tmp_str += self._cur_char
            self._advance()

        if self._cur_char == '\"':
            self._advance()
            self._opening_str = False
            return tmp_str
        else:
            raise ScanWrongTokenException()

    def _scan_identifier_or_keyword(self) -> Token:
        off = 0
        tmp_str = ''
        while self._cur_char is not None and (
                self._cur_char.isalpha() or self._cur_char.isdigit() or self._cur_char == '_'):
            if self._cur_char.isdigit() and off == 0:
                raise ScanWrongTokenException('Identifiers must not start with a digit')
            tmp_str += self._cur_char
            self._advance()
            off += 1

        slen = len(tmp_str)
        if slen == 2:
            if tmp_str == 'if':
                return Token(TokenType.BLOCK_IF, cn=self._char_offset)
            elif tmp_str == 'or':
                return Token(TokenType.LOG_OR, cn=self._char_offset)
        elif slen == 3:
            if tmp_str == 'let':
                return Token(TokenType.LET, cn=self._char_offset)
            elif tmp_str == 'and':
                return Token(TokenType.LOG_AND, cn=self._char_offset)
            elif tmp_str == 'mod':
                return Token(TokenType.MODULO, cn=self._char_offset)
            elif tmp_str == 'sub':
                return Token(TokenType.PROC_SUB, cn=self._char_offset)
        elif slen == 4:
            if tmp_str == 'then':
                return Token(TokenType.BLOCK_THEN, cn=self._char_offset)
            elif tmp_str == 'else':
                return Token(TokenType.BLOCK_ELSE, cn=self._char_offset)
            elif tmp_str == 'exit':
                return Token(TokenType.LOOP_BREAK, cn=self._char_offset)
            elif tmp_str == 'func':
                return Token(TokenType.PROC_FUNC, cn=self._char_offset)
        elif slen == 5:
            if tmp_str == 'endif':
                return Token(TokenType.BLOCK_ENDIF, cn=self._char_offset)
            elif tmp_str == 'until':
                return Token(TokenType.LOOP_UNTIL, cn=self._char_offset)
            elif tmp_str == 'const':
                return Token(TokenType.CONST, cn=self._char_offset)
        elif slen == 6:
            if tmp_str == 'repeat':
                return Token(TokenType.LOOP_REPEAT, cn=self._char_offset)
            elif tmp_str == 'elseif':
                return Token(TokenType.BLOCK_ELSEIF, cn=self._char_offset)
            elif tmp_str == 'endsub':
                return Token(TokenType.PROC_ENDSUB, cn=self._char_offset)
            elif tmp_str == 'return':
                return Token(TokenType.PROC_RETURN, cn=self._char_offset)
            elif tmp_str == 'extern':
                return Token(TokenType.API_EXTERN, cn=self._char_offset)
            elif tmp_str == 'import':
                return Token(TokenType.IMPORT, cn=self._char_offset)
        elif slen == 7:
            if tmp_str == 'forever':
                return Token(TokenType.LOOP_FOREVER, cn=self._char_offset)
            elif tmp_str == 'endfunc':
                return Token(TokenType.PROC_ENDFUNC, cn=self._char_offset)

        return Token(TokenType.IDENTIFIER, cn=self._char_offset, value=tmp_str)

    @property
    def char_offset(self):
        return self._char_offset
