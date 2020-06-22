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
                        func sum(n)
                            if(n != 0) then
                                return n + sum(n - 1)
                            else    
                                return n
                            endif
                        endfunc 
                        
                        print("sum: " + sum(3))
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
