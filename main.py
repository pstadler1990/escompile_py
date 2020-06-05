import os
import subprocess
from esc.codegen import CodeGenerator
from esc.parser import Parser

if __name__ == '__main__':
    p = Parser()
    c = CodeGenerator()

    statements = p.parse('''
                        let i = 1
                        repeat
                            if(i mod 3 = 0 and i mod 5 = 0) then
                                print("FizzBuzz")
                            elseif(i mod 3 = 0) then
                                print("Fizz")
                            elseif(i mod 5 = 0) then
                                print("Buzz")
                            else
                                print("" + i)
                            endif
                            
                            if(i >= 100) then
                                exit
                            endif
                            i = i + 1
                        forever
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
