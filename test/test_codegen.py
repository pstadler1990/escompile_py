import os
import subprocess
import unittest

from esc.codegen import CodeGenerator
from esc.parser import Parser


class TestCodegen(unittest.TestCase):

    def test_func_doubler(self):
        p = Parser()
        c = CodeGenerator()
        statements = p.parse('''
                            func my_func(a)
                                return a * 2
                            endfunc
                            
                            print("result: " + my_func(4))
                            ''')

        for statement in statements:
            c.generate(statement)

        fbytes = c.finalize()

        # CALL vm.exe with bytes_out -b option
        sub = subprocess.Popen(
            ["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system('taskkill /f /im es_vm.exe')
        out, err = sub.communicate()
        lines = [s.decode("utf-8") for s in out.splitlines()[1:]]
        self.assertTrue(lines[0] == 'result: 8.000000')

    def test_array_iteration(self):
        p = Parser()
        c = CodeGenerator()
        statements = p.parse('''
                            let i = [1, 1+1, 3, 42.69]
                            let j = 0
                            repeat
                                print("i: " + i[j])
                                j = j + 1
                            until j = 4
                            ''')

        for statement in statements:
            c.generate(statement)

        fbytes = c.finalize()

        # CALL vm.exe with bytes_out -b option
        sub = subprocess.Popen(
            ["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system('taskkill /f /im es_vm.exe')
        out, err = sub.communicate()
        lines = [s.decode("utf-8") for s in out.splitlines()[1:]]
        self.assertTrue(lines[0] == 'i: 1.000000')
        self.assertTrue(lines[1] == 'i: 2.000000')
        self.assertTrue(lines[2] == 'i: 3.000000')
        self.assertTrue(lines[3] == 'i: 42.690000')

    def test_array_change_iteration(self):
        p = Parser()
        c = CodeGenerator()
        statements = p.parse('''
                            let a = [0, 0, 0, 0]
                            let i = 0
                            repeat
                                a[i] = i
                                print("i after: " + a[i])
                                i = i + 1
                            until i = 4
                            ''')

        for statement in statements:
            c.generate(statement)

        fbytes = c.finalize()

        # CALL vm.exe with bytes_out -b option
        sub = subprocess.Popen(
            ["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system('taskkill /f /im es_vm.exe')
        out, err = sub.communicate()
        lines = [s.decode("utf-8") for s in out.splitlines()[1:]]
        self.assertTrue(lines[0] == 'i after: 0.000000')
        self.assertTrue(lines[1] == 'i after: 1.000000')
        self.assertTrue(lines[2] == 'i after: 2.000000')
        self.assertTrue(lines[3] == 'i after: 3.000000')

    def test_ifelseifelse(self):
        p = Parser()
        c = CodeGenerator()
        statements = p.parse('''
                            let a = 42
                            if(a = 42) then
                                print("a is 42")
                            elseif(a = 43) then
                                print("a is 43")
                            elseif(a = 44) then
                                print("a is 44")
                            else
                                print("a is something else")
                            endif
                            
                            a = 43
                            if(a = 42) then
                                print("a is 42")
                            elseif(a = 43) then
                                print("a is 43")
                            elseif(a = 44) then
                                print("a is 44")
                            else
                                print("a is something else")
                            endif
                            
                            a = 44
                            if(a = 42) then
                                print("a is 42")
                            elseif(a = 43) then
                                print("a is 43")
                            elseif(a = 44) then
                                print("a is 44")
                            else
                                print("a is something else")
                            endif
                            
                            a = 45
                            if(a = 42) then
                                print("a is 42")
                            elseif(a = 43) then
                                print("a is 43")
                            elseif(a = 44) then
                                print("a is 44")
                            else
                                print("a is something else")
                            endif
                            ''')

        for statement in statements:
            c.generate(statement)

        fbytes = c.finalize()

        # CALL vm.exe with bytes_out -b option
        sub = subprocess.Popen(
            ["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system('taskkill /f /im es_vm.exe')
        out, err = sub.communicate()
        lines = [s.decode("utf-8") for s in out.splitlines()[1:]]
        self.assertTrue(lines[0] == 'a is 42')
        self.assertTrue(lines[1] == 'a is 43')
        self.assertTrue(lines[2] == 'a is 44')
        self.assertTrue(lines[3] == 'a is something else')

    def test_sub_jump(self):
        p = Parser()
        c = CodeGenerator()
        statements = p.parse('''
                            sub count_to_zero(param)
                                repeat
                                    print("" + param)
                                    param = param - 1
                                until param = 0
                            endsub
                            
                            print("Now jump into the procedure")
                            count_to_zero(5)
                            ''')

        for statement in statements:
            c.generate(statement)

        fbytes = c.finalize()

        # CALL vm.exe with bytes_out -b option
        sub = subprocess.Popen(
            ["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system('taskkill /f /im es_vm.exe')
        out, err = sub.communicate()
        lines = [s.decode("utf-8") for s in out.splitlines()[1:]]
        self.assertTrue(lines[0] == 'Now jump into the procedure')
        self.assertTrue(lines[1] == '5.000000')
        self.assertTrue(lines[2] == '4.000000')
        self.assertTrue(lines[3] == '3.000000')
        self.assertTrue(lines[4] == '2.000000')
        self.assertTrue(lines[5] == '1.000000')

    def test_recursive_print(self):
        p = Parser()
        c = CodeGenerator()
        statements = p.parse('''
                            sub my_print(str, n)
                                if(n > 1) then
                                    my_print(str, n - 1)
                                endif
                                print(str)
                            endsub
                            
                            my_print("Hello", 5)
                            ''')

        for statement in statements:
            c.generate(statement)

        fbytes = c.finalize()

        # CALL vm.exe with bytes_out -b option
        sub = subprocess.Popen(
            ["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system('taskkill /f /im es_vm.exe')
        out, err = sub.communicate()
        lines = [s.decode("utf-8") for s in out.splitlines()[1:]]
        for ln in lines:
            self.assertTrue(ln == 'Hello')

    def test_sub_return(self):
        p = Parser()
        c = CodeGenerator()
        statements = p.parse('''
                             sub bla
                                print("before return statement")
                                return
                                print("this will never be executed")
                            endsub
                            
                            bla()
                            print("after subroutine")
                                ''')

        for statement in statements:
            c.generate(statement)

        fbytes = c.finalize()

        # CALL vm.exe with bytes_out -b option
        sub = subprocess.Popen(
            ["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system('taskkill /f /im es_vm.exe')
        out, err = sub.communicate()
        lines = [s.decode("utf-8") for s in out.splitlines()[1:]]
        self.assertTrue(lines[0] == 'before return statement')
        self.assertTrue(lines[1] == 'after subroutine')

    def test_recursive_factorial(self):
        p = Parser()
        c = CodeGenerator()
        statements = p.parse('''
                             func fact(n)
                                if(n <= 1) then
                                    return 1
                                else    
                                    return n * fact(n-1)
                                endif  
                            endfunc
                            
                            print("10! = " + fact(10))
                            ''')

        for statement in statements:
            c.generate(statement)

        fbytes = c.finalize()

        # CALL vm.exe with bytes_out -b option
        sub = subprocess.Popen(
            ["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system('taskkill /f /im es_vm.exe')
        out, err = sub.communicate()
        lines = [s.decode("utf-8") for s in out.splitlines()[1:]]
        self.assertTrue(lines[0] == '10! = 3628800.000000')

    def test_recursive_pow(self):
        p = Parser()
        c = CodeGenerator()
        statements = p.parse('''
                             func pow(x, n)
                                if(n = 1) then
                                    return x
                                else
                                    return x * pow(x, n - 1)
                                endif
                            endfunc
                            
                            let x = 2
                            let y = 8
                            print("pow " + x + "^" + y + " -> " + pow(x, y))
                            ''')

        for statement in statements:
            c.generate(statement)

        fbytes = c.finalize()

        # CALL vm.exe with bytes_out -b option
        sub = subprocess.Popen(
            ["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system('taskkill /f /im es_vm.exe')
        out, err = sub.communicate()
        lines = [s.decode("utf-8") for s in out.splitlines()[1:]]
        self.assertTrue(lines[0] == 'pow 2.000000^8.000000 -> 256.000000')

    def test_recursive_fibonacci(self):
        p = Parser()
        c = CodeGenerator()
        statements = p.parse('''
                             func fib(n)
                                if(n < 2) then
                                    return n
                                endif
                                return fib(n - 2) + fib(n - 1)
                            endfunc
                            
                            print("a: " + fib(15))
                            ''')

        for statement in statements:
            c.generate(statement)

        fbytes = c.finalize()

        # CALL vm.exe with bytes_out -b option
        sub = subprocess.Popen(
            ["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system('taskkill /f /im es_vm.exe')
        out, err = sub.communicate()
        lines = [s.decode("utf-8") for s in out.splitlines()[1:]]
        self.assertTrue(lines[0] == 'a: 610.000000')

    def test_recursive_func_calls(self):
        p = Parser()
        c = CodeGenerator()
        statements = p.parse('''
                             func blub(n)
                                print("n is now: " + n)
                                let a = n * 2
                                return a
                            endfunc
                            
                            func bla(n)
                                let m = 99
                                print("n: " + n + " m: " + m)
                                blub(n)
                            endfunc
                            
                            print("result: " + bla(10))
                            ''')

        for statement in statements:
            c.generate(statement)

        fbytes = c.finalize()

        # CALL vm.exe with bytes_out -b option
        sub = subprocess.Popen(
            ["C:\\Users\\patrick.stadler\\CLionProjects\\es_vm\\cmake-build-debug\\es_vm.exe", "-b"] + fbytes,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        os.system('taskkill /f /im es_vm.exe')
        out, err = sub.communicate()
        lines = [s.decode("utf-8") for s in out.splitlines()[1:]]
        self.assertTrue(lines[0] == 'n: 10.000000 m: 99.000000')
        self.assertTrue(lines[1] == 'n is now: 10.000000')
        self.assertTrue(lines[2] == 'result: 20.000000')