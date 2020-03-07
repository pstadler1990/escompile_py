from esc.parser import Node, Parser, AssignmentNode, TermNode, OpType, ValueNode, RootNode, ValueType
from esc.symbols import SymbolTable, NUM_SCOPES, GLOBAL_SCOPE, SymbolEntryNumber


class NodeVisitor:
    def visit(self, node: Node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node: Node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class CodeGenerator(NodeVisitor):
    def __init__(self):
        self._parser = Parser()
        self._global_symbols = SymbolTable()
        self._local_symbols = [SymbolTable()] * NUM_SCOPES
        self._scope = GLOBAL_SCOPE

    def generate(self, root: RootNode):
        for node in root.nodes:
            self.visit(node)

    def visit_AssignmentNode(self, node: AssignmentNode):
        # LET IDENTIFIER = <expr>
        # PUSH <expr> (number|string)
        # PUSHG|PUSHL [index]
        # TODO: Scopes? Lookup?
        value = self.visit(node.right)
        if self._scope == GLOBAL_SCOPE:
            self._global_symbols.symbol_add(node.left.value, SymbolEntryNumber(value))

    def visit_TermNode(self, node: TermNode):
        # TODO: This only works, if both variables (node left.right) are literals!
        # If one or both sides are an identifier (variable), then we cannot simply add the two values,
        # instead we have to generate PUSH and POPG/L ops
        if node.op == OpType.ADD:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op == OpType.SUB:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op == OpType.MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op == OpType.DIV:
            return self.visit(node.left) / self.visit(node.right)

    def visit_ValueNode(self, node: ValueNode):
        if node.value_type == ValueType.VARIABLE:
            # TODO: Fetch value
            if self._scope == GLOBAL_SCOPE:
                try:
                    symbol = self._global_symbols.find_symbol(node.value)
                    return symbol.value
                except NameError:
                    # TODO: Search in locals (scope)
                    pass
        return node.value
