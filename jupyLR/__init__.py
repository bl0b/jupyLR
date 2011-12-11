__all__ = ['lr', 'Slr', 'make_scanner']

import lr
from tokenizer import make_scanner
from itertools import chain, tee, imap
from automaton import Automaton


class Slr(Automaton):

    def __init__(self, start_sym, grammar, scanner):
        Automaton.__init__(self, start_sym, grammar)
        self.scanner = scanner
        # TODO : check keyword sets coherence (partition)

    def shift(self, next_state):
        Automaton.shift(self, next_state)
        self.ast.append(self.input)
        print self.ast

    def reduce(self, ruleidx):
        if self._output(ruleidx):
            Automaton.reduce(self, ruleidx)
            return True
        return False

    def _make_ast(self, rule):
        top = self.ast.pop()
        name, elems = self.R[rule]
        ast = tuple(chain([name], self.ast[-len(elems):]))
        self.ast = self.ast[:-len(elems)]
        self.ast.append(ast)
        self.ast.append(top)
        print self.ast
        return True

    def __call__(self, text, build_ast=False):
        self.ast = []
        mk_scan = lambda n: tee(chain(self.scanner(text), [('$', '$')]), n)
        if build_ast:
            self.ii = 0
            self.ai = 0
            self.scan_iter = mk_scan(2)
            outfunc = self._make_ast
        else:
            self.scan_iter = mk_scan(1)

            def outfunc(rule, inp):
                self.ast.append(rule)
                return True
        self._output = outfunc
        ok = self.recognize(self.scan_iter[0])
        return ok, self.ast
