from parser import parser


class Automaton(parser):

    def init(self, token_stream):
        self.toki = iter(token_stream)
        self.state_stack = []
        self.input_stack = []
        self.shift(self.initial_state)
        self.output = []

    def shift(self, next_state):
        self.state_stack.append(next_state)
        self.input_stack.append(self.toki.next())

    def reduce(self, ruleidx):
        self.output.append(ruleidx)
        name, elems = self.R[ruleidx]
        count = len(elems)
        self.state_stack = self.state_stack[: - count]
        goto = self.ACTION[self.state][name]
        self.state_stack.append(goto[0][1])
        return True

    state = property(lambda s: s.state_stack[-1])
    input = property(lambda s: s.input_stack[-1])

    def recognize(self, token_stream):
        self.init(token_stream)

        while True:
            ac = self.ACTION[self.state][self.input[0]]
            if len(ac) == 0:
                print "ERROR", self.state_stack, self.input_stack
                return False
            if len(ac) > 1:
                print "CONFLICT!", ac
                return False
            ac = ac[0]
            if ac[0] == 'R':
                if not self.reduce(ac[1]):
                    return False
            elif ac[0] == 'S':
                self.shift(ac[1])
            elif ac[0] == 'A':
                print "DONE"
                return True
