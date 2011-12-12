__all__ = ['Slr', 'make_scanner']

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

    def shift_hook(self, output, next_state):
        if self.shift_tokens:
            output.append(self.input)
            print "current output", output

    def reduce_hook(self, output, ruleidx):
        return self._output(output, ruleidx)

    def _make_ast(self, output, rule):
        print "_make_ast", output, rule
        top = output.pop()
        name, elems, commit = self.R[rule]
        if commit:
            ast = (tuple(chain([name], output[-len(elems):])),)
            ok = self.ast_validator(ast[0])
        else:
            ast = output[-len(elems):]
            ok = True
        if ok:
            del output[:-len(elems)]
            output.append(tuple(chain(*ast)))
            output.append(top)
            print "current output", output
        return ok

    def __call__(self, text, build_ast=False):
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

            def outfunc(output, rule):
                output.append(rule)
                return True
        self._output = outfunc
        return self.recognize(self.scan_iter[0])
