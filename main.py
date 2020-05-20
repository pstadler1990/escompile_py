from esc.codegen import CodeGenerator
from esc.parser import Parser

if __name__ == '__main__':
    p = Parser()
    c = CodeGenerator()
    # FIXME: Endet in 3 PUSHS und 2 CONCATS, aber: das erste CONCAT verbindet "World" + " " (die obersten beiden stack elemente)
    # FIXME: und das zweite CONCAT verbindet dann "World " + "Hello" -> ergibt also "World Hello" statt "Hello World"
    # HELLO
    # _
    # WORLD
    # !
    # CONCAT s-3 s-2 s-1
    statements = p.parse('let a = 4\n'
                         'if(a = 4) then\n'
                         'print("a ist 4")\n'
                         'let b = a + 2\n'
                         'print("und b ist: " + b)\n'
                         'else\n'
                         'print("a ist 3")\n'
                         'print("und hier steht" + " noch mehr!")\n'
                         'endif'
                         )
    for statement in statements:
        c.generate(statement)

    print(c.bytes_out)
    #c.finalize()
