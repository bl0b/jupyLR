# jupyLR

An old-school parsing framework that implements the time-honoured scanner+parser stack.

Lexical analysis is performed with regular expressions (as described in http://stackoverflow.com/a/2359619).
Parsing is done with the GLR algorithm based on an SLR automaton.

## Synopsis

    from jupyLR import make_scanner, Slr

    my_scanner = make_scanner(zero='0', one='1', star='[*]', plus='[+]')

    grammar = """
        E = E plus B
        E = E star B
        E = B
        B = zero
        B = one
    """

    a = Slr('E', grammar, my_scanner)

    a('1+1')

### Scanner

The scanner converts a text into a stream of tokens. A token is a pair (token_type, token_value).
jupyLR provides a convenient way to define a scanner with the function make_scanner(). As its docstring states:

Each named keyword is a token type and its value is the corresponding
regular expression. Returns a function that iterates tokens in the form
(type, value) over a string.

Special keywords are discard_names and discard_values, which specify lists
containing tokens names or values that must be discarded from the scanner
output.

As an undocumented feature, the scanner holds the list of token types in
its attribute 'tokens'.

### Grammar

The grammar you can provide to configure a parser is extremely simple: one symbol followed by the equal "=" sign
defines a rule name, and all other words after the equal sign are the production of this rule, until the next rule name
(that is, everything until the word before the next equal sign or the end).

### Parser

The parsing algorithm is Generalized LR (SLR). The LR(0) sets and action/goto tables are computed on the fly when the Slr instance
is created. Support for serialization is planned very soon to avoid recomputing the automaton for big grammars.
For the user's convenience, the parser is callable, taking a string and outputting the stream of productions which can be used
to build an AST.

## How to use jupyLR

### Git

git clone git://github.com/bl0b/jupyLR.git

## TODO

 * fill in "How to use jupyLR" section in this readme
 * draw the automaton using pydot or something
 * ...
 * PROFIT!
