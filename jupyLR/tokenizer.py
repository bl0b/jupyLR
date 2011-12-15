__all__ = ["TokenizerException", "Scanner", "make_scanner"]

import re
from itertools import chain

# Code adapted from an answer at stackoverflow.com
# (url split in 2 to please pep8)
#http://stackoverflow.com/questions/2358890
#/python-lexical-analysis-and-tokenization


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
        tokvalue = m.group(tokname)
        if tokname not in discard_names and tokvalue not in discard_values:
            yield tokname, tokvalue
    if pos != len(text):
        msg = 'tokenizer stopped at pos %r of %r in "%s" at "%s"' % (
                pos, len(text), text, text[pos:pos + 3])
        raise TokenizerException(msg)
# End of adapted code


class Scanner(object):

    def __init__(self, **tokens):
        """Each named keyword is a token type and its value is the
        corresponding regular expression. Returns a function that iterates
        tokens in the form (type, value) over a string.

        Special keywords are discard_names and discard_values, which specify
        lists (actually any iterable is accepted) containing tokens names or
        values that must be discarded from the scanner output.
        """
        if 'discard_names' in tokens:
            self.discard_names = set(tokens['discard_names'])
            del tokens['discard_names']
        else:
            self.discard_names = []
        if 'discard_values' in tokens:
            self.discard_values = set(tokens['discard_values'])
            del tokens['discard_values']
        else:
            self.discard_values = []
        self.re = re.compile('|'.join('(?P<%s>%s)' % (k, v)
                             for k, v in tokens.iteritems()), re.VERBOSE)
        self.tokens = tokens

    def __call__(self, text):
        "Iteratively scans through text and yield each token"
        return tokenize_iter(text, self.re,
                             self.discard_names, self.discard_values)


def make_scanner(**tokens):
    return Scanner(**tokens)
