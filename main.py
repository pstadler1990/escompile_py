from esc.codegen import CodeGenerator
from esc.parser import Parser
import subprocess

if __name__ == '__main__':
    p = Parser()
    c = CodeGenerator()

    statements = p.parse('''
                        let a = 0
                        if(a = 0) then
                            print("a is 0")
                        elseif(a = 1) then
                            print("a is 1")
                        elseif(a = 2) then
                            print("a is 2")
                        else
                            print("else path")
                        endif
                        print("--- END ---")
                        '''
                         )
    for statement in statements:
        c.generate(statement)

    print(c.bytes_out)
    print(c.format())
    fbytes = c.finalize()

    # CALL vm.exe with bytes_out -b option
    subprocess.Popen(["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes)
