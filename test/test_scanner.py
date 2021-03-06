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

    def test_hex_number(self):
        scanner = Scanner()
        scanner.scan_str('0xDEAD 0xAFFE 0x55 0 01')
        self.assertTrue(scanner.next_token().value == 57005)
        self.assertTrue(scanner.next_token().value == 45054)
        self.assertTrue(scanner.next_token().value == 85)
        self.assertTrue(scanner.next_token().value == 0)
        self.assertTrue(scanner.next_token().value == 1)

    def test_strings(self):
        scanner = Scanner()
        scanner.scan_str('"Hello World" "A very very very very very very very very long string" "This should"fail"')
        self.assertTrue(len(str(scanner.next_token().value)) == 11)
        self.assertTrue(len(str(scanner.next_token().value)) == 53)
        self.assertTrue(len(str(scanner.next_token().value)) == 11)
        self.assertTrue(scanner.next_token().ttype == TokenType.IDENTIFIER)
        self.assertRaises(ScanWrongTokenException, lambda: scanner.next_token())

    def test_identifiers(self):
        scanner = Scanner()
        scanner.scan_str('let if repeat a ifif elseif elseiff')
        self.assertTrue(scanner.next_token().ttype == TokenType.LET)
        self.assertTrue(scanner.next_token().ttype == TokenType.BLOCK_IF)
        self.assertTrue(scanner.next_token().ttype == TokenType.LOOP_REPEAT)
        self.assertTrue(scanner.next_token().ttype == TokenType.IDENTIFIER)
        self.assertTrue(scanner.next_token().ttype == TokenType.IDENTIFIER)
        self.assertTrue(scanner.next_token().ttype == TokenType.BLOCK_ELSEIF)
        self.assertTrue(scanner.next_token().ttype == TokenType.IDENTIFIER)


if __name__ == '__main__':
    unittest.main()
