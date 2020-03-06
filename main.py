from esc.codegen import CodeGenerator
from esc.parser import Parser

if __name__ == '__main__':
    p = Parser()
    c = CodeGenerator()

    statements = p.parse('let a = (3*4) + (18/9)')
    test_statement = statements[0]
    c.generate(test_statement)
