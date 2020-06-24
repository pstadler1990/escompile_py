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
                        extern func my_external_func
                        extern func my_external_delay
                        extern func my_external_gpio
                        
                        print("Start of script")
                        repeat
                            my_external_delay(1000)
                            my_external_gpio(1)
                            my_external_delay(1000)
                            my_external_gpio(0)
                            print("loop")
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
