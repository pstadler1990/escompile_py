import enum
import struct
from typing import Union
from esc.parser import Node, Parser, AssignmentNode, TermNode, OpType, ValueNode, ValueType, IfNode, ExpressionNode, \
    CallNode, LoopNode, ExitNode, ConditionPos, ArrayNode, ProcSubNode, ProcSubReturnNode, ProcFuncNode, ExternApiNode, \
    ImportNode, UnaryNode
from abc import ABC

E_MAX_LOCALS = 99


class OP(enum.Enum):
    NOP = 0
    PUSHG = 0x10
    POPG = 0x11
    PUSHL = 0x12
    POPL = 0x13
    PUSH = 0x14
    PUSHS = 0x15
    DATA = 0x16
    PUSHA = 0x17
    PUSHAS = 0x18

    EQ = 0x20
    LT = 0x21
    GT = 0x22
    LTEQ = 0x23
    GTEQ = 0x24
    NOTEQ = 0x25

    ADD = 0x30
    NEG = 0x31
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
    JFS = 0x42
    JMPFUN = 0x43
    CALL = 0x44

    PRINT = 0x50
    ARGTYPE = 0x51
    LEN = 0x52

    @classmethod
    def has(cls, value):
        return value in cls._value2member_map_


class Symbol(ABC):
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return '[SYMBOL {name}]'.format(name=self.name)


class VariableSymbol(Symbol):
    def __init__(self, name: str, value, const: bool = False):
        super().__init__(name)
        self.value = value
        self.is_const = const


class ProcedureSymbol(Symbol):
    def __init__(self, name: str, args: int, addr: int):
        super().__init__(name)
        self.args = args
        self.addr = addr
        self.is_const = True


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
        self.loop_patches = []
        self.proc_scope = 100
        self.external_symbols = []
        self.stats = {
            'max_scope': 0,
            'max_arrays': 0,
            'max_symbols': 0,
            'max_strlen': 0
        }

    def generate(self, root: Node):
        return self.visit(root)

    def finalize(self, rle: bool = False):
        # merge multiple CONCAT ops
        out_stream = []
        for b in self.bytes_out:
            out_stream.append(str(b))

        tmp_len = len(out_stream)
        if rle:
            out_stream = self._rle(out_stream)

        print(out_stream)
        print(
            "** STATS: | Bytes: {b} / ASCII: {ai} | Max scope: {s} | Max arrays: {a} | Max symbols: {sy} | Longest string: {slen} **".format(
                b=tmp_len, ai=len(out_stream), s=self.stats['max_scope'], a=self.stats['max_arrays'], sy=self.stats['max_symbols'],
                slen=self.stats['max_strlen']))
        return out_stream

    @staticmethod
    def _rle(in_stream: []):
        out_stream = ""
        last_b = None
        b_cnt = 0
        i = 0
        while i < len(in_stream):
            b = in_stream[i]
            if i > 0 and b != last_b:
                # out_stream.append([b_cnt, last_b])
                out_stream += "{c},{b},".format(c=b_cnt, b=last_b)
                b_cnt = 0
            last_b = b
            b_cnt += 1
            i = i + 1
        if b_cnt > 0:
            # out_stream.append([b_cnt, last_b])
            out_stream += "{c},{b},".format(c=b_cnt, b=last_b)
        return out_stream.rstrip(',')

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
        # TODO: Implement single byte OPs
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
                    if b in [OP.NOP.value, OP.PUSHAS.value, OP.EQ.value, OP.LT.value, OP.GT.value,
                             OP.LTEQ.value, OP.GTEQ.value, OP.NOTEQ.value, OP.ADD.value, OP.NEG.value,
                             OP.SUB.value, OP.MUL.value, OP.DIV.value, OP.AND.value, OP.OR.value,
                             OP.NOT.value, OP.MOD.value, OP.PRINT.value, OP.ARGTYPE.value, OP.LEN.value]:
                        brem = 1
                        arg1 = 0
                    else:
                        arg1 = self._format_arg(bc, op=OP.value2member_map_[b])
                        brem = 9
                    # arg2 = self._format_arg(bc + 9)
                    print("{lc} @ {adr}\t\t{op}\t\t{a1}".format(lc=lc, adr=bc, op=OP.value2member_map_[b], a1=arg1))

                    while brem > 0:
                        brem -= 1
                        bc += 1

                lc += 1

    def _symbol_exists(self, symbol: str, stype, scope: int = 0):
        # try:
        #     return next(filter(lambda s: s.name == symbol, self.symbols.get(scope)),  # ... and type(s) is stype
        #                 None) is not None
        # except TypeError:
        #     if scope != 0:
        #         return self._symbol_exists(symbol, stype, scope=0)
        #     else:
        #         return False
        try:
            sym = next(filter(lambda s: s.name == symbol, self.symbols.get(scope)),
                       None)  # ... == symbol and type(s) is stype ...
            sym_index = self.symbols.get(scope).index(sym)
            return sym_index is not None
        except:
            if symbol in self.external_symbols:
                return True
            if scope != 0:
                return self._symbol_exists(symbol, stype, scope=0)
            else:
                return False

    def _find_symbol(self, symbol: str, stype, scope: int = 0):
        # if symbol not found in current scope: change scope to 0 and try again
        try:
            sym = next(filter(lambda s: s.name == symbol, self.symbols.get(scope)),
                       None)  # ... == symbol and type(s) is stype ...
            sym_index = self.symbols.get(scope).index(sym)
            return sym, sym_index, scope
        except:
            if symbol in self.external_symbols:
                return None
            if scope != 0:
                return self._find_symbol(symbol, stype, scope=0)
            else:
                self._fail('Symbol {s} not found'.format(s=symbol))

    def _insert_symbol(self, symbol: Symbol, scope: int = 0):
        try:
            self.symbols.get(scope).append(symbol)
            self.stats['max_symbols'] = len(self.symbols)
        except AttributeError:
            self.symbols[scope] = []
            self.symbols.get(scope).append(symbol)
            self.stats['max_symbols'] = len(self.symbols)

    def _open_scope(self):
        if self.scope > 0:
            try:
                for symbol in self.symbols.get(self.scope):
                    self._insert_symbol(symbol, scope=self.scope + 1)
            except TypeError:
                pass
        self.scope += 1
        if self.stats['max_scope'] < self.scope:
            self.stats['max_scope'] = self.scope

    def _close_scope(self):
        self.scope = max(0, self.scope - 1)

    def _open_proc_scope(self):
        r = self.proc_scope
        self.proc_scope += (E_MAX_LOCALS + 1)
        return r

    def visit_NoneType(self, node: None, parent: Node = None):
        self._fail(msg="Unexpected compile error")

    def visit_AssignmentNode(self, node: AssignmentNode, parent: Node = None):
        # LET IDENTIFIER = <expr>
        # PUSH <expr> (number|string)
        # PUSHG|PUSHL [index]
        value = self.visit(node.right, node)

        try:
            if node.left.value_type == ValueType.ARRAYELEMENT:
                self.visit(node.left, parent=node)
        except AttributeError:
            pass

        try:
            if node.left.value_type == ValueType.ARRAYELEMENT:
                return
        except AttributeError:
            pass

        # Insert into symbol table
        if node.modify:
            if not self._symbol_exists(node.left.value, stype=VariableSymbol, scope=self.scope):
                self._fail("Symbol {s} not found".format(s=node.left.value))
        else:
            self._insert_symbol(symbol=VariableSymbol(name=node.left.value, value=value, const=node.is_const), scope=self.scope)

        var, varid, varscope = self._find_symbol(node.left.value, stype=VariableSymbol, scope=self.scope)

        if node.modify and var.is_const:
            self._fail("Cannot modify constant {s}".format(s=node.left.value))

        # PUSHL / PUSHG
        if varscope == 0:
            self._emit_operation(OP.PUSHG, arg1=varid)
        else:
            self._emit_operation(OP.PUSHL, arg1=varid)

    def visit_TermNode(self, node: TermNode, parent: Node = None):
        if node.op == OpType.ADD:
            res1 = self.visit(node.left, node)
            res2 = self.visit(node.right, node)
            if (isinstance(res1, float) or isinstance(res1, int)) and (
                    isinstance(res2, float) or isinstance(res2, int)):
                # Number addition
                self._emit_operation(OP.ADD)
                return res1 + res2
            else:
                # Mixed string addition (concatenate)
                self._emit_operation(OP.CONCAT, arg1=self.concat_mode)
        elif node.op == OpType.SUB:
            res1 = self.visit(node.left, node)
            res2 = self.visit(node.right, node)
            if (isinstance(res1, float) or isinstance(res1, int)) and (
                    isinstance(res2, float) or isinstance(res2, int)):
                self._emit_operation(OP.SUB)
                return res1 - res2
        elif node.op == OpType.MUL:
            res1 = self.visit(node.left, node)
            res2 = self.visit(node.right, node)
            if (isinstance(res1, float) or isinstance(res1, int)) and (
                    isinstance(res2, float) or isinstance(res2, int)):
                self._emit_operation(OP.MUL)
                return res1 * res2
        elif node.op == OpType.DIV:
            res1 = self.visit(node.left, node)
            res2 = self.visit(node.right, node)
            if (isinstance(res1, float) or isinstance(res1, int)) and (
                    isinstance(res2, float) or isinstance(res2, int)):
                self._emit_operation(OP.DIV)
                return res1 / res2
        elif node.op == OpType.MOD:
            res1 = self.visit(node.left, node)
            res2 = self.visit(node.right, node)
            if (isinstance(res1, float) or isinstance(res1, int)) and (
                    isinstance(res2, float) or isinstance(res2, int)):
                self._emit_operation(OP.MOD)
                return res1 % res2

    def visit_ValueNode(self, node: ValueNode, parent: Node = None):
        # let a = 3         -> AssignmentNode       PUSH 3, PUSH(L|G) [index a]
        # let a = 3 + 3     -> TermNode             PUSH 3, PUSH 3, ADD, PUSH(L|G) [index a]
        # let a = b         -> AssignmentNode       POP(L|G) [b], PUSH(L|G) [index a]
        # let a = b * 2
        # if a = 2
        # if a + 2 = 3
        if node.value_type == ValueType.IDENTIFIER:
            try:
                tmp_symbol, tmp_index, tmp_scope = self._find_symbol(node.value, stype=VariableSymbol, scope=self.scope)

                if tmp_scope == 0:
                    self._emit_operation(OP.POPG, arg1=tmp_index)
                else:
                    self._emit_operation(OP.POPL, arg1=tmp_index)
                try:
                    if isinstance(parent, ValueNode) and parent.value_type == ValueType.ARRAYELEMENT:
                        self._emit_operation(OP.PUSHAS)
                except AttributeError:
                    pass

                try:
                    return tmp_symbol.value  # return pop_index
                except AttributeError:
                    pass

            except AttributeError:
                self._fail('Unknown symbol {id}'.format(id=node.value))

        elif node.value_type == ValueType.NUMBER:
            # Initialize with constant
            try:
                if isinstance(parent, ValueNode) and parent.value_type == ValueType.ARRAYELEMENT:
                    self._emit_operation(OP.PUSHA, arg1=node.value)
                else:
                    self._emit_operation(OP.PUSH, arg1=node.value)
            except AttributeError:
                self._emit_operation(OP.PUSH, arg1=node.value)

        elif node.value_type == ValueType.STRING:
            # PUSHS string
            self._emit_operation(OP.PUSHS, arg1=len(node.value), arg2=node.value)
            if self.stats['max_strlen'] < len(node.value):
                self.stats['max_strlen'] = len(node.value)
        elif node.value_type == ValueType.ARRAYELEMENT:
            self.visit(node.index, parent=node)
            if parent:
                op = 'pop'
                if isinstance(parent, AssignmentNode):
                    if parent.modify and node == parent.left:
                        op = 'push'

                try:
                    tmp_symbol, tmp_index, tmp_scope = self._find_symbol(node.identifier, stype=VariableSymbol,
                                                                         scope=self.scope)
                    if tmp_scope == 0:
                        if op == 'pop':
                            self._emit_operation(OP.POPG, arg1=tmp_index)
                        else:
                            self._emit_operation(OP.PUSHG, arg1=tmp_index)
                    else:
                        if op == 'pop':
                            self._emit_operation(OP.POPL, arg1=tmp_index)
                        else:
                            self._emit_operation(OP.PUSHL, arg1=tmp_index)
                except AttributeError:
                    self._fail('Unknown symbol {id}'.format(id=node.value))
            return node.index.value
        return node.value

    def visit_UnaryNode(self, node: UnaryNode, parent: Node = None):
        print("visit unary")
        self.visit_ValueNode(node)
        if node.sign == '-':
            self._emit_operation(OP.NEG)
        elif node.sign == '!':
            self._emit_operation(OP.NOT)
        return 0

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
        except IndexError:
            pass

    def visit_IfNode(self, node: IfNode, parent: Node = None):
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

            if node.elsenode:
                # Patch previous IF / ELSEIF with ELSE + 1
                self._backpatch(jz_last, len(self.bytes_out) + 9)
                patches.append(len(self.bytes_out))
                self._emit_operation(OP.JMP, arg1=0xFFFFFFFF)
                for statement in node.elsenode:
                    self.visit(statement)
                endif = len(self.bytes_out)
                patch_head = patches.pop()
                self._backpatch(patch_head, endif)

        else:
            if node.elsenode:
                bytecnt_after_else = len(self.bytes_out) + 9
                patch_head = patches.pop()
                self._backpatch(patch_head, bytecnt_after_else)

                patches.append(len(self.bytes_out))
                self._emit_operation(OP.JMP, arg1=0xFFFFFFFF)
                for statement in node.elsenode:
                    self.visit(statement)
                endif = len(self.bytes_out)
                patch_head = patches.pop()
                self._backpatch(patch_head, endif)

        # TODO: Watch, if these changes will work for every case!
        bytecnt_after_all = len(self.bytes_out)
        for p in range(len(patches)):
            patch_head = patches.pop()
            self._backpatch(patch_head, bytecnt_after_all)

        self._close_scope()

    def visit_LoopNode(self, node: LoopNode, parent: Node = None):
        patches = []

        if node.condition_pos == ConditionPos.TOP:
            self.visit(node.left[0])

            loop_head = len(self.bytes_out)
            patches.append(loop_head)

            self.visit(node.left[1])

            patches.append(len(self.bytes_out))
            self._emit_operation(OP.JZ, arg1=0xFFFFFFFF)

            # Loop body
            self._open_scope()
            for statement in node.right:
                self.visit(statement)

            self._emit_operation(OP.JMP, loop_head)

            patch_head = patches.pop()
            bytecnt_after_all = len(self.bytes_out)
            self._backpatch(patch_head, bytecnt_after_all)
        else:
            self._open_scope()

            loop_head = len(self.bytes_out)

            for statement in node.right:
                self.visit(statement)

            self.visit(node.left)
            self._emit_operation(OP.JZ, arg1=loop_head)

            bytecnt_after_all = len(self.bytes_out)

        # Backpatch exits (breaks)
        while self.loop_patches:
            self._backpatch(self.loop_patches.pop(), bytecnt_after_all)

        self._close_scope()

    def visit_ExpressionNode(self, node: ExpressionNode, parent: Node = None):
        self.visit(node.left, parent=node)
        self.visit(node.right, parent=node)

        if node.op == OpType.AND:
            self._emit_operation(OP.AND)
        elif node.op == OpType.EQUALS:
            self._emit_operation(OP.EQ)
        elif node.op == OpType.NOTEQUALS:
            self._emit_operation(OP.NOTEQ)
        elif node.op == OpType.OR:
            self._emit_operation(OP.OR)
        elif node.op == OpType.LT:
            self._emit_operation(OP.LT)
        elif node.op == OpType.LTEQ:
            self._emit_operation(OP.LTEQ)
        elif node.op == OpType.GT:
            self._emit_operation(OP.GT)
        elif node.op == OpType.GTEQ:
            self._emit_operation(OP.GTEQ)

    def visit_CallNode(self, node: CallNode, parent: Node = None):
        n = node.type.value.lower()
        if n == 'print':
            # Print signature:
            # PUSH STRING <param> | BUILD STRING <param> onto STACK
            self.visit(node.args[0], parent=node)
            # CALL __print
            self._emit_operation(OP.PRINT)
        elif n == 'argtype':
            # CALL __argtype
            self.visit(node.args[0], parent=node)
            self._emit_operation(OP.ARGTYPE)
        elif n == 'len':
            # CALL __len
            self.visit(node.args[0], parent=node)
            self._emit_operation(OP.LEN)
        else:
            try:
                proc = self._find_symbol(node.type.value, stype=ProcedureSymbol, scope=0)[0]

                if proc.args != len(node.args):
                    self._fail('Insufficient amount of arguments for procedure {p} - required {n}, given {g}'.format(
                        p=proc.name, n=proc.args, g=len(node.args)))

                for arg in range(proc.args):
                    try:
                        self.visit(node.args[arg])
                        # self._emit_operation(OP.PUSHL, arg)
                    except IndexError:
                        self._fail(
                            'Insufficient amount of arguments for procedure {p} - required {n}, given {g}'.format(
                                p=proc.name, n=proc.args, g=len(node.args)))

                # Push own return address onto stack
                self._emit_operation(OP.PUSH, len(self.bytes_out) + 18)  # 18 = 9 (this operation) + 9 (next jmp) bytes!

                # JMP to address of sub
                self._emit_operation(OP.JMPFUN, arg1=proc.addr)
            except TypeError:
                # External defined function / subroutine
                for a, arg in enumerate(node.args):
                    self.visit(arg)
                self._emit_operation(OP.PUSHS, arg1=len(node.type.value), arg2=node.type.value)
                # Call needs information on number of arguments (arg1)
                self._emit_operation(OP.CALL, arg1=len(node.args))

            return 1  # required for ADD operation

    def visit_ExitNode(self, node: ExitNode, parent: Node = None):
        self.loop_patches.append(len(self.bytes_out))
        self._emit_operation(OP.JMP, arg1=0xFFFFFFFF)
        # Backpatched later (at forever / loop end) to address of loop end

    def visit_ArrayNode(self, node: ArrayNode, parent: Node = None):
        for v in node.values:
            self.visit(v)
        self._emit_operation(OP.DATA, arg1=len(node.values))
        self.stats['max_arrays'] += 1

    def visit_ProcSubNode(self, node: Union[ProcSubNode, ProcFuncNode], parent: Node = None):
        # node.left = identifier
        # node.right = statements body
        # node.args = argument name(s)
        if not self._symbol_exists(node.left.value, stype=ProcedureSymbol, scope=0):
            proc_head = len(self.bytes_out)
            # self.visit(node.right) -> will generate executable byte code wherever the procedure was declared!
            # Guard the procedure block with a JMP statement at the beginning and patch it to the end of the sub
            self._emit_operation(OP.JMP, arg1=0xFFFFFF)

            self._insert_symbol(
                symbol=ProcedureSymbol(name=node.left.value, args=len(node.args), addr=len(self.bytes_out)),
                scope=0)

            prev_scope = self.scope
            proc_scope = self._open_proc_scope()
            self.scope = proc_scope
            # Pop required values from stack (depending of number of arguments specified!)
            for a, arg in enumerate(node.args):
                # If we call the sub later, we push(l) the given arguments into the new (local) scope!
                # i.e.  my_sub(1, 2, 3) will PUSHL 1 [0], PUSHL 2 [1] and PUSHL 3 [2]
                # Then the procudure will POPL these args again to be used within the sub
                self._insert_symbol(VariableSymbol(name=arg.value, value=a), scope=proc_scope)
                self._emit_operation(OP.PUSHL, arg1=len(node.args) - a - 1)

            for statement in node.right:
                self.visit(statement)

            # OP code JFS (jump from stack), takes a value from the stack and uses it as jump address
            self._emit_operation(OP.JFS)
            self._backpatch(proc_head, len(self.bytes_out))
            self.scope = prev_scope

    def visit_ProcSubReturnNode(self, node: ProcSubReturnNode, parent: Node = None):
        if node.ret_arg is not None:
            self.visit(node.ret_arg, parent=node)
            self._emit_operation(OP.JFS, arg1=1)  # TODO: more than 1 values returned from stack?
        else:
            # no return value
            self._emit_operation(OP.JFS)

    def visit_ProcFuncNode(self, node: ProcFuncNode, parent: Node = None):
        self.visit_ProcSubNode(node, parent)

    def visit_ExternApiNode(self, node: ExternApiNode, parent: Node = None):
        # Add identifier to list of external identifiers
        if node.identifier not in self.external_symbols:
            self.external_symbols.append(node.identifier)

    def visit_ImportNode(self, node: ImportNode, parent: Node = None):
        pass

    def _fail(self, msg: str = ''):
        raise Exception('COMPILER ERROR,{msg}'.format(msg=msg))

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

        if op not in [OP.NOP, OP.PUSHAS, OP.EQ, OP.LT, OP.GT, OP.LTEQ, OP.GTEQ, OP.NOTEQ, OP.ADD, OP.NEG, OP.SUB,
                      OP.MUL, OP.DIV, OP.AND, OP.OR, OP.NOT, OP.MOD, OP.PRINT, OP.ARGTYPE, OP.LEN, OP.PUSHS]:
            while len(bytes_out) < 9:
                bytes_out.append(0x00)
            if len(bytes_out) != 9:
                self._fail('OP and / or arguments are invalid')

        self.bytes_out.extend(bytes_out)
