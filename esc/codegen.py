import enum
import struct
from esc.parser import Node, Parser, AssignmentNode, TermNode, OpType, ValueNode, ValueType, IfNode, ExpressionNode
from abc import ABC


class OP(enum.Enum):
    NOP = 0
    PUSHG = 0x10
    POPG = 0x11
    PUSHL = 0x12
    POPL = 0x13
    PUSH = 0x14
    POP = 0x15

    EQ = 0x20
    LT = 0x21
    GT = 0x22
    LTEQ = 0x23
    GTEQ = 0x24

    ADD = 0x30
    SUB = 0x32
    MUL = 0x33
    DIV = 0x34
    AND = 0x35
    OR = 0x36
    NOT = 0x37
    CONCAT = 0x38
    MOD = 0x39

    JZ = 0x40
    JMP = 0x41

    PRINT = 0x50


class Symbol(ABC):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return '[SYMBOL {name}]'.format(name=self.name)


class IntegerSymbol(Symbol):
    def __init__(self, name: str, value: int):
        super().__init__(name)
        self.value = value


class NodeVisitor:
    def visit(self, node: Node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node: Node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class CodeGenerator(NodeVisitor):
    def __init__(self):
        self.symbols = {}
        self.parser = Parser()

    def generate(self, root: Node):
        return self.visit(root)

    def visit_AssignmentNode(self, node: AssignmentNode):
        # LET IDENTIFIER = <expr>
        # PUSH <expr> (number|string)
        # PUSHG|PUSHL [index]
        print('Assign identifier {id}'.format(id=node.left.value))
        # TODO: Scopes? Lookup?
        value = self.visit(node.right)

        # Insert into symbol table
        if self.symbols.get(node.left.value):
            print('Symbol {id} already found'.format(id=node.left.value))
        else:
            self.symbols[node.left.value] = IntegerSymbol(name=node.left.value, value=value)
            print(self.symbols)

        self._emit_operation(OP.PUSH, arg1=value)

    def visit_TermNode(self, node: TermNode):
        if node.op == OpType.ADD:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op == OpType.SUB:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op == OpType.MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op == OpType.DIV:
            return self.visit(node.left) / self.visit(node.right)

    def visit_ValueNode(self, node: ValueNode):
        print("ValueNode", node)
        if node.value_type == ValueType.IDENTIFIER:
            # let a = b
            tmp_value = self.symbols.get(node.value)
            try:
                return tmp_value.value
            except AttributeError:
                self._fail('Unknown symbol {id}'.format(id=node.value))
        return node.value

    def visit_IfNode(self, node: IfNode):
        print("If statement", node)
        # node.left = <conditional expression>  i.e. a = 3 and b > 42
        self.visit(node.left)
        # node.right = <statement(s)>   body of if statement

    def visit_ExpressionNode(self, node: ExpressionNode):
        print("Expression node", node)
        if node.op == OpType.AND:
            res1 = self.visit(node.left)
            res2 = self.visit(node.right)
            return res1 and res2
            # TODO: Shorten to self.visit(node.left) and self.visit(node.right) after implementation
        elif node.op == OpType.EQUALS:
            return self.visit(node.left) == self.visit(node.right)
        # TODO: Add other types (OR, LT, GT, LTE, GTE)

    def _fail(self, msg: str = ''):
        raise Exception(msg)

    def _emit_operation(self, op: OP, arg1=0x00000000, arg2=0x00000000):
        # [1 Byte OP][4 Byte arg1][4 Byte arg2]
        bytes_out: list = []
        if op.value > 256:
            self._fail('OP code must not exceed 256')
        bytes_out.append(op.value)

        if arg1 < 0xFFFFFFFF:
            bytes_out.extend(list(struct.pack('f', arg1)))
        else:
            self._fail('Argument 1 is too large')

        if arg2 < 0xFFFFFFFF:
            bytes_out.extend(list(struct.pack('f', arg2)))
        else:
            self._fail('Argument 2 is too large')

        print(bytes_out)
