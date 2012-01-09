__all__ = ['pp_ast', 'Automaton', 'Scanner', 'make_scanner']

from automaton import Automaton
from tokenizer import Scanner, make_scanner


def pp_ast(ast, indent='', is_last=True):
    """Pretty-print an AST node created by the parser."""
    if is_last:
        prefix = '`- '
        follow = '   '
    else:
        prefix = '+- '
        follow = '|  '
    if type(ast) is not tuple:
        print ''.join((indent, prefix, str(ast)))
    elif len(ast) and type(ast[1]) is not str:  # be it a tuple or anything
        print ''.join((indent, prefix, ast[0]))
        subi = indent + follow
        for x in ast[1:-1]:
            pp_ast(x, subi, False)
        pp_ast(ast[-1], subi, True)
    else:
        print ''.join((indent, prefix, str(ast)))
