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


def tokenize_iter(text, token_re, discard_names={}, discard_values={}):
    pos = 0
    while True:
        m = token_re.match(text, pos)
        if not m:
            break
        pos = m.end()
        tokname = m.lastgroup
        try:
            tokvalue = m.group(tokname)
        except IndexError, ie:
            print "No such group", tokname
        tokpos = m.start()
        if tokname not in discard_names and tokvalue not in discard_values:
            yield tokname, tokvalue, tokpos
    if pos != len(text):
        msg = 'tokenizer stopped at pos %r of %r in "%s" at "%s"' % (
                pos, len(text), text, text[pos:pos + 3])
        raise TokenizerException(msg)
# End of adapted code


check_groups = re.compile('[(][?]P=(\w+)[)]')


class Scanner(object):

    def __init__(self, **tokens):
        self.re = re.compile('')
        self.tokens = {}
        self.discard_names = set()
        self.discard_values = set()
        self.add(**tokens)

    def add(self, **tokens):
        """Each named keyword is a token type and its value is the
        corresponding regular expression. Returns a function that iterates
        tokens in the form (type, value) over a string.

        Special keywords are discard_names and discard_values, which specify
        lists (actually any iterable is accepted) containing tokens names or
        values that must be discarded from the scanner output.
        """
        if 'discard_names' in tokens:
            self.discard_names.update(tokens['discard_names'])
            del tokens['discard_names']
        if 'discard_values' in tokens:
            self.discard_values.update(tokens['discard_values'])
            del tokens['discard_values']
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

    def __call__(self, text):
        "Iteratively scans through text and yield each token"
        return tokenize_iter(text, self.re,
                             self.discard_names, self.discard_values)


def make_scanner(**tokens):
    return Scanner(**tokens)
