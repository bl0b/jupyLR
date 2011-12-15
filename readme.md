# jupyLR

An old-school parsing framework that implements the time-honoured scanner+parser stack.

Lexical analysis is performed with regular expressions (as described in http://stackoverflow.com/a/2359619).
Parsing is done with the GLR algorithm based on an SLR automaton.

## Synopsis

    from jupyLR import Scanner, Automaton

    my_scanner = Scanner(zero='0', one='1', star='[*]', plus='[+]')

    grammar = """
        E = E plus B
        E = E star B
        E = B
        B = zero
        B = one
    """

    a = Automaton('E', grammar, my_scanner)

    a('1+1')

### Scanner

The scanner converts a text into a stream of tokens. A token is a pair (token_type, token_value).
jupyLR provides a convenient way to define a scanner with the Scanner class. As the __init__ docstring states:

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

The parsing algorithm is Generalized LR (GLR). The LR(0) sets and SLR action/goto tables are computed on the fly when the Automaton instance
is created. Support for serialization is planned very soon to avoid recomputing the automaton for big grammars.
For the user's convenience, the parser is callable, taking a string and outputting the stream of productions which can be used
to build an AST.

### AST and progressive disambiguation

As the GLR progresses in the parsing, it maintains up-to-date AST and validates each new AST node before continuing.

By default each rule produces an AST node in the form (rule_name, contents...). A dash ("-") can be prepended to a rule
name in the grammar to make this rule transient in the AST.

For instance :

    E = E plus B
    E = B
    B = 1

with the text "1+1" will produce (E (E (B (one, 1))) (plus, +) (E (B (one, 1)))).

The variant :

    E = E plus B
    -E = B
    B = 1

with the same text will produce (E (B (one, 1)) (plus, +) (B (one, 1))).

## How to use jupyLR

### Git

git clone git://github.com/bl0b/jupyLR.git

## TODO

 * fill in "How to use jupyLR" section in this readme
 * draw the automaton using pydot or something
 * ...
 * PROFIT!
