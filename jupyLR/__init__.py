__all__ = ['Slr', 'make_scanner']

import lr
from tokenizer import make_scanner
from itertools import chain, tee, imap, izip_longest
from automaton import Automaton


class Slr(Automaton):

    def __init__(self, start_sym, grammar, scanner,
                 ast_validator=lambda ast: True):
        Automaton.__init__(self, start_sym, grammar)
        self.scanner = scanner
        self.ast_validator = ast_validator
        # TODO : check keyword sets coherence (partition)

    def shift_hook(self, outputs, next_state):
        for output in outputs:
            output.append(self.input)
        print id(outputs), 'S%-3i' % next_state, outputs

    def reduce_hook(self, outputs, ruleidx):
        to_remove = []
        for i, output in enumerate(outputs):
            if not self._make_ast(output, ruleidx):
                to_remove.append(i)
        for i in reversed(to_remove):
            del outputs[i]
        return len(outputs) > 0

    def _make_ast(self, output, rule):
        # FIXME: this last output token is the result of bad design.
        # FIXME: it's actually the NEXT TOKEN that the parser currently sees,
        # FIXME: not the lastly consumed token.

        top = output and output.pop() or None
        name, elems, commit = self.R[rule]
        print "reduce", name, elems, commit
        slc = - len(elems)
        # FIXME: is it enough to just test length ?
        #if len(output) < len(elems):
        #    return False
        all_same = reduce(lambda a, b: a and b[0][0] == b[1][0],
                          izip_longest(output[slc:], elems,
                                       fillvalue=(None,)),
                          True)
        if not all_same:
            return False
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

    def __call__(self, text):
        self.ii = 0
        self.ai = 0
        return self.recognize(chain(self.scanner(text), [('$', '$')]))
