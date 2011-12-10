

def rule_items(rulename, elems):
    "converts a sequence of elements into a sequence of items"
    return ((elems, i, rulename) for i in xrange(len(elems) + 1))


def items(rules):
    "convert sequence of rules into a sequence of items"
    ret = []
    for rulename, elems in rules:
        ret.extend(rule_items(rulename, elems))
    return ret


def first(itemset, ruleset):
    "set of the tokens at the right of each dot in this item set"
    ret = set()
    for ruleelems, i, rulename in itemset:
        if i == len(ruleelems):
            continue
        e = ruleelems[i]
        if not e in ruleset:
            ret.add(e)
    return ret


def follow(itemset, ruleset):
    "all transitions from an item set in a dictionary [token]->item set"
    print "FOLLOW FOR:"
    print itemsetstr(itemset)
    ret = dict()
    for ruleelems, i, rulename in itemset:
        if i == len(ruleelems):
            continue
        e = ruleelems[i]
        if e not in ret:
            ret[e] = set()
        ret[e].update(closure([(ruleelems, i + 1, rulename)], ruleset))
    for k, v in ret.iteritems():
        print '', k, '->'
        print itemsetstr(v)
    return ret


def closure(itemset, ruleset):
    "the epsilon-closure of this item set"
    C = set(itemset)
    last = -1
    while len(C) != last:
        last = len(C)
        Ctmp = set()
        for item in C:
            elems, i, name = item
            if i == len(elems):
                continue
            if elems[i] in ruleset:
                Ctmp.update((e, 0, elems[i]) for e in ruleset[elems[i]])
        C.update(Ctmp)
    return C


def kernel(itemset, start):
    "the kernel items in this item set"
    return set(ifilter(lambda (e, i, n): i != 0 or n == '@', itemset))
