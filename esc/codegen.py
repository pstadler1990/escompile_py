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
    def visit(self, node: Node, parent: Node = None):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node, parent)

    def _generic_visit(self, node: Node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class CodeGenerator(NodeVisitor):
    def __init__(self):
        self.symbols = {0: []}
        # Prefill global symbols with builtin variables
        self.parser = Parser()
        self.bytes_out = []
        self.scope = 0

    def generate(self, root: Node):
        return self.visit(root)

    def _symbol_exists(self, symbol: str, scope: int = 0):
        return next(filter(lambda s: s.name == symbol, self.symbols.get(scope)), None) is not None

    def _find_symbol(self, symbol: str, scope: int = 0):
        # if symbol not found in current scope: change scope to 0 and try again
        try:
            sym = next(filter(lambda s: s.name == symbol, self.symbols.get(scope)), None)
            sym_index = self.symbols.get(scope).index(sym)
            return sym, sym_index, scope
        except ValueError:
            if scope != 0:
                return self._find_symbol(symbol, scope=0)
            else:
                self._fail('Symbol {s} not found'.format(s=symbol))

    def _insert_symbol(self, symbol: Symbol, scope: int = 0):
        try:
            self.symbols.get(scope).append(symbol)
        except AttributeError:
            self.symbols[scope] = []
            self.symbols.get(scope).append(symbol)

    def _open_scope(self):
        # TODO: Opening a scope needs to copy all the symbols from the previous scope into the new symbol table
        if self.scope > 0:
            for symbol in self.symbols.get(self.scope):
                self._insert_symbol(symbol, scope=self.scope + 1)
        self.scope += 1

    def _close_scope(self):
        self.scope = max(0, self.scope - 1)

    def visit_AssignmentNode(self, node: AssignmentNode, parent: Node = None):
        # LET IDENTIFIER = <expr>
        # PUSH <expr> (number|string)
        # PUSHG|PUSHL [index]
        print('Assign identifier {id}'.format(id=node.left.value))
        # TODO: Scopes? Lookup?
        value = self.visit(node.right, node)

        # Insert into symbol table
        if self._symbol_exists(node.left.value):  # self._find_symbol(node.left.value):
            print('Symbol {id} already found'.format(id=node.left.value))
        else:
            self._insert_symbol(symbol=IntegerSymbol(name=node.left.value, value=value), scope=self.scope)
            print(self.symbols)

        _, varid, varscope = self._find_symbol(node.left.value, scope=self.scope)

        # PUSHL / PUSHG
        if varscope == 0:
            self._emit_operation(OP.PUSHG, arg1=varid)
        else:
            self._emit_operation(OP.PUSHL, arg1=varid)

    def visit_TermNode(self, node: TermNode, parent: Node = None):
        if node.op == OpType.ADD:
            return self.visit(node.left, node) + self.visit(node.right, node)
        elif node.op == OpType.SUB:
            return self.visit(node.left, node) - self.visit(node.right, node)
        elif node.op == OpType.MUL:
            return self.visit(node.left, node) * self.visit(node.right, node)
        elif node.op == OpType.DIV:
            return self.visit(node.left, node) / self.visit(node.right, node)

    def visit_ValueNode(self, node: ValueNode, parent: Node = None):
        print("ValueNode", node, " with parent ", parent)

        # let a = 3         -> AssignmentNode       PUSH 3, PUSH(L|G) [index a]
        # let a = 3 + 3     -> TermNode             PUSH 3, PUSH 3, ADD, PUSH(L|G) [index a]
        # let a = b         -> AssignmentNode       POP(L|G) [b], PUSH(L|G) [index a]
        # let a = b * 2
        # if a = 2
        # if a + 2 = 3

        if node.value_type == ValueType.IDENTIFIER:
            # let a = b
            # TODO: emit POP(L|G) [b]
            # TODO: ValueNode can either PUSH a number value, or POP(L|G) depending on the context of the node visit
            # TODO: a = 3 (assignment with constant) results in a PUSH <number> followed by a PUSH(L|G) [symtable_pos]
            # is_rvalue = any(isinstance(parent, n) for n in [AssignmentNode])
            # TODO: if(a = 3) ... (expr) results in a POP(L|G) [symtable_pos]

            # if is_rvalue:
            #    # RVALUE means constant assignment, so PUSH value
            #    self._emit_operation(OP.PUSH, arg1=node.value)

            # tmp_value = self.symbols.get(node.value)    # TODO: Remove as we cannot receive the value here
            # pop_index = self.symbols.index(...) TODO: Replace dict with proper data structure
            try:
                tmp_symbol, tmp_index, tmp_scope = self._find_symbol(node.value, self.scope)
                # TODO: POP(L|G) variable
                if tmp_scope == 0:
                    self._emit_operation(OP.POPG, arg1=tmp_index)
                else:
                    self._emit_operation(OP.POP, arg1=tmp_index)
                return tmp_symbol.value  # return pop_index
            except AttributeError:
                self._fail('Unknown symbol {id}'.format(id=node.value))
        elif node.value_type == ValueType.NUMBER:
            # Initialize with constant
            self._emit_operation(OP.PUSH, arg1=node.value)
        return node.value

    def visit_IfNode(self, node: IfNode, parent: Node = None):
        print("If statement", node)

        self.visit(node.left)
        bytecnt_before = len(self.bytes_out)
        self._emit_operation(OP.JZ, arg1=0xFFFFFFFF)
        # If body
        self._open_scope()
        for statement in node.right:
            self.visit(statement)
        bytecnt_after = len(self.bytes_out)
        # Patch dummy addresses 0xFFFFFFFF
        self.bytes_out[bytecnt_before + 1] = ((bytecnt_after >> 24) & 0xFF)
        self.bytes_out[bytecnt_before + 2] = ((bytecnt_after >> 16) & 0xFF)
        self.bytes_out[bytecnt_before + 3] = ((bytecnt_after >> 8) & 0xFF)
        self.bytes_out[bytecnt_before + 4] = (bytecnt_after & 0xFF)

        self._close_scope()

    def visit_ExpressionNode(self, node: ExpressionNode, parent: Node = None):
        print("Expression node", node)
        if node.op == OpType.AND:
            self.visit(node.left)   # res1
            self.visit(node.right)  # res2
            self._emit_operation(OP.AND)
            # return res1 and res2
        elif node.op == OpType.EQUALS:
            self.visit(node.left)
            self.visit(node.right)
            self._emit_operation(OP.EQ)
        # TODO: Add other types (OR, LT, GT, LTE, GTE)

    def _fail(self, msg: str = ''):
        raise Exception(msg)

    def _emit_operation(self, op: OP, arg1=None, arg2=None):
        # [1 Byte OP][4 Byte arg1][4 Byte arg2]
        bytes_out: list = []
        if op.value > 256:
            self._fail('OP code must not exceed 256')
        bytes_out.append(op.value)

        if arg1 is not None:
            if arg1 <= 0xFFFFFFFF:
                b = list(bytearray.fromhex(hex(struct.unpack('<Q', struct.pack('<d', arg1))[0]).lstrip('0x')))
                while len(b) < 8:
                    b.append(0x00)
                bytes_out.extend(b)
            else:
                self._fail('Argument 1 is too large')

        if arg2 is not None:
            if arg2 <= 0xFFFFFFFF:
                b = list(bytearray.fromhex(hex(struct.unpack('<Q', struct.pack('<d', arg2))[0]).lstrip('0x')))
                while len(b) < 8:
                    b.append(0x00)
                bytes_out.extend(b)
            else:
                self._fail('Argument 2 is too large')

        while len(bytes_out) < 9:
            bytes_out.append(0x00)

        print([hex(b) for b in bytes_out])
        self.bytes_out.extend(bytes_out)
