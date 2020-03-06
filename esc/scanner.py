import enum


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

    LOOP_REPEAT = 50
    LOOP_FOREVER = 51
    LOOP_BREAK = 52

    LOG_NOT = 60
    LOG_AND = 61
    LOG_OR = 62

    EOF = 999


class Token(object):
    def __init__(self, ttype: TokenType, value=None):
        self.ttype = ttype
        self.value = value

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

    def next_token(self) -> Token:
        """
        Get next available token
        :return: Token instance
        """
        while self._cur_char is not None:
            if self._cur_char.isspace():
                self._skip_whitespace()

            if self._cur_char == '(':
                self._advance()
                return Token(TokenType.LPARENT)

            if self._cur_char == ')':
                self._advance()
                return Token(TokenType.RPARENT)

            if self._cur_char == '+':
                self._advance()
                return Token(TokenType.PLUS)

            if self._cur_char == '-':
                self._advance()
                return Token(TokenType.MINUS)

            if self._cur_char == '/':
                self._advance()
                return Token(TokenType.DIVIDE)

            if self._cur_char == '*':
                self._advance()
                return Token(TokenType.MULTIPLY)

            if self._cur_char == '=':
                self._advance()
                # TODO: Peek next char to be another =  -> results in == (comparison operator)
                return Token(TokenType.EQUALS)

            if self._cur_char.isdigit() or self._cur_char == '.':
                return Token(TokenType.NUMBER, self._scan_number())

            if self._cur_char == '\"':
                if self._opening_str:
                    raise ScanWrongTokenException('Missing closing quotes')
                return Token(TokenType.STRING, self._scan_string())

            if self._cur_char.isalpha() or self._cur_char == '_':
                return self._scan_identifier_or_keyword()

            raise ScanWrongTokenException('Wrong character {c} at {o}'.format(c=self._cur_char, o=self._char_offset))

    def _advance(self) -> None:
        if self._char_offset + 1 < self._str_len:
            self._char_offset += 1
            self._cur_char = self._str_stream[self._char_offset]
        else:
            self._scan_complete()

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
        while self._cur_char is not None and (self._cur_char.isalpha() or self._cur_char.isdigit() or self._cur_char == '_'):
            if self._cur_char.isdigit() and off == 0:
                raise ScanWrongTokenException('Identifiers must not start with a digit')
            tmp_str += self._cur_char
            self._advance()
            off += 1

        slen = len(tmp_str)
        if slen == 2:
            if tmp_str == 'if':
                return Token(TokenType.BLOCK_IF)
        elif slen == 3:
            if tmp_str == 'let':
                return Token(TokenType.LET)
        elif slen == 4:
            if tmp_str == 'then':
                return Token(TokenType.BLOCK_THEN)
            elif tmp_str == 'else':
                return Token(TokenType.BLOCK_ELSE)
        elif slen == 5:
            if tmp_str == 'endif':
                return Token(TokenType.BLOCK_ENDIF)
            elif tmp_str == 'break':
                return Token(TokenType.LOOP_BREAK)
        elif slen == 6:
            if tmp_str == 'repeat':
                return Token(TokenType.LOOP_REPEAT)
            elif tmp_str == 'elseif':
                return Token(TokenType.BLOCK_ELSEIF)
        elif slen == 7:
            if tmp_str == 'forever':
                return Token(TokenType.LOOP_FOREVER)

        return Token(TokenType.IDENTIFIER, tmp_str)
