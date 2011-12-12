from parser import parser
from itertools import chain


class Automaton(parser):
    class Process(object):
        def __init__(self, A, parent):
            self.state_stack = parent and list(parent.state_stack) or []
            self.output = []
            self.A = A
            A.processes.add(self)

        def shift(self, next_state):
            print id(self), "SHIFT", next_state
            self.state_stack.append(next_state)
            self.A.shift_hook(self.output, next_state)

        def reduce(self, ruleidx):
            print id(self), "REDUCE", ruleidx
            #self.output.append(ruleidx)
            name, elems, commit = self.A.R[ruleidx]
            count = len(elems)
            self.state_stack = self.state_stack[: - count]
            goto = self.A.ACTION[self.state][name]
            self.state_stack.append(goto[0][1])
            return self.A.reduce_hook(self.output, ruleidx)

        def __hash__(self):
            return id(self)

        state = property(lambda s: s.state_stack[-1])

    def shift_hook(self, output, next_state):
        pass

    def reduce_hook(self, output, ruleidx):
        return True

    def init(self, token_stream):
        self.toki = iter(token_stream)
        self.processes = set()
        p = Automaton.Process(self, None)
        self.input_stack = [self.toki.next()]
        p.shift(self.initial_state)

    input = property(lambda s: s.input_stack[-1])

    def shifts_reds(self):
        def spawn(p, aclist):
            if not aclist:
                return []
            return [(p, aclist[0])] + [(Automaton.Process(self, p), ac)
                                       for ac in aclist[1:]]

        shifts = []
        reductions = []
        accepts = []

        pcopy = set(self.processes)
        for (p, ac) in chain(*[spawn(p, self.ACTION[p.state][self.input[0]])
                             for p in pcopy]):
            if ac[0] == 'S':
                shifts.append((p, ac))
            if ac[0] == 'R':
                reductions.append((p, ac))
            if ac[0] == 'A':
                accepts.append(p)
        return shifts, reductions, accepts

    def recognize(self, token_stream):
        self.init(token_stream)

        accepting = []

        while len(self.processes):
            shifts, reductions, accepts = self.shifts_reds()
            accepting.extend(accepts)
            self.processes.difference_update(accepts)
            while reductions:
                for p, (red, rule) in reductions:
                    if not p.reduce(rule):
                        self.processes.remove(p)
                shifts, reductions, accepts = self.shifts_reds()
                accepting.extend(accepts)
                self.processes.difference_update(accepts)

            if shifts:
                self.input_stack.append(self.toki.next())
                for p, (shift, state) in shifts:
                    p.shift(state)

        return [acc.output for acc in accepting]
