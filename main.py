from esc.codegen import CodeGenerator
from esc.parser import Parser

if __name__ == '__main__':
    p = Parser()
    c = CodeGenerator()

    statements = p.parse('let a = 3 * 42\n'
                         'let b = 9 + a\n'
                         'let c = a + b\n'
                         'let a = 999.69\n')
    c.generate(statements)
    print(c._global_symbols)
