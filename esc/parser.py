import abc
import enum
from typing import Union, Type

from esc.scanner import Scanner, TokenType, Token


class ValueType(enum.Enum):
    NUMBER = 1
    STRING = 2


class OpType(enum.Enum):
    NONE = 0
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4


class Node(abc.ABC):
    pass


class Binary(Node):
    def __init__(self):
        super().__init__()
        self.left: Node = None
        self.right: Node = None


class Unary(Node):
    def __init__(self):
        super().__init__()
        self.value = None


class StatementNode(Binary):
    pass


class ExpressionNode(Binary):
    pass


class AssignmentNode(Binary):
    pass


class TermNode(Binary):
    def __init__(self):
        super().__init__()
        self.op = OpType.NONE


class SubexprNode(Binary):
    pass


class ValueNode(Unary):
    def __init__(self, value_type: ValueType):
        super().__init__()
        self.value_type = value_type


class ParseSyntaxException(Exception):
    pass


class Parser:
    def __init__(self):
        self._scanner = Scanner()
        self._scanner.scan_str('let a = (3*4)+(18/9)')
        self._cur_token: Token = self._scanner.next_token()
        self._statements: [StatementNode] = []

    def parse(self):
        return self._parse_statements()

    def _accept(self, ttype: TokenType):
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

    def _parse_statements(self):
        t: TokenType = self._cur_token.ttype

        if t == TokenType.LET:
            self._statements.append(self._parse_assignment())

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

    def _parse_andexpr(self):
        node = ExpressionNode()
        node_tmp = self._parse_notexpr()

        t = self._cur_token_type()
        while t == TokenType.LOG_AND:
            self._accept(TokenType.LOG_AND)
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
        while t in [TokenType.REL_EQ, TokenType.REL_NOTEQ, TokenType.REL_GT, TokenType.REL_GTEQ, TokenType.REL_LT, TokenType.REL_LTEQ]:
            self._accept(t)
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

