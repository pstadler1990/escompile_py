import enum
import struct
from esc.parser import Node, Parser, AssignmentNode, TermNode, OpType, ValueNode, ValueType, IfNode, ExpressionNode, \
    CallNode, LoopNode
from abc import ABC
from termcolor import colored


class OP(enum.Enum):
    NOP = 0
    PUSHG = 0x10
    POPG = 0x11
    PUSHL = 0x12
    POPL = 0x13
    PUSH = 0x14
    POP = 0x15
    PUSHS = 0x16

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

    @classmethod
    def has(cls, value):
        return value in cls._value2member_map_


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

    def _generic_visit(self, node: Node, parent: Node = None):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class CodeGenerator(NodeVisitor):
    def __init__(self):
        self.symbols = {0: []}
        # Prefill global symbols with builtin variables
        self.parser = Parser()
        self.bytes_out = []
        self.scope = 0
        self.concat_mode = 0

    def generate(self, root: Node):
        return self.visit(root)

    def finalize(self):
        # merge multiple CONCAT ops
        out_stream = []
        for b in self.bytes_out:
            out_stream.append(str(b))
        return out_stream

    def _format_arg(self, bc, op: OP = None):
        if op is not None and op.value in [OP.JMP.value, OP.JZ.value]:
            a1 = self.bytes_out[bc + 1]
            a2 = self.bytes_out[bc + 2]
            a3 = self.bytes_out[bc + 3]
            a4 = self.bytes_out[bc + 4]
            a5 = self.bytes_out[bc + 5]
            a6 = self.bytes_out[bc + 6]
            a7 = self.bytes_out[bc + 7]
            a8 = self.bytes_out[bc + 8]
            bts = hex((
                    ((a1 & 0xFF) << 56) |
                    ((a2 & 0xFF) << 48) |
                    ((a3 & 0xFF) << 40) |
                    ((a4 & 0xFF) << 32) |
                    ((a5 & 0xFF) << 24) |
                    ((a6 & 0xFF) << 16) |
                    ((a7 & 0xFF) << 8) |
                    (a8 & 0xFF)))[2:]

            if bts == '0' or len(bts) < 2:
                return 0.0
            b = bytearray.fromhex(bts)
            r = struct.unpack('>d', b)[0]
            return r
        else:
            a1 = self.bytes_out[bc + 1]
            a2 = self.bytes_out[bc + 2]
            a3 = self.bytes_out[bc + 3]
            a4 = self.bytes_out[bc + 4]
            bts = hex((
                        ((a1 & 0xFF) << 24) |
                        ((a2 & 0xFF) << 16) |
                        ((a3 & 0xFF) << 8) |
                        (a4 & 0xFF)))[2:]

            if bts == '0' or len(bts) < 2:
                return 0.0
            b = bytearray.fromhex(bts)
            while len(b) < 8:
                b.append(0)
            r = struct.unpack('>d', b)[0]
            return r

    def format(self):
        lc: int = 0
        bc: int = 0

        while bc < len(self.bytes_out):
            b = self.bytes_out[bc]
            if OP.has(b):
                if b in [OP.PUSHS.value]:
                    # String len
                    strlen = int(self._format_arg(bc))
                    ostr: str = ''
                    brem: int = 0
                    while brem < strlen:
                        ostr += chr(self.bytes_out[bc + 9 + brem])
                        brem += 1

                    print("{lc} @ {adr}\t\t{op}\t\"{str}\"".format(lc=lc, adr=bc, op=OP.value2member_map_[b], str=ostr))
                    bc += strlen + 9
                else:
                    arg1 = self._format_arg(bc, op=OP.value2member_map_[b])
                    # arg2 = self._format_arg(bc + 9)
                    print("{lc} @ {adr}\t\t{op}\t\t{a1}".format(lc=lc, adr=bc, op=OP.value2member_map_[b], a1=arg1))
                    brem: int = 9
                    while brem > 0:
                        brem -= 1
                        bc += 1

                lc += 1

    def _symbol_exists(self, symbol: str, scope: int = 0):
        return next(filter(lambda s: s.name == symbol, self.symbols.get(scope)), None) is not None

    def _find_symbol(self, symbol: str, scope: int = 0):
        # if symbol not found in current scope: change scope to 0 and try again
        try:
            sym = next(filter(lambda s: s.name == symbol, self.symbols.get(scope)), None)
            sym_index = self.symbols.get(scope).index(sym)
            return sym, sym_index, scope
        except:
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
        if self.scope > 0:
            try:
                for symbol in self.symbols.get(self.scope):
                    self._insert_symbol(symbol, scope=self.scope + 1)
            except TypeError:
                print(colored("Could not copy scope {s}".format(s=self.scope), "red"))
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
            print(colored("SYMOBLS: ", "yellow"), self.symbols)

        _, varid, varscope = self._find_symbol(node.left.value, scope=self.scope)

        # PUSHL / PUSHG
        if varscope == 0:
            self._emit_operation(OP.PUSHG, arg1=varid)
        else:
            self._emit_operation(OP.PUSHL, arg1=varid)

    def visit_TermNode(self, node: TermNode, parent: Node = None):
        if node.op == OpType.ADD:
            res1 = self.visit(node.left, node)
            res2 = self.visit(node.right, node)
            if isinstance(res1, float) and isinstance(res2, float):
                # Constant addition
                # FIXME: Instead of the two PUSHes of res1 and res2 and the ADD instr,
                # FIXME: we should only PUSH the result of the addition
                self._emit_operation(OP.ADD)
                return res1 + res2
            else:
                # Mixed string addition (concatenate)
                # TODO: We need to determine, which concat param is pushed first (OP_CONCAT_LEFT | RIGHT)
                self._emit_operation(OP.CONCAT, arg1=self.concat_mode)

        elif node.op == OpType.SUB:
            res1 = self.visit(node.left, node)
            res2 = self.visit(node.right, node)
            if isinstance(res1, float) and isinstance(res2, float):
                self._emit_operation(OP.SUB)
                return res1 - res2
        elif node.op == OpType.MUL:
            res1 = self.visit(node.left, node)
            res2 = self.visit(node.right, node)
            if isinstance(res1, float) and isinstance(res2, float):
                self._emit_operation(OP.MUL)
                return res1 * res2
        elif node.op == OpType.DIV:
            res1 = self.visit(node.left, node)
            res2 = self.visit(node.right, node)
            if isinstance(res1, float) and isinstance(res2, float):
                self._emit_operation(OP.DIV)
                return res1 / res2

    def visit_ValueNode(self, node: ValueNode, parent: Node = None):
        print("ValueNode", node, " with parent ", parent)
        # let a = 3         -> AssignmentNode       PUSH 3, PUSH(L|G) [index a]
        # let a = 3 + 3     -> TermNode             PUSH 3, PUSH 3, ADD, PUSH(L|G) [index a]
        # let a = b         -> AssignmentNode       POP(L|G) [b], PUSH(L|G) [index a]
        # let a = b * 2
        # if a = 2
        # if a + 2 = 3
        if node.value_type == ValueType.IDENTIFIER:
            try:
                tmp_symbol, tmp_index, tmp_scope = self._find_symbol(node.value, self.scope)
                if tmp_scope == 0:
                    self._emit_operation(OP.POPG, arg1=tmp_index)
                else:
                    self._emit_operation(OP.POPL, arg1=tmp_index)
                return tmp_symbol.value  # return pop_index
            except AttributeError:
                self._fail('Unknown symbol {id}'.format(id=node.value))
        elif node.value_type == ValueType.NUMBER:
            # Initialize with constant
            self._emit_operation(OP.PUSH, arg1=node.value)
        elif node.value_type == ValueType.STRING:
            # PUSHS string
            self._emit_operation(OP.PUSHS, arg1=len(node.value), arg2=node.value)
        return node.value

    def _backpatch(self, head_addr, patch_addr):
        f = float(patch_addr)
        s = bytearray(struct.pack('>d', f))
        if len(s) > 8:
            self._fail("Illegal number")
        try:
            self.bytes_out[head_addr + 1] = s[0]
            self.bytes_out[head_addr + 2] = s[1]
            self.bytes_out[head_addr + 3] = s[2]
            self.bytes_out[head_addr + 4] = s[3]
            self.bytes_out[head_addr + 5] = s[4]
            self.bytes_out[head_addr + 6] = s[5]
            self.bytes_out[head_addr + 7] = s[6]
            self.bytes_out[head_addr + 8] = s[7]
            print(colored("Patched {h} with {p}".format(h=head_addr, p=patch_addr), "green"))
        except IndexError:
            print(colored("Cannot patch {h} with {p}".format(h=head_addr, p=patch_addr), "red"))

    def visit_IfNode(self, node: IfNode, parent: Node = None):
        print("If statement", node)
        patches = []
        jz_last = None

        self.visit(node.left)

        patches.append(len(self.bytes_out))
        self._emit_operation(OP.JZ, arg1=0xFFFFFFFF)
        # If body
        self._open_scope()
        for statement in node.right:
            self.visit(statement)

        if node.elseifnodes:
            # 1. Patch root IF node to address of first elseif node
            bytecnt_before_elif = len(self.bytes_out) + 9
            patch_head = patches.pop()
            self._backpatch(patch_head, bytecnt_before_elif)

            patches.append(len(self.bytes_out))
            self._emit_operation(OP.JMP, arg1=0xFFFFFFFF)

            for cnt, elifnode in enumerate(node.elseifnodes):
                # Evalulate if(<expr>)
                self.visit(elifnode.left)

                patches.append(len(self.bytes_out))

                if node.elsenode and cnt >= len(node.elseifnodes) - 1:
                    jz_last = len(self.bytes_out)

                self._emit_operation(OP.JZ, arg1=0xFFFFFFFF)

                for statement in elifnode.right:
                    self.visit(statement)

                bytecnt_after_elif = len(self.bytes_out) + 9

                patch_head = patches.pop()
                self._backpatch(patch_head, bytecnt_after_elif)

                patches.append(len(self.bytes_out))
                self._emit_operation(OP.JMP, arg1=0xFFFFFFFF)

                if node.elsenode and cnt >= len(node.elseifnodes) - 1:
                    print(colored("last node before else", "blue"))

        if node.elsenode:
            # # Patch previous IF / ELSEIF with ELSE + 1
            # patch_head = patches.pop()
            self._backpatch(jz_last, len(self.bytes_out) + 9)
            #
            patches.append(len(self.bytes_out))
            #
            self._emit_operation(OP.JMP, arg1=0xFFFFFFFF)
            for statement in node.elsenode:
                self.visit(statement)
            #
            endif = len(self.bytes_out)
            #
            patch_head = patches.pop()
            self._backpatch(patch_head, endif)
            pass

        bytecnt_after_all = len(self.bytes_out)
        for p in range(len(patches)):
            patch_head = patches.pop()
            self._backpatch(patch_head, bytecnt_after_all)

        self._close_scope()

    def visit_LoopNode(self, node: LoopNode, parent: Node = None):
        print("loop node")
        patches = []
        self.visit(node.left)

        loop_head = len(self.bytes_out)
        patches.append(loop_head)
        self._emit_operation(OP.JZ, arg1=0xFFFFFFFF)
        # Loop body
        self._open_scope()
        for statement in node.right:
            self.visit(statement)

        self._emit_operation(OP.JMP, loop_head + 9)

        patch_head = patches.pop()
        bytecnt_after_all = len(self.bytes_out)
        self._backpatch(patch_head, bytecnt_after_all)

        self._close_scope()

    def visit_ExpressionNode(self, node: ExpressionNode, parent: Node = None):
        print("Expression node", node)
        if node.op == OpType.AND:
            self.visit(node.left)  # res1
            self.visit(node.right)  # res2
            self._emit_operation(OP.AND)
            # return res1 and res2
        elif node.op == OpType.EQUALS:
            self.visit(node.left)
            self.visit(node.right)
            self._emit_operation(OP.EQ)
        # TODO: Add other types (OR, LT, GT, LTE, GTE)

    def visit_CallNode(self, node: CallNode, parent: Node = None):
        print("Call node", node)
        if node.type.lower() == 'print':
            # Print signature:
            # PUSH STRING <param> | BUILD STRING <param> onto STACK
            self.visit(node.value)
            # CALL __print
            self._emit_operation(OP.PRINT)
            pass

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
            if isinstance(arg2, str):
                bytes_out.extend(arg2.encode())
            else:
                if arg2 <= 0xFFFFFFFF:
                    b = list(bytearray.fromhex(hex(struct.unpack('<Q', struct.pack('<d', arg2))[0]).lstrip('0x')))
                    while len(b) < 8:
                        b.append(0x00)
                    bytes_out.extend(b)
                else:
                    self._fail('Argument 2 is too large')

        if op != OP.PUSHS:
            while len(bytes_out) < 9:
                bytes_out.append(0x00)
            if len(bytes_out) != 9:
                self._fail('OP and / or arguments are invalid')

        print([hex(b) for b in bytes_out])
        self.bytes_out.extend(bytes_out)
