import unittest
from esc.parser import Parser, ProcSubNode
from esc.scanner import TokenType


class TestParser(unittest.TestCase):

    def test_proc_sub_define_3_args(self):
        p = Parser()
        statements = p.parse('''
                                sub my_sub(a, b, c)
                                    print("Hello from my procedure")
                                endsub
                                '''
                             )
        self.assertIsInstance(statements[0], ProcSubNode)
        self.assertTrue(len(statements[0].args) == 3)
        self.assertTrue(statements[0].left.ttype == TokenType.IDENTIFIER)
        self.assertTrue(statements[0].left)

    def test_proc_sub_define_0_args_parents(self):
        p = Parser()
        statements = p.parse('''
                                sub my_sub()
                                    print("Hello from my procedure")
                                endsub
                                '''
                             )
        self.assertIsInstance(statements[0], ProcSubNode)
        self.assertTrue(len(statements[0].args) == 0)
        self.assertTrue(statements[0].left.ttype == TokenType.IDENTIFIER)
        self.assertTrue(statements[0].left)

    def test_proc_sub_define_0_args(self):
        p = Parser()
        statements = p.parse('''
                                sub my_sub
                                    print("Hello from my procedure")
                                endsub
                                '''
                             )
        self.assertIsInstance(statements[0], ProcSubNode)
        self.assertTrue(len(statements[0].args) == 0)
        self.assertTrue(statements[0].left.ttype == TokenType.IDENTIFIER)
        self.assertTrue(statements[0].left)
