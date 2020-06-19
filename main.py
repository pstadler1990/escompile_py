import os
import subprocess
from esc.codegen import CodeGenerator
from esc.parser import Parser

# TODO: If release
# import sys
# sys.tracebacklimit = 0

if __name__ == '__main__':
    p = Parser()
    c = CodeGenerator()

    statements = p.parse('''
                        sub bla(n)
                            if(n = 5) then
                                print("n = 5!")
                                return
                            else
                                print("n =! 5")
                            endif
                        endsub
                        
                        let a = 0
                        repeat
                            bla(a)
                            a = a + 1
                        until a = 10
                        print("after subroutine ")
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
