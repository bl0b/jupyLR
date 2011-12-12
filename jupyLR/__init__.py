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
            print id(output), 'S%-3i' % next_state, output

    def reduce_hook(self, output, ruleidx):
        return self._output(output, ruleidx)

    def _make_ast(self, output, rule):
        # FIXME: this last output token is the result of bad design.
        # FIXME: it's actually the NEXT TOKEN that the parser currently sees,
        # FIXME: not the lastly consumed token.
        top = output and output.pop() or None
        name, elems, commit = self.R[rule]
        if len(output) < len(elems):
            return False
        slc = - len(elems)
        if commit:
            ast = (tuple(chain([name], output[slc:])),)
            ok = self.ast_validator(ast[0])
        else:
            ast = output[slc:]
            ok = True
        if ok:
            del output[slc:]
            output.append(tuple(chain(*ast)))
            top is not None and output.append(top)
            print id(output), 'R%-3i' % rule, output
        return ok

    def __call__(self, text, build_ast=False):
        self.shift_tokens = build_ast
        if build_ast:
            self.ii = 0
            self.ai = 0
            self._output = self._make_ast
        else:
            self._output = lambda output, rule: output.append(rule) or True
        return self.recognize(chain(self.scanner(text), [('$', '$')]))
