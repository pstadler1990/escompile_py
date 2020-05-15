import abc
import enum
from typing import Union
from esc.scanner import Scanner, TokenType, Token


class ValueType(enum.Enum):
    NUMBER = 1
    STRING = 2
    IDENTIFIER = 3


class OpType(enum.Enum):
    NONE = 0
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4

    EQUALS = 10
    AND = 11


class Node(abc.ABC):
    pass


class Binary(Node):
    def __init__(self):
        super().__init__()
        self.left = None
        self.right = None


class Unary(Node):
    def __init__(self):
        super().__init__()
        self.value = None


class StatementNode(Binary):
    pass


class ExpressionNode(Binary):
    def __init__(self):
        super().__init__()
        self.op = OpType.NONE


class AssignmentNode(Binary):
    pass


class IfNode(Binary):
    pass


class TermNode(Binary):
    def __init__(self):
        super().__init__()
        self.op = OpType.NONE


class ValueNode(Unary):
    def __init__(self, value_type: ValueType):
        super().__init__()
        self.value_type = value_type


class ParseSyntaxException(Exception):
    pass


class Parser:
    def __init__(self):
        self._scanner = Scanner()
        self._cur_token = None
        self._statements: [StatementNode] = []

    def parse(self, input_str: str) -> [StatementNode]:
        self._scanner.scan_str(input_str)
        self._cur_token: Token = self._scanner.next_token()
        self._statements: [StatementNode] = []
        return self._parse_statements()

    def _accept(self, ttype: TokenType):
        if self._cur_token is not None:
            if self._cur_token.ttype == ttype:
                self._cur_token = self._scanner.next_token()
            else:
                self._fail()

    def _fail(self, msg: str = ''):
        raise ParseSyntaxException(msg)

    def _cur_token_type(self):
        if self._cur_token is not None:
            return self._cur_token.ttype
        else:
            return TokenType.EOF

    def _parse_statements(self) -> [StatementNode]:
        statements = []
        t: TokenType = self._cur_token.ttype

        while t in [TokenType.LET, TokenType.BLOCK_IF]:
            if t == TokenType.LET:
                statements.append(self._parse_assignment())
            elif t == TokenType.BLOCK_IF:
                statements.append(self._parse_if())

            if self._cur_token is not None:
                t = self._cur_token.ttype
            else:
                break
        return statements

    def _parse_expressions(self):
        pass

    def _parse_assignment(self) -> AssignmentNode:
        node = AssignmentNode()
        self._accept(TokenType.LET)
        node.left = self._cur_token
        self._accept(TokenType.IDENTIFIER)
        self._accept(TokenType.EQUALS)
        node.right = self._parse_expression()
        return node

    def _parse_if(self) -> IfNode:
        # if <expr> then <statement(s)>
        # | if <expr> then
        #     <statement(s)>
        #   endif
        node = IfNode()
        self._accept(TokenType.BLOCK_IF)
        node.left = self._parse_expression()
        self._accept(TokenType.BLOCK_THEN)
        node.right = self._parse_statements()
        self._accept(TokenType.BLOCK_ENDIF)
        # TODO: Else / Elseif
        return node

    def _parse_expression(self) -> ExpressionNode:
        node = ExpressionNode()
        node_tmp = self._parse_andexpr()

        t = self._cur_token_type()
        while t == TokenType.LOG_OR:
            self._accept(TokenType.LOG_OR)
            node.left = node_tmp
            node.right = self._parse_expression()
            return node
        return node_tmp

    def _parse_andexpr(self) -> ExpressionNode:
        node = ExpressionNode()
        node_tmp: ExpressionNode = self._parse_notexpr()

        t = self._cur_token_type()
        while t == TokenType.LOG_AND:
            self._accept(TokenType.LOG_AND)
            node.op = OpType.AND
            node.left = node_tmp
            node.right = self._parse_andexpr()
            return node
        return node_tmp

    def _parse_notexpr(self):
        node = ExpressionNode()
        node_tmp = self._parse_compareexpr()

        t = self._cur_token_type()
        while t == TokenType.LOG_NOT:
            self._accept(TokenType.LOG_NOT)
            node.left = node_tmp
            node.right = self._parse_compareexpr()
            return node
        return node_tmp

    def _parse_compareexpr(self) -> Union[ExpressionNode, TermNode]:
        node = ExpressionNode()
        node_tmp = self._parse_addexpr()

        t = self._cur_token_type()
        # TODO: REL_EQ (==) replaced with EQUALS (=) to keep it standard BASIC
        while t in [TokenType.EQUALS, TokenType.REL_NOTEQ, TokenType.REL_GT, TokenType.REL_GTEQ, TokenType.REL_LT, TokenType.REL_LTEQ]:
            self._accept(t)
            # node.op = t
            if t == TokenType.EQUALS:
                node.op = OpType.EQUALS
            # TODO: Add other types
            node.left = node_tmp
            node.right = self._parse_compareexpr()
            return node
        return node_tmp

    def _parse_addexpr(self) -> Union[TermNode, ExpressionNode, ValueNode]:
        node = TermNode()
        node_tmp = self._parse_multexpr()

        t = self._cur_token_type()
        while t == TokenType.PLUS or t == TokenType.MINUS:
            self._accept(t)
            if t == TokenType.PLUS:
                node.op = OpType.ADD
            else:
                node.op = OpType.SUB
            node.left = node_tmp
            node.right = self._parse_addexpr()
            return node
        return node_tmp

    def _parse_multexpr(self) -> Union[TermNode, ExpressionNode, ValueNode]:
        node = TermNode()
        node_tmp = self._parse_negateexpr()

        t = self._cur_token_type()
        while t == TokenType.MULTIPLY or t == TokenType.DIVIDE:
            self._accept(t)
            if t == TokenType.MULTIPLY:
                node.op = OpType.MUL
            else:
                node.op = OpType.DIV
            node.left = node_tmp
            node.right = self._parse_multexpr()
            return node
        return node_tmp

    def _parse_negateexpr(self):
        node = ExpressionNode()

        t = self._cur_token_type()
        if t in [TokenType.MINUS, TokenType.BANG]:
            node.left = t
            self._accept(t)
            node.right = self._parse_subexpr()
        else:
            node = self._parse_subexpr()
        return node

    def _parse_subexpr(self) -> Union[ExpressionNode, ValueNode]:
        t = self._cur_token_type()
        if t == TokenType.LPARENT:
            self._accept(TokenType.LPARENT)
            node = self._parse_expression()
            self._accept(TokenType.RPARENT)
            return node
        else:
            return self._parse_value()

    def _parse_value(self) -> ValueNode:
        t = self._cur_token_type()
        if t == TokenType.NUMBER:
            node = ValueNode(ValueType.NUMBER)
            node.value = self._cur_token.value
            self._accept(TokenType.NUMBER)
            return node
        elif t == TokenType.STRING:
            node = ValueNode(ValueType.STRING)
            node.value = str(self._cur_token.value)
            self._accept(TokenType.STRING)
            return node
        elif t == TokenType.IDENTIFIER:
            node = ValueNode(ValueType.IDENTIFIER)
            node.value = self._cur_token.value
            self._accept(TokenType.IDENTIFIER)
            return node
        else:
            self._fail('Invalid value for token')
