import os
import subprocess
from esc.codegen import CodeGenerator
from esc.parser import Parser

# TODO: If release
import sys
sys.tracebacklimit = 0

if __name__ == '__main__':
    p = Parser()
    c = CodeGenerator()

    statements = p.parse('''
                        sub my_sub(a, b)
                            print("Called sub with a: " + a)
                            print("b: " + b)
                        endsub
                        print("before sub")
                        my_sub(1, 2)
                        print("after sub")
                        let a = 32
                        print("now im after the a assignment")
                        my_sub(42, 69)
                        print("THIS IS THE END!")
                        '''
                         )
    for statement in statements:
        c.generate(statement)

    print(c.bytes_out)
    print(c.format())
    fbytes = c.finalize()

    # CALL vm.exe with bytes_out -b option
    subprocess.Popen(["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes)
    os.system('taskkill /f /im es_vm.exe')
