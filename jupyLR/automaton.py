__all__ = ['Automaton']

from parser import parser
from itertools import ifilter, chain
from stack import stack


class Automaton(parser):

    def __init__(self, start_sym, grammar, scanner):
        parser.__init__(self, start_sym, grammar)
        self.scanner = scanner

    def validate_ast(self, ast):
        """Overload this method in subclasses to discriminate semantically
        invalid ASTs on the fly.
        """
        return True

    def recognize(self, token_stream):
        S = stack(self)
        #toki = iter(token_stream)
        S.shift(None, None, 0)
        S.count_active = 1
        for cur_tok in token_stream:
            if len(S.active) == 0:
                break
            # Reduce phase
            for i, node in S.enumerate_active():  # S.active may grow
                state = node.data
                for r, rule in ifilter(lambda x: x[0] == 'R',
                                       self.ACTION[state][cur_tok[0]]):
                    S.reduce(node, rule)
                i += 1
            # Shift phase
            todo = []
            for node in S.active:  # S.active MUST NOT grow
                state = node.data
                for r, state in ifilter(lambda x: x[0] == 'S',
                                       self.ACTION[state][cur_tok[0]]):
                    todo.append((node, cur_tok, state))
            reduce(lambda a, b: S.shift(b[0], (b[1],), b[2]), todo, None)
            # Merge states
            S.merge()
            # Check if there are accepting states, and return their outputs
            if cur_tok == ('$', '$'):
                acc = S.accepts()
                if acc:
                    return acc
        return None

    def __call__(self, text):
        return self.recognize(chain(self.scanner(text), [('$', '$')]))
