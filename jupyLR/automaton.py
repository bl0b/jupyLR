from parser import parser
from itertools import chain, ifilter


class stack_item(object):
    def __init__(self, prev, x):
        self.prev = prev
        self.data = x

    def __str__(self):
        return "stack_item<%s>" % str(self.data)

    __repr__ = __str__


class stack(object):
    def __init__(self, A):
        self.active = []
        self.A = A
        self.count_active = 0

    def enumerate_active(self):
        i = 0
        while i < len(self.active):
            yield i, self.active[i]
            i += 1

    def shift(self, source, token, state):
        sit = stack_item([source], token)
        sis = stack_item([sit], state)
        self.active.append(sis)

    def rec_path(self, node, n):
        if n == -1:
            return [[]]
        if not node.prev:
            return None
        ret = [path for prev in node.prev
               for path in self.rec_path(prev, n - 1)
               if path is not None]
        return ret

    def reduce(self, node, ruleidx):
        name, elems, commit = self.A.R[ruleidx]
        pathes = self.rec_path(node, len(elems) * 2)
        print "---------------------------------"
        print '\n'.join(map(str, pathes))
        print "================================="
        for path in pathes:
            tokens = path[1::2]
            if commit:
                ast = (tuple(chain([name], tokens)),)
                ok = self.A.validate_ast(ast)
            else:
                ast = tokens
                ok = True
            if ok:
                goto = self.A.ACTION[path[0].data][name]
                self.shift(path[0], ast, goto)

    def merge(self):
        merged_s = {}
        for node in self.active[self.count_active:]:
            state = node.data
            if state in merged_s:
                merged_s[state].prev.extend(node.prev)
            else:
                merged_s[state] = node
        self.active = merged_s.values()
        self.count_active = len(self.active)

    def accepts(self):
        AC = self.A.ACTION
        return [output for state, output in self.active
                       if AC[state]['$'] and AC[state]['$'][0] == 'A']


class Automaton(parser):

    def validate_ast(self, ast):
        return True

    def recognize(self, token_stream):
        S = stack(self)
        toki = iter(token_stream)
        S.shift(None, toki.next(), 0)
        for cur_tok in token_stream:
            print S.active
            if len(S.active) == 0:
                return None
            if cur_tok == ('$', '$'):
                return S.accepts()
            # Reduce phase
            for i, node in S.enumerate_active():
                state = node.data
                for r, rule in ifilter(lambda x: x[0] == 'R',
                                       self.ACTION[state][cur_tok[0]]):
                    S.reduce(node, rule)
                i += 1
            # Shift phase
            for i, node in S.enumerate_active():
                state = node.data
                for r, state in ifilter(lambda x: x[0] == 'S',
                                       self.ACTION[state][cur_tok[0]]):
                    S.shift(node, cur_tok, state)
                i += 1
            # Merge states
            S.merge()
