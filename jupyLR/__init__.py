__all__ = ['lr', 'Slr', 'make_scanner']

import lr
from tokenizer import make_scanner
from parser import parser
from itertools import chain


class Slr(parser):

    def __init__(self, start_sym, grammar, scanner):
        parser.__init__(self, start_sym, grammar)
        self.scanner = scanner

    def __call__(self, text):
        return self.recognize(chain(self.scanner(text), [('$', '$')]))
