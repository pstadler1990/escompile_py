import abc
import enum
from typing import Union
from esc.scanner import Scanner, TokenType, Token


class ValueType(enum.Enum):
    NUMBER = 1
    STRING = 2
    IDENTIFIER = 3
    KEYWORD = 4
    ARRAYELEMENT = 5


class OpType(enum.Enum):
    NONE = 0
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    MOD = 5

    EQUALS = 10
    NOTEQUALS = 11
    AND = 12
    OR = 13
    LT = 14
    LTEQ = 15
    GT = 16
    GTEQ = 17


class ConditionPos(enum.Enum):
    TOP = 0
    BOTTOM = 1


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
    def __init__(self, modify: bool = False):
        super().__init__()
        self.modify = modify


class IfNode(Binary):
    def __init__(self):
        super().__init__()
        self.elsenode = None
        self.elseifnodes = []


class CallNode(Unary):
    def __init__(self):
        super().__init__()
        self.type = ''
        self.args = []


class ExitNode(Unary):
    def __init__(self):
        super().__init__()


class ArrayNode(Unary):
    def __init__(self):
        super().__init__()
        self.values = []


class ProcSubNode(Binary):
    def __init__(self):
        super().__init__()
        self.args = []


class ProcSubReturnNode(Unary):
    pass


class LoopNode(Binary):
    def __init__(self):
        super().__init__()
        self.condition_pos = ConditionPos.TOP


class TermNode(Binary):
    def __init__(self):
        super().__init__()
        self.op = OpType.NONE


class ValueNode(Unary):
    def __init__(self, value_type: ValueType):
        super().__init__()
        self.value_type = value_type
        self.identifier = None
        self.index = None


class ParseSyntaxException(Exception):
    pass


class Parser:
    def __init__(self):
        self._scanner = Scanner()
        self._cur_token = None
        self._prev_token = None
        self._statements: [StatementNode] = []
        self._loops = 0

    def _next_token(self, peek: bool = False):
        if self._cur_token is not None:
            self._prev_token = self._cur_token
        return self._scanner.next_token(peek)

    def parse(self, input_str: str) -> [StatementNode]:
        # Parse given input string
        # We perform some string cleaning and whitespace removing before actually passing the raw string to the scanner
        lines = list(filter(lambda e: len(e), [ln.lstrip() for ln in input_str.splitlines()]))
        for ln, _ in enumerate(lines):
            lines[ln] = ''.join(lines[ln])
        clean_str: str = '\n'.join(lines)

        self._scanner.scan_str(clean_str)
        self._cur_token: Token = self._next_token()
        self._statements: [StatementNode] = []
        return self._parse_statements()

    def _accept(self, ttype: TokenType):
        if self._cur_token is not None:
            if self._cur_token.ttype == ttype:
                self._cur_token = self._next_token()
            else:
                self._fail()

    def _fail(self, msg: str = ''):
        try:
            char_offset = self._cur_token.meta_cn
        except AttributeError:
            char_offset = self._scanner.char_offset
        raise ParseSyntaxException('PARSER ERROR,{msg},{cn}'.format(msg=msg, cn=char_offset))

    def _cur_token_type(self):
        if self._cur_token is not None:
            return self._cur_token.ttype
        else:
            return TokenType.EOF

    def _parse_statements(self) -> [StatementNode]:
        statements = []
        t: TokenType = self._cur_token.ttype

        while t in [TokenType.LET,
                    TokenType.BLOCK_IF,
                    TokenType.LOOP_REPEAT,
                    TokenType.IDENTIFIER,
                    TokenType.LOOP_BREAK,
                    TokenType.PROC_SUB,
                    TokenType.PROC_RETURN]:
            if t == TokenType.LET:
                statements.append(self._parse_assignment())
            elif t == TokenType.BLOCK_IF:
                statements.append(self._parse_if())
            elif t == TokenType.LOOP_REPEAT:
                statements.append(self._parse_loop())
            elif t == TokenType.LOOP_BREAK:
                statements.append(self._parse_exit())
            elif t == TokenType.IDENTIFIER:
                if self._next_token(peek=True).ttype == TokenType.LPARENT:
                    statements.append(self._parse_call())
                else:
                    statements.append(self._parse_lmodify())
            elif t == TokenType.PROC_SUB:
                statements.append(self._parse_sub())
            elif t == TokenType.PROC_RETURN:
                statements.append(self._parse_subreturn())

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

        if self._cur_token.ttype == TokenType.LSQBRACKET:
            # let my_var = [1, 2, 3]
            node.right = self._parse_array()
        else:
            # let my_var = (3 + 42)
            node.right = self._parse_expression()

        return node

    def _parse_lmodify(self) -> AssignmentNode:
        node = AssignmentNode(modify=True)
        node.left = self._parse_value()
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

        t = self._cur_token_type()
        while t == TokenType.BLOCK_ELSEIF:
            self._accept(TokenType.BLOCK_ELSEIF)
            n = IfNode()
            n.left = self._parse_expression()
            self._accept(TokenType.BLOCK_THEN)
            n.right = self._parse_statements()
            node.elseifnodes.append(n)

            t = self._cur_token_type()

        if self._cur_token_type() == TokenType.BLOCK_ELSE:
            self._accept(TokenType.BLOCK_ELSE)
            node.elsenode = self._parse_statements()

        self._accept(TokenType.BLOCK_ENDIF)
        return node

    def _parse_call(self):
        # Call the specified function <func>
        # Available functions:
        #  - PRINT(str)
        node = CallNode()
        node.type = self._cur_token
        self._accept(TokenType.IDENTIFIER)

        self._accept(TokenType.LPARENT)

        t = self._cur_token_type()
        while t not in [TokenType.RPARENT]:
            if t == TokenType.COMMA:
                self._accept(TokenType.COMMA)
            else:
                node.args.append(self._parse_expression())
            t = self._cur_token_type()

        self._accept(TokenType.RPARENT)
        return node

    def _parse_loop(self) -> LoopNode:
        node = LoopNode()
        self._loops += 1
        self._accept(TokenType.LOOP_REPEAT)
        node.right = self._parse_statements()

        try:
            if self._cur_token.ttype == TokenType.LOOP_FOREVER:
                # Repeat Forever -> node.left condition is (1) or (1=1)
                self._accept(TokenType.LOOP_FOREVER)
                forever_cond = ExpressionNode()
                v1 = ValueNode(value_type=ValueType.NUMBER)
                v1.value = 1
                forever_cond.left = v1
                forever_cond.right = v1
                forever_cond.op = OpType.NOTEQUALS
                node.left = forever_cond
            elif self._cur_token.ttype == TokenType.LOOP_UNTIL:
                # Repeat Until <expr> -> node.left condition is <expr>
                self._accept(TokenType.LOOP_UNTIL)
                node.left = self._parse_expression()
                node.condition_pos = ConditionPos.BOTTOM
        except AttributeError:
            self._fail('Missing loop body')

        self._loops -= 1
        return node

    def _parse_exit(self) -> ExitNode:
        if self._loops <= 0:
            self._fail('Exit without loop')
        node = ExitNode()
        node.value = ValueNode(value_type=ValueType.KEYWORD)
        self._accept(TokenType.LOOP_BREAK)
        return node

    def _parse_array(self) -> ArrayNode:
        node = ArrayNode()

        self._accept(TokenType.LSQBRACKET)

        t = self._cur_token_type()
        while t not in [TokenType.RSQBRACKET]:
            if t == TokenType.COMMA:
                self._accept(TokenType.COMMA)
            else:
                tmp_node = self._parse_expression()
                node.values.append(tmp_node)
            t = self._cur_token_type()

        self._accept(TokenType.RSQBRACKET)
        return node

    def _parse_sub(self) -> ProcSubNode:
        node = ProcSubNode()
        # sub my_name(args)
        #   .. sub_body
        # endsub
        self._accept(TokenType.PROC_SUB)
        node.left = self._cur_token
        self._accept(TokenType.IDENTIFIER)
        if self._cur_token.ttype == TokenType.LPARENT:
            # parantheses without arguments are optional,
            # however, they are required if arguments are passed
            self._accept(TokenType.LPARENT)
            t = self._cur_token_type()
            while t not in [TokenType.RPARENT]:
                if t == TokenType.COMMA:
                    self._accept(TokenType.COMMA)
                else:
                    tmp_node = self._cur_token
                    self._accept(TokenType.IDENTIFIER)
                    node.args.append(tmp_node)
                t = self._cur_token_type()

            self._accept(TokenType.RPARENT)

        node.right = self._parse_statements()

        self._accept(TokenType.PROC_ENDSUB)
        return node

    def _parse_subreturn(self) -> ProcSubReturnNode:
        node = ProcSubReturnNode()
        print("Proc sub return node")
        self._accept(TokenType.PROC_RETURN)
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
        while t in [TokenType.EQUALS, TokenType.REL_NOTEQ, TokenType.REL_GT, TokenType.REL_GTEQ, TokenType.REL_LT, TokenType.REL_LTEQ]:
            self._accept(t)

            if t == TokenType.EQUALS:
                node.op = OpType.EQUALS
            elif t == TokenType.REL_NOTEQ:
                node.op = OpType.NOTEQUALS
            elif t == TokenType.REL_GT:
                node.op = OpType.GT
            elif t == TokenType.REL_GTEQ:
                node.op = OpType.GTEQ
            elif t == TokenType.REL_LT:
                node.op = OpType.LT
            elif t == TokenType.REL_LTEQ:
                node.op = OpType.LTEQ

            node.left = node_tmp
            node.right = self._parse_compareexpr()
            return node
        return node_tmp

    def _parse_addexpr(self) -> Union[TermNode, ExpressionNode, ValueNode]:
        node = TermNode()
        node_tmp = self._parse_modexpr()

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

    def _parse_modexpr(self) -> Union[TermNode, ExpressionNode, ValueNode]:
        node = TermNode()
        node_tmp = self._parse_multexpr()

        t = self._cur_token_type()
        while t == TokenType.MODULO:
            self._accept(t)
            node.op = OpType.MOD
            node.left = node_tmp
            node.right = self._parse_modexpr()
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
            try:
                if self._cur_token.ttype == TokenType.LSQBRACKET:
                    # Access array at given index, i.e. my_var[0]
                    self._accept(TokenType.LSQBRACKET)
                    node.value_type = ValueType.ARRAYELEMENT
                    node.identifier = node.value
                    node.index = self._parse_expression()
                    self._accept(TokenType.RSQBRACKET)
            except AttributeError:
                pass
            return node
        else:
            self._fail('Invalid value for token')
