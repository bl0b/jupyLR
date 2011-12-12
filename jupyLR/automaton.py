from parser import parser
from itertools import chain, ifilter


class Automaton(parser):

    class Process(object):

        def __init__(self, A, parent):
            self.state_stack = parent and list(parent.state_stack) or []
            self.output = []
            self.A = A
            A.processes.add(self)

        def shift(self, next_state):
            #print id(self), "SHIFT", next_state
            self.state_stack.append(next_state)
            self.A.shift_hook(self.output, next_state)

        def reduce(self, ruleidx):
            #print id(self), "REDUCE", ruleidx
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

    def shifts_reds(self, blacklist=[]):
        print "shifts_reds blacklist", blacklist
        shifts = []
        reductions = []
        accepts = []
        # helper to spawn a new process for each action but the first.
        spawn = lambda p, aclist: aclist \
                                  and [(p, aclist[0])] \
                                      + [(Automaton.Process(self, p), ac)
                                         for ac in aclist[1:]] \
                                  or []
        pcopy = set(self.processes)
        actions = lambda p: filter(lambda x: x not in blacklist,
                                   self.ACTION[p.state][self.input[0]])
        pac = chain(*[spawn(p, actions(p)) for p in pcopy])
        for (p, ac) in pac:
            if ac[0] == 'S':
                shifts.append((p, ac))
            if ac[0] == 'R':
                reductions.append((p, ac))
            if ac[0] == 'A':
                accepts.append(p)
        print "shifts", shifts, "reductions", reductions,
        print "accepts", accepts
        return shifts, reductions, accepts

    def recognize(self, token_stream):
        self.init(token_stream)
        accepting = []
        red_blacklist = set()
        while len(self.processes):
            shifts, reductions, accepts = self.shifts_reds()
            accepting.extend(accepts)
            self.processes.difference_update(accepts)

            while reductions:
                for p, (red, rule) in reductions:
                    if not p.reduce(rule):
                        #print "process", id(p.output),
                        #print "failed to reduce; blacklisting", (red, rule)
                        self.processes.remove(p)
                        red_blacklist.add((red, rule))
                shifts, reductions, accepts = self.shifts_reds(red_blacklist)
                accepting.extend(accepts)
                self.processes.difference_update(accepts)

            if shifts:
                red_blacklist = set()
                self.input_stack.append(self.toki.next())
                for p, (shift, state) in shifts:
                    p.shift(state)

        return [acc.output for acc in accepting]
