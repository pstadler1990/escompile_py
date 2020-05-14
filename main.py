from esc.codegen import CodeGenerator
from esc.parser import Parser

if __name__ == '__main__':
    p = Parser()
    c = CodeGenerator()

    statements = p.parse('let a = 34\n'
                         'let b = a * 2\n'
                         'let c = a + b + 2 * a'
                         )
    for statement in statements:
        c.generate(statement)
