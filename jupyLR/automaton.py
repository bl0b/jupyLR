__all__ = ['Automaton']

from parser import parser
from itertools import ifilter, chain
from stack import stack
#from lr import kernel
from tokenizer import token_line_col

INITIAL_TOKEN = ('#', '#', 0)


class Automaton(parser):
    """A GLR parser."""

    def __init__(self, start_sym, grammar, scanner):
        """Construct a GLR automaton given an LR grammar and a start symbol.
        The scanner that creates the automaton input is also provided for
        convenience of use."""
        parser.__init__(self, start_sym, grammar, scanner.tokens.keys())
        self.scanner = scanner

    def validate_ast(self, ast):
        """Overload this method in subclasses to discriminate semantically
        invalid ASTs on the fly.
        """
        return True

    def error_detected(self, cur_tok, last_states):
        """Overload this method in subclasses to implement error recovery
        or notification.
        """
        line, column = token_line_col(self.text, cur_tok)
        print "Error detected at line %i, column %i:" % (line, column)
        #for st in last_states:
        #    print self.itemsetstr(kernel(self.LR0[st.data]))
        #    print "Expected", ', '.join(kw
        #                                for kw in self.kw_set
        #                                if len(self.ACTION[st.data][kw]) > 0)
        print "Expected", ', '.join(kw for st in last_states
                                       for kw in self.kw_set
                                        if len(self.ACTION[st.data][kw]) > 0)
        return False

    def __recognize(self, token_stream):
        """Runs the automaton over an input stream of tokens. For use with the
        output of a Scanner instance. The last token MUST be
        ('$', '$', length_of_text)."""
        S = stack(self)
        #toki = iter(token_stream)
        S.shift(None, None, 0)
        S.count_active = 1
        prev_tok = INITIAL_TOKEN
        for cur_tok in token_stream:
            if len(S.active) == 0:
                if not self.error_detected(prev_tok, S.previously_active):
                    break
                else:
                    continue
            prev_tok = cur_tok
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
            if cur_tok[0] == '$':
                acc = S.accepts()
                if acc:
                    return acc
                else:
                    self.error_detected(cur_tok, S.active)
        return None

    def __call__(self, text):
        """Parse this text and return a list of valid ASTs, if any. On error,
        returns None."""
        self.text = text  # for the sake of the error detection/recovery
        return self.__recognize(chain(self.scanner(text),
                                      [('$', '$', len(self.text))]))
