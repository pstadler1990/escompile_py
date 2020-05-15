from esc.codegen import CodeGenerator
from esc.parser import Parser

if __name__ == '__main__':
    p = Parser()
    c = CodeGenerator()

    statements = p.parse('let a = 34\n'
                         'if (a = 3 and 1=2) then\n'
                         'let b = 12.34\n'
                         'endif'
                         )
    for statement in statements:
        c.generate(statement)

    print(c.bytes_out)
