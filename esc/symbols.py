# Symbol tables
import abc

# Global and local scopes
GLOBAL_SCOPE = 0
NUM_SCOPES = 64


class SymbolEntry(abc.ABC):
    def __init__(self):
        self.value = 0

    def __repr__(self):
        return self.__str__()


class SymbolEntryNumber(SymbolEntry):
    def __init__(self, num_value: float):
        super().__init__()
        self.value = num_value

    def __str__(self):
        return 'Symbol of type NUMBER with value {v}'.format(v=self.value)


class SymbolEntryString(SymbolEntry):
    def __init__(self, str_value: str):
        super().__init__()
        self.value = str_value

    def __str__(self):
        return 'Symbol of type STRING with value \"{v}\"'.format(v=self.value)


class SymbolTable:
    def __init__(self):
        self.symbols = {}

    def __str__(self):
        out_str: str = 'SYMBOL TABLE\n'
        for entry in self.symbols:
            out_str += ('{e}\n'.format(e=self.symbols[entry]))
        return out_str

    def __repr__(self):
        return self.__str__()

    def find_symbol(self, symbol_name: str) -> SymbolEntry:
        symbol: SymbolEntry = self.symbols.get(symbol_name)
        if not symbol:
            raise NameError('Symbol {s} is not defined'.format(s=symbol_name))
        return symbol

    def symbol_exists(self, symbol_name: str) -> bool:
        return self.find_symbol(symbol_name) is not None

    def symbol_add(self, symbol_name: str, entry: SymbolEntry) -> None:
        self.symbols[symbol_name] = entry
