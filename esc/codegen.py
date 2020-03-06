from esc.parser import Node, Parser, AssignmentNode, TermNode, OpType, ValueNode


class NodeVisitor:
    def visit(self, node: Node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self._generic_visit)
        return visitor(node)

    def _generic_visit(self, node: Node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class CodeGenerator(NodeVisitor):
    def __init__(self):
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
        print(value)

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
        return node.value
