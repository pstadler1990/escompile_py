import os
import subprocess
from esc.codegen import CodeGenerator
from esc.parser import Parser

if __name__ == '__main__':
    p = Parser()
    c = CodeGenerator()

    statements = p.parse('''
                        let a = 0
                        repeat
                            a = a + 1
                            print("a is: " + a)
                            if(a = 400) then
                                print("YEAH YEAH YEAH!!!!")
                                let b = 10
                                repeat
                                    print("inner b: " + b)
                                    b = b + 1
                                    if(b = 50) then
                                        print("EXIT b")
                                        exit
                                    endif
                                forever
                                exit
                            endif
                        forever
                        print("end of inner loops")
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
