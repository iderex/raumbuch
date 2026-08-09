# The expression sub-language

A metric component, a stress-energy component, a coordinate range, a parameter
range and a stratum condition are all strings, and they are all strings in this
one language. Record
[0003](decisions/0003-the-solution-record.md) fixed that they are, and that both
the function list and the constant list are closed. This document fixes what is
in them, what the grammar is, and what a parser refuses.

The reason the language is small is in record 0003 and is not restated here past
one sentence: loading a record parses text into a syntax tree, and a catalogue is
the kind of file people download from the internet.

The parser is `src/raumbuch/expression.py`. It produces the syntax tree of this
grammar and nothing else. It constructs no algebra object: turning a tree into
the arithmetic of record
[0009](decisions/0009-arithmetic-and-zero-testing.md) happens behind the
interface record 0001 puts in `src/raumbuch/algebra/`, which is empty today.

## The grammar

Complete. Anything a reader can write that this does not derive is refused, and
the refusal names which rule it fell out of.

```
condition    = comparison { "and" comparison }
comparison   = expression relation expression
relation     = "!=" | "<" | "<=" | "=" | ">" | ">="

expression   = term { ( "+" | "-" ) term }
term         = signed { ( "*" | "/" ) signed }
signed       = [ "-" | "+" ] factor
factor       = atom [ "^" exponent ]
atom         = integer
             | name
             | call
             | "(" expression ")"
call         = name "(" expression ")"
exponent     = integer
             | "-" integer
             | "(" exponent ")"
integer      = digit { digit }
name         = ( letter | "_" ) { letter | digit | "_" }
digit        = "0" ... "9"
letter       = "A" ... "Z" | "a" ... "z"
```

Five operators and one bracket. `^` binds tighter than `*` and `/`, which bind
tighter than `+` and `-`, and the four binary operators group to the left.
Whitespace separates tokens and is otherwise not read.

`^` does not chain, and that falls out of the exponent rule rather than out of
an associativity choice: an exponent is an integer, so there is no derivation of
`a^b^c` at all and the parser refuses one.

The name production is the identifier pattern of `schema/record-1.schema.json`,
character for character, so a coordinate or parameter the schema admits as a
declaration is a name this grammar admits as a use. Two patterns would be two
places to change.

Three properties of that grammar are decisions rather than shorthand, and each
one has a refusal behind it.

**A literal is an integer, and a rational is a quotient of two of them.** `1/2`
is admitted and is exactly the rational one half, because the arithmetic under
this language is exact and division is one of the five operators. `0.5` is
refused. A decimal point is the one place a reader could put a floating point
number into a record, and record 0009 keeps floating point out of the
classification path entirely, so this is the boundary where that decision is
enforced rather than described.

**An exponent is an integer.** `r^2` and `r^(-1)` are admitted, `r^(1/2)` and
`t^(2*p)` are not. The ground field of record 0009 is the rational functions in
the declared symbols, and an integer power keeps an expression inside it while a
rational power leaves it for an algebraic extension the record says is not
entered, and a symbolic power leaves it for something wider still. Where an
entry needs a variable exponent it writes `exp(p*log(t))`, which is in the
function list below and stays inside the field.

**A name is ASCII.** A Cyrillic `а` and a Latin `a` are different names that no
reader can tell apart, and a record is a file somebody downloads. The parser
refuses a non-ASCII character by its own name rather than folding it into an
unknown character, so a confusable is a diagnosis and not a shrug.

What a name means is not a question this grammar answers. An identifier has to
be a coordinate the chart declares, a parameter the record declares, or a
constant from the list below, and deciding that needs the record around the
expression. It is a loader refusal, issue #36, and the parser hands up the set
of names an expression used so the loader can make it.

## A condition is not an expression, and which field is which

Record 0003 says a metric component, a stress-energy component, a coordinate
range and a parameter range are all strings in one small sub-language, and lists
its material: literals, identifiers, `+ - * / ^`, parentheses, the functions and
the constants. That list has no relational operator in it, and the worked
Schwarzschild record in the same document writes `r > 2*M` as a coordinate
range and `M > 0` as a stratum condition. A grammar that admits only the listed
material cannot read the record the document is built around.

So the sub-language has two entry points over one set of expressions. A field
that holds a value is an expression. A field that says where a value holds is a
comparison of two expressions, and that is the whole of the difference:

| Field | Read as |
| --- | --- |
| `chart.metric[].value` | an expression |
| `matter.stress_energy[].value` | an expression |
| `chart.range[]` | a condition |
| `parameter[].range` | a condition |
| `stratum[].condition` | a condition |

Two shapes are deliberately outside it. A chained comparison, `0 < theta < pi`,
is refused rather than read as two, because reading it as two is a guess that is
correct until somebody writes something else. And there is no `or` and no `not`:
a stratum whose condition is a disjunction is two strata, which is the shape
record 0005 asks for, and a stratum whose condition is a negation is the
complement somebody has not written down. `and` is the one connective, which
makes it a word no coordinate may be named.

`chart.identifications[]` is not in this language at all. The schema types it as
prose, and `phi ~ phi + 2*pi` in the worked record uses a character the grammar
has no token for. Nothing here parses an identification and nothing here checks
one.

## The closed constant list

| Constant | What it is |
| --- | --- |
| `pi` | the ratio of a circumference to a diameter |

One entry, and the list exists because of it: the worked Schwarzschild record
has `theta < pi` in a coordinate range, and there is no chart for `pi` to be a
coordinate of. Record 0009 admits a named constant as a transcendental symbol
with no declared relations, which is what keeps the field the expressions live
in a rational function field.

The imaginary unit is deliberately not here. Record 0009 extends the ground
field by `i` because record 0002 chose a complex null tetrad, and that extension
happens inside the algorithm, on scalars the algorithm computed. No record's
asserted text needs it, and a name that no record writes is a name this list
should not carry.

`e` is not here either, because `exp(1)` is the same number and one spelling of
a thing is easier to check than two.

A record that needs a constant this list does not carry is a change to this
list, to the tuple in the parser, and to whichever decision record the constant
belongs to. That route is visible; a free symbol would not be.

## The closed function list

Every admitted function takes exactly one argument. A function of two arguments
would be a second shape in the grammar and nothing in the reference literature
this catalogue starts from needs one.

Six functions are the normal form. The derivative column is the property record
0009 requires and is the reason each one is here, with `u` the argument and `u'`
its derivative:

| Function | Derivative | Stays in the list because |
| --- | --- | --- |
| `sin(u)` | `cos(u)*u'` | `cos` is in the list |
| `cos(u)` | `-sin(u)*u'` | `sin` is in the list |
| `exp(u)` | `exp(u)*u'` | it is its own derivative |
| `log(u)` | `u'/u` | the result is a quotient and needs no function at all |
| `sinh(u)` | `cosh(u)*u'` | `cosh` is in the list |
| `cosh(u)` | `sinh(u)*u'` | `sinh` is in the list |

Four more are admitted and are rewritten to those six before any arithmetic
happens, so they add a spelling and not a domain:

| Function | Rewrites to |
| --- | --- |
| `cot(u)` | `cos(u)/sin(u)` |
| `coth(u)` | `cosh(u)/sinh(u)` |
| `tan(u)` | `sin(u)/cos(u)` |
| `tanh(u)` | `sinh(u)/cosh(u)` |

`sec` and `csc` are not admitted. `1/cos(u)` and `1/sin(u)` say the same thing
in the operators the grammar already has, and a name that buys no expressiveness
costs the differentiation of milestone 5, the rewrite table below and the
fuzzing of issue #90 one case each.

`sqrt` is not admitted, and it is the omission most likely to be read as an
oversight. A square root is an algebraic extension of the rational function
field, and record 0009 says algebraic extensions are entered as late as possible
and, for the discrete steps this board takes, are not entered at all. Admitting
`sqrt` as an opaque symbol would be worse than refusing it: `sqrt(r)^2` and `r`
would be different elements of the field, so a zero test would answer that a
vanishing expression does not vanish, which is the confidently wrong
classification this project exists to remove. The relation that would repair
that is not in the declared set below and is not cheap to add.

### Closure under differentiation

Record 0009 requires the list to be closed under differentiation, because the
algorithm differentiates the curvature repeatedly and a function whose
derivative is not expressible in the list leaves the declared domain on the
first covariant derivative.

The derivative column above is the proof for the six, one row each. The four
rewritten functions inherit it, because a quotient of two functions from the six
differentiates into quotients and products of the same six. Integer powers
inherit it too: the derivative of `f^n` is `n*f^(n-1)*f'`, and `n-1` is an
integer whenever `n` is, so the exponent rule of the grammar is closed under the
same operation. Sums, products and quotients need nothing outside the operators.

So every expression this grammar admits has a derivative this grammar admits.

## The declared relations

Record 0009 requires that every relation the project relies on among the
admitted functions is declared as a rewrite to a normal form, and that no
relation is relied on that is not declared. This is that list.

| Relation | Rewrite | Needed by |
| --- | --- | --- |
| `sin(u)^2 + cos(u)^2 = 1` | `sin(u)^2` becomes `1 - cos(u)^2` | `r^2*sin(theta)^2` in the worked Schwarzschild metric |
| `cosh(u)^2 - sinh(u)^2 = 1` | `sinh(u)^2` becomes `cosh(u)^2 - 1` | the hyperbolic form of the same shape, in a metric written on a hyperbolic slice |
| `exp(u)*exp(v) = exp(u+v)` | a product or integer power of exponentials becomes one exponential of the summed argument | `exp(t)^2` and `exp(2*t)` are the same function and a zero test that says otherwise is wrong |
| `exp(0) = 1` | `exp` of a vanishing argument becomes `1` | the previous rewrite produces it whenever two exponentials cancel |
| `cot(u) = cos(u)/sin(u)` | the definition above | the four rewritten functions |
| `coth(u) = cosh(u)/sinh(u)` | the definition above | the four rewritten functions |
| `tan(u) = sin(u)/cos(u)` | the definition above | the four rewritten functions |
| `tanh(u) = sinh(u)/cosh(u)` | the definition above | the four rewritten functions |

The first rewrite is what makes the normal form work. After it, an expression in
`sin(u)` and `cos(u)` is a polynomial in `cos(u)` plus `sin(u)` times another
polynomial in `cos(u)`, and two such expressions are equal exactly when they are
identical. The second does the same for the hyperbolic pair.

Relations that are true and are **not** declared, so nothing here relies on
them:

`log(u*v) = log(u) + log(v)`, and its consequence `log(u^n) = n*log(u)`. Both
hold only up to a branch on the sign of the argument, and record 0009 refuses a
branch choice hidden inside a representation.

The angle-sum and double-angle identities, past what the first rewrite already
gives. `sin(2*u)` and `2*sin(u)*cos(u)` are different elements of the field
here, and a record writing one where another writes the other produces two
expressions this arithmetic will not identify.

`sin(pi) = 0`, and every other value of an admitted function at an admitted
constant. Record 0009 says this outright: a named constant is a transcendental
symbol with no declared relations, so `pi` inside a function argument is opaque.
The cost is stated there and this is where it lands.

Nothing has applied any of these rewrites. The operation that does is
`apply the declared rewrites of the closed function list` on the algebra
interface of record 0001, and `src/raumbuch/algebra/` holds no operations yet.
What this document does is declare the set; the run that exercises it does not
exist, and this sentence stays until it does.

## What the parser refuses, by name

One reason per line, and each line says what failure it prevents rather than
what rule it came out of. The parser raises through one function, so a reason
that is not on this list is a reason nothing can produce.

| Reason | What it prevents |
| --- | --- |
| `empty-expression` | a field present but blank, read downstream as the number zero |
| `non-ascii-character` | a confusable letter making two names that no reader can tell apart |
| `unknown-character` | a character the grammar has no token for, which is every escape shape below |
| `decimal-literal` | a floating point number entering an arithmetic record 0009 keeps exact |
| `power-is-caret` | `**` written by somebody whose last language spelled it that way |
| `unknown-function` | a call to something outside the closed list, including a call to a parameter |
| `function-takes-one-argument` | a call with nothing between its brackets |
| `function-name-without-argument` | a function's name used as though it were a coordinate |
| `non-integer-exponent` | an exponent that leaves the rational function field of record 0009 |
| `unclosed-parenthesis` | a bracket that opens and does not close |
| `unexpected-token` | an operator or bracket where the grammar expects something else |
| `trailing-input` | a second expression after the first, which is where a statement separator arrives |
| `comparison-in-an-expression` | a condition written into a field that holds a value |
| `comparison-expected` | a range or a stratum condition that restricts nothing |
| `chained-comparison` | `0 < theta < pi`, which reads as one statement and is two |
| `expression-too-deep` | brackets or calls nested until the recursive descent runs out of stack |
| `number-too-long` | an integer literal past what the interpreter converts, which fails in a language about digit limits rather than about records |

## Escapes, and what refuses each one

The shapes below are the ones a reader worried about a downloaded catalogue asks
about first. Each is a fixture in `tests/test_expression.py` and each stays
there, because a refusal nobody has watched fire is a refusal that may not work.

| Written into a record | Refused as | On what |
| --- | --- | --- |
| `r.__class__` | `unknown-character` | the full stop |
| `sin(r)[0]` | `unknown-character` | the bracket |
| `eval("1")` | `unknown-character` | the quotation mark |
| `sin(r); import os` | `unknown-character` | the semicolon |
| `lambda: r` | `unknown-character` | the colon |
| `__import__("os")` | `unknown-character` | the quotation mark |
| `__import__(r)` | `unknown-function` | the name, which is not on the list |
| `open(r)` | `unknown-function` | the name, which is not on the list |

That most of them land on one reason is the shape of the language rather than a
weakness of the parser. The grammar has no token for a full stop, a bracket, a
quotation mark, a comma, a colon or a semicolon, so an expression that reaches
for the host fails at the first character that is not in the alphabet, and there
is no second line of defence to reach. The last two rows are the ones that get
past the alphabet, because a name of underscores and letters is a name here, and
they are stopped by the function list instead.

A stronger claim is available and is not made here. Nothing about the parser
proves that the loader never reaches an evaluator; what proves it is that no
module outside `src/raumbuch/algebra/` names the algebra layer at all, which
record 0001 fixes and issue #36 quotes the command for.

## Is it complete enough for the catalogue

The first bullet of issue #40 asks that the grammar be complete enough to write
the metric of every entry in the first catalogue milestone. That milestone is
issues #73 and #74 and no entry exists yet, so this cannot be measured and is
not claimed.

What is measured is the nearest thing available. `tests/test_expression.py`
parses every metric component, every coordinate range and the stratum condition
of the worked Schwarzschild record, read out of `docs/record-format.md` rather
than copied, so a change to that record is a change to what this parser is asked
to read. Beside it, the same test parses every component of six more metrics
written in this language and chosen for the shapes an entry that exercises the
classification would take: a rotating vacuum in Boyer-Lindquist coordinates, a
charged static one, a static one with a cosmological constant, a hyperbolic
slicing, a homogeneous anisotropic one whose exponents are parameters, and a
plane wave. The command is in the pull request that landed this document.

The anisotropic one is the row worth reading. Its metric is usually written
`t^(2*p)`, which this grammar refuses, and it is here as `exp(2*p*log(t))`,
which the exponent rule above says is the way to write it. That the entry is
writable at all is the evidence for that sentence.

The gap between that and the bullet is real and is one direction: those metrics
are written here, and the entries of #73 and #74 are written there. Where an
entry needs something this grammar refuses, the entry is the evidence and the
repair is a change to this document rather than an exception in a record.

## A record cannot carry a free function, and record 0009 expects one

Record 0009 admits free functions of the coordinates as function symbols with no
relations, and says outright that refusing every record carrying one was
rejected because the families with free functions are not a fringe case.

Nothing in the record format lets a record declare one. The schema fixes the
top-level keys and refuses anything else, and there is no key for a function the
way there is `parameter` for a parameter:

    python3 -c "import json;print(json.load(open('schema/record-1.schema.json'))['additionalProperties'])"
    False

So the closed function list here is the whole of what a call may name, a metric
written with `a(t)` in it is refused as `unknown-function`, and the alternative
of admitting an undeclared call name would delete the refusal this list exists
to make. Nothing else would refuse it either: the identifier rule reaches names,
not call names.

The consequence is a bound on the catalogue rather than on this parser. Every
entry of milestone 8 has to have a metric written in closed form, and a family
carried by an arbitrary function cannot be transcribed until a record can
declare one. Where that declaration lands is the record format rather than this
document.

## What this document does not settle

The arithmetic. That is record 0009, which this document is downstream of.

The order the rewrites are applied in, and the cost of applying them. That is
the algebra interface of record 0001 and the normalisation of record 0010.

Whether an expression is well formed as physics. A metric component that parses
is a metric component in this language, and whether it is a metric at all is
issue #50.
