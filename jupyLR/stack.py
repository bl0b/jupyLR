__all__ = ['stack_item', 'stack']

from parser import parser
from itertools import chain, ifilter


def printlist(l, pfx):
    print pfx + ('\n' + pfx).join(map(str, l))


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
        self.previously_active = []

    def enumerate_active(self):
        i = 0
        while i < len(self.active):
            yield i, self.active[i]
            i += 1

    def shift(self, source, token, state):
        #printlist(self.rec_all_pathes(source), "before shift: ")
        sit = stack_item([source], token)
        sis = stack_item([sit], state)
        self.active.append(sis)
        #printlist(self.rec_all_pathes(sis), "after shift: ")
        #print "shift", source, token, state, self.active

    def rec_path(self, node, n):
        #print "rec_path(%s, %s)" % (str(node), str(n))
        if n == 0:
            return [[node]]
        if not node.prev:
            return None
        ret = [path.append(node.data) or path
               for prev in node.prev
               for path in self.rec_path(prev, n - 1)
               if path is not None]
        return ret

    def rec_all_pathes(self, node):
        if node is None:
            return [[]]
        ret = [path.append(node.data) or path
               for prev in node.prev
               for path in self.rec_all_pathes(prev)]
        return ret

    def reduce(self, node, ruleidx):
        name, elems, commit = self.A.R[ruleidx]
        pathes = self.rec_path(node, len(elems) * 2)
        #print "---------------------------------"
        #print 'R'+'\nR'.join(map(str, pathes))
        #print "================================="
        tokenlists = set()
        for path in pathes:
            tokenlists.add(tuple(e for el in path[1::2] for e in el))
        for tokens in tokenlists:
            if commit:
                ast = (tuple(chain([name], tokens)),)
                ok = self.A.validate_ast(ast[0])
            else:
                ast = tokens
                ok = True
            if ok:
                goto = self.A.ACTION[path[0].data][name]
                #print goto
                self.shift(path[0], ast, goto[0][1])

    def merge(self):
        merged_s = {}
        self.previously_active = self.active[:self.count_active]
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
        is_accepting = lambda state: len(AC[state]['$']) > 0 \
                                     and AC[state]['$'][0][0] == 'A'
        # Ast's are always encapsulated inside a 1-uple. We don't want that
        # in the output. Hence the [0].
        return [path[-2][0] for node in self.active
                             if is_accepting(node.data)
                            for path in self.rec_all_pathes(node)
                             if len(path) == 4]
                            # length 4 being
                            # (None, initial_state, AST, accepting_state)
                            # we want the AST, hence the [-2].
