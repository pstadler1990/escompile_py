import unittest
from esc.scanner import Scanner, Token, TokenType, ScanWrongTokenException


class TestScanner(unittest.TestCase):

    def test_single_expression(self):
        scanner = Scanner()
        scanner.scan_str('1+1')
        tok1: Token = scanner.next_token()
        tok2: Token = scanner.next_token()
        tok3: Token = scanner.next_token()
        tok4: Token = scanner.next_token()
        self.assertIsInstance(tok1, Token)
        self.assertIsInstance(tok2, Token)
        self.assertIsInstance(tok3, Token)
        self.assertIsNone(tok4)
        self.assertTrue(tok1.ttype == TokenType.NUMBER)
        self.assertTrue(tok2.ttype == TokenType.PLUS)
        self.assertTrue(tok3.ttype == TokenType.NUMBER)

    def test_numbers(self):
        scanner = Scanner()
        scanner.scan_str('1 42 .3 0.42 42.69 .3.4')
        self.assertTrue(scanner.next_token().value == 1)
        self.assertTrue(scanner.next_token().value == 42)
        self.assertTrue(scanner.next_token().value == .3)
        self.assertTrue(scanner.next_token().value == 0.42)
        self.assertTrue(scanner.next_token().value == 42.69)
        self.assertRaises(ScanWrongTokenException, lambda: scanner.next_token())

    def test_strings(self):
        scanner = Scanner()
        scanner.scan_str('"Hello World" "A very very very very very very very very long string" "This should" fail"')
        self.assertTrue(len(str(scanner.next_token().value)) == 11)
        self.assertTrue(len(str(scanner.next_token().value)) == 53)
        self.assertTrue(len(str(scanner.next_token().value)) == 11)
        self.assertRaises(ScanWrongTokenException, lambda: scanner.next_token())


if __name__ == '__main__':
    unittest.main()
