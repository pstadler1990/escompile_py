from esc.codegen import CodeGenerator
from esc.parser import Parser
import subprocess

if __name__ == '__main__':
    p = Parser()
    c = CodeGenerator()

    statements = p.parse('''
                        let a = 1
                        if(a = 0) then
                            print("a is 0")
                            print("und blibblabblub")
                        elseif(a = 1) then
                            print("a is 1")
                            let b = 22.55
                            let c = b + 2.35678
                            print("c is " + c)
                        elseif(a = 2) then
                            print("a is 2")
                        elseif(a = 42) then
                            print("a is 42")
                        else
                            print("a is was andres")
                        endif
                        print("--- END1 ---")
                        '''
                         )
    for statement in statements:
        c.generate(statement)

    print(c.bytes_out)
    print(c.format())
    fbytes = c.finalize()

    # CALL vm.exe with bytes_out -b option
    subprocess.Popen(["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes)
