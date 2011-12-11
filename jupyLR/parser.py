from tokenizer import tokenize_iter
import re
from itertools import ifilter, izip, chain, imap
from tokenizer import make_scanner
from lr import *

lr_grammar_scanner = make_scanner(
    sep='=', word=r"\b\w+\b", whitespace=r'[ \t\r\n]+',
    discard_names=('whitespace',))


def rules(start, grammar, kw):
    words = [start]
    edit_rule = '@'
    kw.add(edit_rule)
    for tokname, tokvalue in lr_grammar_scanner(grammar):
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
    counter = 0
    for rulename, elems in rules:
        if rulename not in ret:
            ret[rulename] = []
        rule = (rulename, elems)
        ret[rulename].append(counter)
        ret[counter] = rule
        counter += 1
    return ret, counter


class parser(object):

    def __init__(self, start_sym, grammar):
        self.kw_set = set()
        self.kw_set.add('$')
        self.R, counter = ruleset(rules(start_sym, grammar, self.kw_set))
        self.I = set((r, i) for r in xrange(counter)
                            for i in xrange(len(self.R[r][1]) + 1))
        self.compute_lr0()
        self.LR0 = list(sorted(self.LR0))
        self.LR0_idx = {}
        for i, s in enumerate(self.LR0):
            self.LR0_idx[s] = i
        self.initial_state = self.index(self.initial_items)
        self.compute_ACTION()

    def compute_lr0(self):
        self.LR0 = set()
        x = closure([(0, 0)], self.R)
        self.initial_items = x
        stack = [tuple(sorted(x))]
        while stack:
            x = stack.pop()
            print "set", x
            self.LR0.add(x)
            F = follow(x, self.R)
            for t, s in F.iteritems():
                s = tuple(sorted(s))
                if s not in self.LR0:
                    stack.append(s)

    def itemstr(self, item):
        return itemstr(item, self.R)

    def itemsetstr(self, item, label=''):
        return itemsetstr(item, self.R, label)

    def closure(self, s):
        return tuple(sorted(closure(s, self.R)))

    def kernel(self, s):
        return kernel(s, self.R)

    def index(self, s):
        return self.LR0_idx[self.closure(s)]

    def compute_GOTO(self):
        self.GOTO = []
        for s in self.LR0:
            f = {}
            for tok, dest in follow(s, self.R).iteritems():
                f[tok] = self.LR0_idx[self.closure(dest)]
            self.GOTO.append(f)

    def init_row(self, init=None):
        if init is None:
            init = []
        ret = {}
        for kw in self.kw_set:
            ret[kw] = [] + init
        return ret

    def next_items(self, item):
        items = []
        name = self.R[item[0]][0]
        for r, e, i, n in expand_itemset2(self.I, self.R):
            if i > 0 and e[i - 1] == name:
                if len(e) == i:
                    items.extend(self.next_items((r, i)))
                else:
                    items.append((r, i))
        return items

    def following_tokens(self, item):
        items = self.next_items(item)
        print self.itemstr(item)
        print self.itemsetstr(items)
        ret = first(closure(items, self.R), self.R)
        ret.add('$')
        print ret
        return ret

    def compute_ACTION(self):
        self.compute_GOTO()
        self.ACTION = []
        for s, g in izip(self.LR0, self.GOTO):
            action = self.init_row()
            # reductions
            for r, i in ifilter(lambda (r, i): i == len(self.R[r][1]), s):
                if not r:
                    action['$'].append(('A',))
                else:
                    for kw in self.following_tokens((r, i)):
                    #for kw in self.kw_set:
                        action[kw].append(('R', r))
            # transitions
            for tok, dest in g.iteritems():
                action[tok].append(('S', dest))
            # commit
            self.ACTION.append(action)
        # now show how proud we are of the pretty-print
        print self.action_to_str()

    def action_to_str(self):

        def ac_str(c):
            return ''.join(imap(str, c))

        def cell(i, kw):
            if i >= 0:
                return ','.join(map(ac_str, self.ACTION[i][kw]))
            if i < 0:
                return kw != '@' and str(kw) or ''

        def col_width(kw):
            return reduce(max, chain([type(kw) is str and len(kw) or kw],
                                     (len(cell(i, kw))
                                      for i in xrange(len(self.ACTION)))))

        col_labels = sorted(self.kw_set,
                            key=lambda x: x in self.R and '|' + x
                                          or x == '$' and '|$'
                                          or x)
        col_widths = [kw != '@' and col_width(kw) or 0 for kw in col_labels]

        def row(i):
            return ' | '.join(cell(i, kw).center(cw)
                              for kw, cw in izip(col_labels, col_widths))

        header = '    | ' + row(-1) + '\n'
        return header + '\n'.join(('%3i | ' % i) + row(i)
                                  for i in xrange(len(self.ACTION)))

    def dump_sets(self):
        for i, lrset in enumerate(self.LR0):
            print self.itemsetstr(lrset, i)
            print
#
