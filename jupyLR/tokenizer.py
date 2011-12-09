__all__ = ["TokenizerException", "tokenize_iter", "tokenize", "token_pattern"]

import re
from itertools import chain

# Code adapted from an answer at stackoverflow.com
# (url split in 2 to please pep8)
#http://stackoverflow.com/questions/2358890
#/python-lexical-analysis-and-tokenization

num = r"(?:\.[0-9]+|(?:[0-9]+)(?:\.[0-9]*)?)"
expo = r"(?:[eE]-?[0-9]+\.?[0-9]*)?[lLdf]?"
number = num + expo

keyword = [
    'kw_switch', 'kw_class', 'kw_while', 'kw_do', 'kw_for', 'kw_typedef',
    'kw_if', 'kw_else', 'kw_struct', 'kw_union', 'kw_return', 'kw_namespace',
    'kw_new', 'kw_delete', 'kw_operator', 'kw_typename', 'kw_template',
    'kw_throw', 'kw_using', 'kw_restrict', 'kw_extension', 'kw_void',
    'kw_inline', 'kw_sizeof', 'kw_enum', 'kw_typeof',
]

type_spec = [
    'typename', 'const', '__const', 'static', 'register', 'volatile',
    'virtual', 'extern', 'long', 'short', 'unsigned', 'signed', 'friend',
]

scope = ['public', 'private', 'protected']

sym_assert = ''.join('(?!(?P=%s))' % i
                     for i in chain(keyword, ['type_spec', 'scope']))

token_pattern = r"""
(?P<number>""" + number + r""")
|(?P<ellipsis>\.\.\.)
|(?P<kw_switch>\bswitch\b)
|(?P<kw_class>\bclass\b)
|(?P<kw_while>\bwhile\b)
|(?P<kw_gcc_attr>\b__attribute__\b)
|(?P<kw_do>\bdo\b)
|(?P<kw_typeof>\b(?:__typeof|__typeof__)\b)
|(?P<kw_enum>\benum\b)
|(?P<kw_sizeof>\bsizeof\b)
|(?P<kw_inline>\binline\b)
|(?P<kw_void>\bvoid\b)
|(?P<kw_extension>\b__extension__\b)
|(?P<kw_restrict>\b__restrict\b)
|(?P<kw_throw>\bthrow\b)
|(?P<kw_using>\busing\b)
|(?P<kw_namespace>\bnamespace\b)
|(?P<kw_typedef>\btypedef\b)
|(?P<kw_for>\bfor\b)
|(?P<kw_if>\bif\b)
|(?P<kw_else>\belse\b)
|(?P<kw_struct>\bstruct\b)
|(?P<kw_union>\bunion\b)
|(?P<kw_return>\breturn\b)
|(?P<kw_template>\btemplate\b)
|(?P<kw_typename>\btypename\b)
|(?P<kw_operator>\boperator\b)
|(?P<scope>\b(?:""" + '|'.join(scope) + r""")\b)
|(?P<type_spec>\b(?:""" + '|'.join(type_spec) + r""")\b)
|(?P<kw_new>\bnew\b)
|(?P<kw_delete>\bdelete\b)
|(?P<symbol>""" + sym_assert + r"""\b[a-zA-Z_][a-zA-Z0-9_]*\b)
|(?P<access>(?:\.(?!\.\.)|->)[*]?)
|(?P<ampersand>[&])
|(?P<comma>[,])
|(?P<minus>[-](?![=>-]))
|(?P<semicolon>[;])
|(?P<tilde>[~])
|(?P<open_angle>(?<!<)[<](?![<=]))
|(?P<close_angle>(?<!>)[>](?![>=]))
|(?P<open_square>[[])
|(?P<close_square>[]])
|(?P<open_paren>[(])
|(?P<close_paren>[)])
|(?P<namespace_member>::)
|(?P<ternary>[?])
|(?P<colon>(?<!:):(?!:))
|(?P<open_curly>[{])
|(?P<close_curly>[}])
|(?P<whitespace>\s+)
|(?P<assign_set>(?<!=)[=](?!=))
|(?P<assign_update>(?:>>|<<|(?<![<>])[<>]|[&^%*/+-])[=](?!=))
|(?P<shift>(>>|<<)(?!=))
|(?P<incdec>[+][+]|--)
|(?P<string>"(?:\\["bntr]|[^\\"])*")
|(?P<char>'(?:\\['bntr\\]|[^\\'])')
|(?P<boolop>(?:[|][|]|[&][&]|!)(?!=))
|(?P<bitop>(?:(?<!\|)\|(?!\|) | (?<!\^)\^(?!\^))(?!=))
|(?P<comp>==|!=|<=|>=)
|(?P<addmoddiv>[%+/])
|(?P<star>[*])
|(?P<dot>[.])
|(?P<sharp>[#])
|(?P<dollar>[$])
"""

token_re = re.compile(token_pattern, re.VERBOSE)


discard_names = ('whitespace', 'kw_restrict', 'kw_extension')
discard_values = ('static', 'inline', 'const', 'volatile')


class TokenizerException(Exception):
    pass


def tokenize_iter(text, token_re, discard_names={}, discard_values={}):
    pos = 0
    while True:
        m = token_re.match(text, pos)
        if not m:
            break
        pos = m.end()
        tokname = m.lastgroup
        tokvalue = m.group(tokname)
        if tokname not in discard_names and tokvalue not in discard_values:
            yield tokname, tokvalue
    if pos != len(text):
        msg = 'tokenizer stopped at pos %r of %r in "%s" at "%s"' % (
                pos, len(text), text, text[pos:pos + 3])
        raise TokenizerException(msg)
# End of adapted code

tokenize = lambda t: list(tokenize_iter(t, token_re,
                                        discard_names,
                                        discard_values))
