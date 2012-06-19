__all__ = ["TokenizerException", "Scanner", "make_scanner", "token_line_col"]

import re
from itertools import chain

# Code adapted from an answer at stackoverflow.com
# (url split in 2 to please pep8)
#http://stackoverflow.com/questions/2358890
#/python-lexical-analysis-and-tokenization


def token_line_col(text, tok):
    """Converts the token offset into (line, column) position.
    First character is at position (1, 1)."""
    line = text.count('\n', 0, tok[2]) + 1
    offset = text.rfind('\n', 0, tok[2])
    if offset == -1:
        column = tok[2] + 1
    else:
        column = tok[2] - offset
    return line, column


class TokenizerException(Exception):
    pass


#def tokenize_iter(text, token_re, discard):
#    pos = 0
#    states = [None]
#    while True:
#        m = token_re.match(text, pos)
#        if not m:
#            break
#        pos = m.end()
#        tokname = m.lastgroup
#        try:
#            tokvalue = m.group(tokname)
#        except IndexError, ie:
#            print "No such group", tokname
#        tokpos = m.start()
#        if (tokname not in discard[states[-1]]['discard_names']
#                and tokvalue not in discard[states[-1]]['discard_values']):
#            yield tokname, tokvalue, tokpos
#    if pos != len(text):
#        msg = 'tokenizer stopped at pos %r of %r in "%s" at "%s"' % (
#                pos, len(text), text, text[pos:pos + 3])
#        raise TokenizerException(msg)
# End of adapted code


check_groups = re.compile('[(][?]P=(\w+)[)]')


class Scanner(object):

    def __init__(self, **tokens):
        self.re = re.compile('')
        self.tokens = {}
        self.state_enter = {}
        self.state_leave = {}
        self.state_discard = {None: {'discard_names': set(),
                                     'discard_values': set()}}
        #self.discard_names = set()
        #self.discard_values = set()
        self.add(**tokens)

    def add(self, **tokens):
        """Each named keyword is a token type and its value is the
        corresponding regular expression. Returns a function that iterates
        tokens in the form (type, value) over a string.

        Special keywords are discard_names and discard_values, which specify
        lists (actually any iterable is accepted) containing tokens names or
        values that must be discarded from the scanner output.
        """
        for d in ('discard_values', 'discard_names'):
            if d in tokens:
                for s in self.state_discard:
                    self.state_discard[s][d].update(tokens[d])
                del tokens[d]

#        if 'discard_names' in tokens:
#            #self.discard_names.update(tokens['discard_names'])
#            for s in self.state_discard:
#                self.state_discard[s].update(tokens['discard_names'])
#            del tokens['discard_names']
#        if 'discard_values' in tokens:
#            #self.discard_values.update(tokens['discard_values'])
#            for s in self.state_discard:
#                self.state_discard[s].update(tokens['discard_values'])
#            del tokens['discard_values']

        # Check there is no undefined group in an assertion
        for k, v in tokens.iteritems():
            bad_groups = filter(lambda g: g not in tokens,
                                check_groups.findall(v))
            if bad_groups:
                print "Unknown groups", bad_groups
        pattern_gen = ('(?P<%s>%s)' % (k, v) for k, v in tokens.iteritems())
        if self.re.pattern:
            pattern_gen = chain((self.re.pattern,), pattern_gen)
        self.re = re.compile('|'.join(pattern_gen), re.VERBOSE | re.MULTILINE)
        self.tokens.update(tokens)
        return self

    def state(self, state_name, enter_tokens, leave_tokens, **discard):
        for tok in enter_tokens:
            self.state_enter[tok] = state_name
        for tok in leave_tokens:
            self.state_leave[tok] = state_name
        self.state_discard[state_name] = {'discard_names': set(),
                                          'discard_values': set()}
        for d in ('discard_values', 'discard_names'):
            if d in discard:
                self.state_discard[state_name][d].update(discard[d])
            self.state_discard[state_name][d].update(
                    self.state_discard[None][d])
        #print "state enter:", self.state_enter
        #print "state leave:", self.state_leave
        #print "current discards:", self.state_discard
        return self

    def must_publish_token(self, state, tokname, tokvalue):
        return (tokname not in self.state_discard[state]['discard_names']
                and
                tokvalue not in self.state_discard[state]['discard_values'])

    def __call__(self, text):
        "Iteratively scans through text and yield each token"
        # Code adapted from an answer at stackoverflow.com
        # (url split in 2 to please pep8)
        #http://stackoverflow.com/questions/2358890
        #/python-lexical-analysis-and-tokenization
        pos = 0
        states = [None]
        while True:
            m = self.re.match(text, pos)
            if not m:
                break
            pos = m.end()
            tokname = m.lastgroup
            try:
                tokvalue = m.group(tokname)
            except IndexError, ie:
                print "No such group", tokname
            tokpos = m.start()
            if (tokname in self.state_leave
                    and states[-1] == self.state_leave[tokname]):
                #print "leaving state", states[-1]
                states.pop()
            if tokname in self.state_enter:
                states.append(self.state_enter[tokname])
                #print "entering state", states[-1]
            if self.must_publish_token(states[-1], tokname, tokvalue):
                yield tokname, tokvalue, tokpos
        if pos != len(text):
            msg = 'tokenizer stopped at pos %r of %r in "%s" at "%s"' % (
                    pos, len(text), text, text[pos:pos + 3])
            raise TokenizerException(msg)
#        return tokenize_iter(text, self.re,
#                             self.state_discard)
#                             #self.discard_names, self.discard_values)


def make_scanner(**tokens):
    return Scanner(**tokens)
