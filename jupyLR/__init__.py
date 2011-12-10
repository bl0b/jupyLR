__all__ = ['lr', 'make_scanner']

import lr
from tokenizer import make_scanner


def rules(start, grammar, kw):
    words = [start]
    edit_rule = '@'
    kw.add(edit_rule)
    for tokname, tokvalue in tokenize_iter(grammar, token_re):
        if tokname == 'word':
            words.append(tokvalue)
            kw.add(tokvalue)
        elif tokname == 'sep':
            tmp = words.pop()
            yield (edit_rule, tuple(words))
            edit_rule = tmp
            words = []
    yield (edit_rule, tuple(words))


def ruleset(rules):
    ret = {}
    for rulename, elems in rules:
        if rulename not in ret:
            ret[rulename] = []
        ret[rulename].append(elems)
    return ret
