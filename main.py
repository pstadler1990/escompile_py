from esc.codegen import CodeGenerator
from esc.parser import Parser
import subprocess

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
    statements = p.parse('''
                        let a = 3
                        let b = 4
                        print("a + b = " + a + b)
                        '''
                         )
    for statement in statements:
        c.generate(statement)

    # print(c.bytes_out)
    fbytes = c.finalize()

    # CALL vm.exe with bytes_out -b option
    subprocess.Popen(["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes)
