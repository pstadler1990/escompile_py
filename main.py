from esc.codegen import CodeGenerator
from esc.parser import Parser

if __name__ == '__main__':
    p = Parser()
    c = CodeGenerator()

    statements = p.parse('let a = 42\n'
                         'let b = 12\n'
                         'if a = 42 then\n'
                         'let c = 39.123\n'
                         'if 1 = 2 then\n'
                         'let d = c * 2\n'
                         'endif\n'
                         'let e = 3.14\n'
                         'endif'
                         )
    for statement in statements:
        c.generate(statement)

    print(c.bytes_out)
