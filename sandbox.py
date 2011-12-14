#!/usr/bin/bpython -i

import jupyLR
from jupyLR import *

#a = Slr('E', 'E = a E a E = a', make_scanner(a='a', b='b'))
#x = a('aaa')
#print "x =", x
#


#alpha = ''.join(chr(x) for x in xrange(ord('a'), ord('z') + 1))
#alpha = "abc"
#template = "E = %c E %c E = %c"
#grammar = ' '.join(template % ((c,) * 3) for c in alpha)
#tokens = dict((c, c) for c in alpha)
#pal = Slr('E', grammar, make_scanner(**tokens))
#print pal.action_to_str()


b = Slr('E', 'E = a E = a a E = E E', make_scanner(a='a'))
