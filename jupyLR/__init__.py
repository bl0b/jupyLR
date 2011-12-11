__all__ = ['lr', 'Slr', 'make_scanner']

import lr
from tokenizer import make_scanner
from itertools import chain, tee, imap
from automaton import Automaton


class Slr(Automaton):

    def __init__(self, start_sym, grammar, scanner,
                 ast_validator=lambda ast: True):
        Automaton.__init__(self, start_sym, grammar)
        self.scanner = scanner
        self.ast_validator = ast_validator
        # TODO : check keyword sets coherence (partition)

    def shift(self, next_state):
        Automaton.shift(self, next_state)
        if self.shift_tokens:
            self.ast.append(self.input)
        print self.ast

    def reduce(self, ruleidx):
        if self._output(ruleidx):
            Automaton.reduce(self, ruleidx)
            return True
        return False

    def _make_ast(self, rule):
        top = self.ast.pop()
        name, elems, commit = self.R[rule]
        if commit:
            ast = (tuple(chain([name], self.ast[-len(elems):])),)
            ok = self.ast_validator(ast[0])
        else:
            ast = self.ast[-len(elems):]
            ok = True
        if ok:
            self.ast = self.ast[:-len(elems)]
            self.ast.append(tuple(chain(*ast)))
            self.ast.append(top)
            print self.ast
        return ok

    def __call__(self, text, build_ast=False):
        self.ast = []
        mk_scan = lambda n: tee(chain(self.scanner(text), [('$', '$')]), n)
        if build_ast:
            self.ii = 0
            self.ai = 0
            self.scan_iter = mk_scan(2)
            outfunc = self._make_ast
            self.shift_tokens = True
        else:
            self.scan_iter = mk_scan(1)
            self.shift_tokens = False

            def outfunc(rule):
                self.ast.append(rule)
                return True
        self._output = outfunc
        ok = self.recognize(self.scan_iter[0])
        return ok, self.ast
