.. _pattern-matching:

Pattern-matching mathematical expressions
=========================================

.. page_status::
    :kind: draft

Problem
-------

In Numbas, we have two related tasks: give feedback based on the form of
a student's answer, and “simplify” expressions according to a
configurable set of rules.

Both of these tasks involve pattern-matching in some form: to give
feedback, different forms of algebraically equivalent expressions must
be described in some general way; to simplify an expression, a rewriting
rule must recognise expressions in a certain form and identify
particular sub-expressions to produce a new form.

Pattern-matching on trees is not as simple as on strings.

If you've done some coding, you might have encountered regular
expressions: these are a standard way of describing patterns in text
strings, often used to perform text replacements.
Regular expressions aren't appropriate for mathematical expressions, because there's a lot
of structure that regular expressions can't pick up.
The most obvious of these is that regular expressions can't deal with matching brackets.
For example, in the simplification rule :math:`a \times (-b) \to -(a \times b)`, :math:`a` and :math:`b` are
arbitrary expressions which may contain any number of nested brackets.
There's also a wealth of semantic information about mathematical
operations, such as commutativity and associativity, that a
pattern-matching system should know about and take into account.

So, we need a pattern-matching system which operates on mathematical
expressions with all of their structure, not strings.
This isn't a new idea: most computer algebra systems, such as Mathematica and Maple, are
fundamentally pattern-matching and term-rewriting systems.

The problem is that how the algorithms in those systems work on a
technical level isn't well documented, and because Numbas runs entirely
on the client, we need an algorithm written in JavaScript.

Thanks to a very fruitful discussion with a couple of attendees at EAMS
2018, I came up with a rough description of the tools that a good
pattern-matching system should offer.

I've spent the time since then implementing the system, and in using it
I came up with some more features that greatly widened the range of
possible uses.

Things we want:

- Consider all terms of an associative operation together, e.g. terms
  in a sum, joined by :math:`+` or :math:`-`.

- Match if a subset of the terms match the given pattern, leaving the other terms unmatched.

- Accept several different forms with the same rule, to avoid
  repetition, e.g. :math:`x+By` is a special case of :math:`Ax+By` with
  :math:`A=1`.

- It would be nice to have built-in matchers for common non-atomic objects, e.g. rational polynomials, complex numbers in Cartesian or polar form, diagonal matrices.

- A fairly readable (and writable) syntax for defining patterns which match expressions.

  It doesn't need to make immediate sense, but shouldn't be too complicated:
  regular expressions don't make sense to someone who hasn't seen them
  before, but there are very few things to learn.

- Capture a missing term with a default value.

- Identify equivalent terms that appear in more than one place, for collecting or cancelling.

Once you've got pattern-matching and rewriting, you can do lots of things:

* Check the form of an answer.
* Simplify expressions.
* Symbolic differentiation and integration.
* Obtain canonical forms for (some classes of) expressions.
* Other CAS techniques.

Rewriting an expression
#######################

To define a rewriting rule, we need a :defn:`pattern` that the expression must match and a :defn:`result` expression, which might have parts of the matched expression substituted into it.

If the language for patterns is not expressive enough, there could be combinatorial explosion in the number of rules that must be defined.
(But a more expressive pattern language could lead to combinatorial explosion in the algorithm's running time).

Rewriting rules should ignore parts of the expression that remain unchanged, and keep them roughly where they were in the rewritten expression.

It must be possible to evaluate a captured term to an object that you can do arithmetic with, for example collecting together constant terms.

It's often much easier to use several rules together, rather than writing one rule which does everything.
For example, when simplifying the fraction :math:`\frac{18}{6}`, one rule could first cancel the common factor to obtain :math:`\frac{3}{1}`, and then another rule could remove the denominator :math:`1` to obtain :math:`3`.

Examples
~~~~~~~~

* Take negation out of a fraction: 

  :math:`\frac{-x}{y}` becomes :math:`- \frac{x}{y}`.

* Collect constants: 

  :math:`1 + x + 3` becomes :math:`x + 4`.

* Collect coefficients of arbitrary terms: 

  :math:`5 \times (x + \sin(z)) - 3 \times (x+\sin(z))` becomes :math:`2 \times (x+\sin(z))`.

* Remove terms with a factor of zero: 

  :math:`\cos(t) + 0 \times e^{5t} + z` becomes :math:`\cos(t) + z`.

* Simplify square roots of square numbers: 

  :math:`\sqrt{16}` becomes :math:`4`, but :math:`\sqrt{3}` is unchanged.

* Apply trigonometric identities: 

  :math:`\cos(\pi/2)` becomes :math:`0`, :math:`\sin(3\pi/2)` becomes :math:`-1`, but :math:`\sin(0.34 \pi)` is unchanged.

* Cancel common factors on the top and bottom of a fraction: 

  :math:`\displaystyle \frac{4 \, a^2 \, b \, c}{6 \, a \, b}` becomes :math:`\displaystyle \frac{2 \, a \, c}{3}`.

* Extract a scalar factor from the elements of a matrix: 

  :math:`\begin{pmatrix} 2\lambda & 0 \\ 0 & - \lambda \, x \end{pmatrix}`` becomes :math:`\lambda \begin{pmatrix} 2 & 0 \\ 0 & -x \end{pmatrix}`.

Determining the form of an expression
#####################################

In a 'mathematical expression' question, the student's answer :math:`S` is an algebraic expression which must match the teacher's expected answer :math:`T`.

We can numerically establish that the student has given an equivalent expression by substituting values for :math:`x` into both :math:`S` and :math:`T`, but this tells us nothing about the *form* of :math:`S`.

Often, valid forms of answer to a particular question differ substantially from each other.
The order of terms in a sequence of commuting operations usually doesn't matter, and some terms may be optional or not present in some randomisations of the question.

Examples
~~~~~~~~

* The student must expand :math:`(x+\alpha)(x+\beta)`.

  The expanded expression will be of the form :math:`x^2+Ax+B`.

  Necessary conditions for 'expanded' include 'contains no brackets', and 'each term
  is an integer multiplied by a power of :math:`x`'.

  The :math:`x` and constant terms might be omitted.

  If the coefficient :math:`A = 1`, it can be omitted.
  
  The opposite task, factorise :math:`x^2+Ax+B`, will produce an
  expression of the form :math:`(x+\alpha)(x+\beta)`.

  A condition for 'factorised' is 'the expression is a product of irreducible
  polynomials'.

* Write a complex number in argument-modulus form, :math:`r\,e^{i\theta}` - :math:`r` and :math:`\theta` could be literal real numbers, or expressions producing real numbers.

  If either of :math:`r` or :math:`\theta` are :math:`1`, they can be omitted.
  
  If :math:`\theta = 0`, then the whole exponent could be written as :math:`e^0`, :math:`1`, or omitted entirely.

  Some complex numbers in argument-modulus form:

  * :math:`5e^{-2i}`

  * :math:`5e^{3i}`

  * :math:`e^i`

  * :math:`(1+\sqrt{2})e^{\frac{\pi}{2}i}`

  * :math:`1.32445e^0`

  * :math:`1`

Previous work
-------------

WeBWorK
#######

WeBWorK uses `'bizarro
arithmetic' <https://github.com/openwebwork/pg/blob/8a089edceb5d3b36500bac47ef3c2daeec10e0e4/macros/bizarroArithmetic.pl>`__
to force expressions which would be equivalent in standard arithmetic to
be non-equivalent.
It then uses the trick of evaluating at randomly chosen points to establish equivalence.
Still unable to give reliable feedback on the form of the student's answer.
Quite a lot of work to set it all up (add flags to context, etc.)

`limitedFactor
context <https://github.com/openwebwork/webwork-open-problem-library/blob/master/OpenProblemLibrary/macros/PCC/contextLimitedFactor.pl>`__

`bizarro math for sine and
cosine <http://webwork.maa.org/moodle/mod/forum/discuss.php?d=4434>`__ -
Davide suggests directly inspecting the Formula object to test if it's
of the form :math:`\sin(\cdot)`.

`Adaptive parameters <http://webwork.maa.org/wiki/AdaptiveParameters>`__
try to allow for free variables which change the value of an expression
linearly, i.e.
:math:`Af(x) + B` instead of :math:`f(x)`.
Another randomised algorithm is used to establish how the parameters affect the expression, as a matrix - pick some random values for the parameters,
and solve the resulting system of equations.

Prolog
######

(Because Chris Sangwin told me to look at it).

Prolog uses a variant of the
`Martelli-Montanari <http://www.nsl.com/misc/papers/martelli-montanari.pdf>`__
unification algorithm to identify values of free variables on either
side of an equation so that they are equivalent.

It doesn't allow for missing values, or alternate forms in one
expression - you'd have to give an equation for each form.

STACK
#####

`STACK <https://stack-assessment.org/>`__ has a few answer tests to do with the form of the student's
answer: LowestTerms, Expanded, FacForm, SingleFrac, PartFrac,
CompletedSquare.

For anything else, you can apply simplification rules to expressions
before comparing - the two expressions should end up exactly equal after
simplifying.

Maxima
######

`Maxima <https://maxima.sourceforge.io/>`__ deals with everything as S-expressions, and seems to require
quite a lot of code to add new rules.

expreduce, Mathics, Mathematica
###############################

`expreduce <https://github.com/corywalker/expreduce>`__ is a project in Go. 
Inspired by Mathics, but some syntax differences.

`A video by Brian
Beckman <https://www.youtube.com/watch?v=S2OEPFbsl50>`__ about how term
rewriting in the style of Mathematica works.
`Jacquard <https://archive.codeplex.com/?p=jacquard>`__ is a JavaScript
clone of Mathematica's syntax.

`Mathics
pattern-matching <https://mathics.angusgriffith.com/doc/reference-of-built-in-symbols/patterns-and-rules/>`__
seems to have many of the same operators I've come up with.
Turns out it's basically a clone of Mathematica.

`Mathematica <https://reference.wolfram.com/language/tutorial/PatternsAndTransformationRules.html>`__\ 's
functionality is similar to what I came up with.

Maple
#####

`Maple's pattern matching
commands <https://www.maplesoft.com/support/help/maple/view.aspx?path=examples/patmatch>`__
don't look as sophisticated as Mathematica, but there are some
shorthands for common patterns: algebraic, linear, multilinear.

Matchpy
#######

`Matchpy <https://matchpy.readthedocs.io>`__ is a library for pattern-matching symbolic expressions in Python.

It seems to be inspired by Mathematica, and isn't very sophisticated at the moment.

It has a "many-to-one "matcher which tries to match an expression against several patterns at once.
Where patterns are similar, it only needs to check once.
Could this be modelled with a nondeterministic finite state automaton?

Rewriting rules are implemented as patterns, with a Python function whose parameters are the captured names, returning a transformed expression.

Rubi
####

`Rubi <http://www.apmaths.uwo.ca/%7Earich/>`__ symbolically integrates.

It's a collection of rewriting rules, first implemented in Mathematica and later ported to other computer algebra systems.

Solution
---------

To define patterns, I added several new symbols to the JME language, for quantifiers, conjunctions and atoms.

I originally had lots of functions of the form ``m_X``, which led to quite long and hard-to-read patterns.
Operators are a lot easier to read, especially the postfix quantifiers which look more like regex
quantifiers, e.g. ``x `?`` rather than ``m_maybe(x)``.

The :ref:`pattern-matching algorithm <matching-a-pattern>` takes a pattern written with these operators and an input expression, and decides if there's a match, producing a collection of captured parts analogous to regular expression capturing groups.

Similarities with regular expressions.
######################################

The matching algorithm is backtracking, like many implementations of regular expression matchers.
When there is a choice to make, due to a quantifier or the order of terms, the matcher can backtrack and make a different choice if one path turns out not to lead to a match.

Quantifiers allow arbitrarily many similar terms to be captured without repetition in the pattern.

The ```&`` operator for specifying two patterns that an expression must match is analogous to positive lookahead in regular expressions.

Unlike most regular expression matchers, patterns can specify arbitrarily complicated conditions on parts of the expression in the middle of the matching process. 
For example, a regular expression can't test that a number is prime in one pass.

Syntax trees
############

A string representing a mathematical expression or pattern is parsed into a syntax tree.

The pattern-matcher operates on these trees.

.. class:: Tree

    A tree consists of a :dfn:`token`, which has a :dfn:`type`, and an ordered list of :dfn:`arguments`, which are themselves trees.

    The types include, but are not limited to:

    * Function application
    * Operator (binary, unary prefix or unary suffix)
    * Variable name
    * Number

    So :math:`\sin(x)+1` would be::

        operator '+' 
            function 'sin'
                variable x
            number 1

.. _pattern-matching-options:

Options
#######

Commutative
    When matching terms joined by a commutative operation
    such as :math:`\times` or :math:`+`, match terms in any order.

Associative
    When matching terms joined by an associative operation,
    collect as many terms as possible to match at once, instead of just
    the two subtrees of the first application of the operation. 
    e.g., :math:`(a+b)+c` is matched as a list of three terms :math:`a`,
    :math:`b`, :math:`c`, not two terms :math:`a+b` and :math:`c`.

Allow other terms
    Match a sequence of terms where the pattern is
    satisfied by a subset of the terms. e.g., :math:`1+2+x` matches
    ``n +n`` - the extra :math:`x` is ignored.
    In a non-commutative match, the pattern must match a contiguous subsequence of the terms.

Strict inverse
    If turned off, ``x-y`` will be considered as
    ``x+(-y)``, so will match patterns like ``?+?``.

    Similar for ``x/y`` being interpreted as ``x*(/y)``.
    If turned on, plus means plus!

Gather as a sequence
    If turned off, then multiple terms matched under the same name will be stored in a list.
    
    If turned on, then they will be captured as a sequence of terms joined by the same operator used to find them, e.g. addition or multiplication.

.. _matching-a-pattern:

Matching a pattern
##################

.. function:: matchTree(ruleTree, exprTree)

    To decide whether the given ``exprTree`` matches the given ``ruleTree``, and return any matched names if so.

    This algorithm operates recursively.
    Its behaviour depends on the type of the token at the top of ``ruleTree``:

    * A capturing operator: the rule must be of the form ``subRule ; name`` - if ``exprTree`` matches ``subRule``, then capture it under ``name``.

    * An :dfn:`identified capturing` operator: the rule must be of the form ``subRule ;= name``.
      All parts of the expression that are captured under this name must be equal.

    * A name: use :func:`matchName`.

    * A function application: use :func:`matchFunction`.

    * An operator: use :func:`matchOp`.

    * A list: use :func:`matchList`.

    * Anything else: use :func:`matchToken`.

    These produce either ``false`` if there is no match, or a match object, mapping captured names to the corresponding parts of ``exprTree``.

    Most of these cases are quite easy.
    The hardest task is to :ref:`match a sequence of terms <match-sequence>` - that's where quantifiers come in.


.. function:: matchName(ruleTree, exprTree)

    When the ``ruleTree`` is a single name token, it is either a special name representing some built-in pattern, or a generic name.

    If the name is not special, it matches ``exprTree`` if ``exprTree`` is also exactly that single name token.

    The special names are:

    * ``?`` - matches any expression.

    * ``$n`` - matches a literal number.
      Annotations on this can specify extra conditions, or match other kinds of numbers, such as fractions or complex numbers.

    * ``$v`` - matches any variable name.

    * ``$z`` - never matches.
      Used as a dummy term when :ref:`matching sequences of terms <match-sequence>`, all of which are matched by a single pattern.

.. function:: matchFunction(ruleTree, exprTree)

    Match the application of a function.

    ``ruleTree`` is a function application token, with an ordered list of arguments.

    If it's a special function, run the logic for that.

    Otherwise, match as an ordinary function:

    * If the expression is not a function application, return false.

    * If the name of the function in the expression is not the same as the one in the rule and the rule function's name is not ``?``, return false.

    * Consider the arguments of both function applications as a sequence, and run :func:`matchTermSequence`.
      Collect names matched in the arguments as follows: if a name is only matched by one argument, keep the match as returned by matchTermSequence.
      If it's matched by more than one argument, the name is matched to a list, with an entry for each argument the name was captured in.

    The special matching functions either change options for the sub-pattern they enclose, or specify conditions:

    * ``m_uses(names)`` - Matches if ``exprTree`` uses all of the given names as free variables.
    * ``m_exactly`` - Turns off the "Allow other terms" :ref:`option <pattern-matching-options>`.
    * ``m_commutative`` - Turns on the "Commutative" :ref:`option <pattern-matching-options>`.
    * ``m_noncommutative`` - Turns off the "Commutative" :ref:`option <pattern-matching-options>`.
    * ``m_associative`` - Turns on the "Associative" :ref:`option <pattern-matching-options>`.
    * ``m_nonassociative`` - Turns off the "Associative" :ref:`option <pattern-matching-options>`.
    * ``m_strictinverse`` - Turns on the "Strict" :ref:`option <pattern-matching-options>`.
    * ``m_gather`` - Turns on the "Gather as a sequence" :ref:`option <pattern-matching-options>`.
    * ``m_nogather`` - Turns off the "Gather as a sequence" :ref:`option <pattern-matching-options>`.
    * ``m_type(type)`` - Matches if the token at the top of ``exprTree`` is of the given type.
    * ``m_func(name,arguments)`` - Matches if ``exprTree`` is the application of the function with the given name, and its arguments match the given list.
    * ``m_op`` - Matches if ``exprTree`` is the application of the operator with the given name, and the operands read from left to right match the given list.
    * ``m_anywhere(subpattern)`` - Matches if the ``subpattern`` matches anywhere within ``exprTree`` - perform a breadth-first search of ``exprTree``, returning the first match.

.. function:: matchOp(ruleTree, exprTree)

    Match the application of an operator.

    ``ruleTree`` is an operator token, with a list of operands.

    If it's a special operator, run the logic for that.

    Otherwise, match an ordinary operator:

    The operator being matched is the operator at the top of ``ruleTree``.

    The match is :dfn:`commutative` if the commutative :ref:`option <pattern-matching-options>` is turned on and the operator is commutative.

    The match is :dfn:`associative` if the associative :ref:`option <pattern-matching-options>` is turned on and the operator is associative.

    Run :func:`getTerms` to identify terms in ``ruleTree`` and ``exprTree``.

    If the match is not associative, and the expression is not an application of the operator being matched, and it's a unary operation, then there is no match.

    Run :func:`matchTermSequence` on the terms.
    Unmatched terms are allowed if the "Allow other terms" :ref:`option <pattern-matching-options>` is turned on and the match is associative.

    Collate the named groups: for names which are matched more than once, combine them.
    If the "Gather as a sequence" :ref:`option <pattern-matching-options>` is turned off, the name matches to a list with an entry for each time the name was matched.
    If it's turned on, the occurrences are joined together by applications of the operator.

    When gathering multiplicative terms as a sequence, the invented unary reciprocal operator must be removed: replace each instance of ``x*(/y)`` with ``x/y``.
    
    Capture the operator token under the name ``__op__``, to be used by a rewriting rule if there are unmatched terms in the sequence.

    The special matching operators specify quantifiers, allow for plus/minus or times/divide matches, or express combinations of patterns:

    **Quantifiers**:

    * ``subpattern`?`` - match ``subpattern`` if possible, otherwise ignore it.

    * ``subpattern`*`` - match any number of terms matching ``subpattern``.

    * ``subpattern`+`` - match one or more terms matching ``subpattern``.

    **Combining patterns**:

    * ``a `| b`` - "either ``a`` or ``b``".
      If ``exprTree`` matches pattern ``a``, return that, otherwise try to match ``b``.

    * ```! subpattern`` - "not ``subpattern``".
      ``exprTree`` only matches if it does not match ``subpattern``.

    * ``a `& b`` - "both ``a`` and ``b``".
      Test both ``a`` and ``b``, and combine their matched names.

    **Conditions**:

    * ``subpattern `where condition``.
      ``exprTree`` must match ``subpattern``, and then after substituting matched names into ``condition``, it must evaluate to ``true``.

    **Inverses**:

    * ```+- subpattern``. "Plus or minus ``subpattern``".
      ``exprTree`` must match either ``subpattern``, or ``-(subpattern)``.

    * ```*/ subpattern``. "``subpattern`` or its reciprocal".
      ``exprTree`` must match either ``subpattern``, or ``/(subpattern)``.
      The unary reciprocal operator is added when collecting the terms in a sequence, replacing ``x/y` with ``x*(/y)``.

    **Other special operators**:

    * ``subpattern `: v``. "Default value for missing term".
      When matching a sequence, if ``subpattern`` is not matched, then this term is matched as the default value ``v`` instead.

    * ``macros `@ subpattern``.
      ``macros`` is a dictionary mapping names to patterns.
      The macros are substituted into ``subpattern`` before running :func:`matchTree` to find a match.

.. function:: matchList(ruleTree, exprTree)

    ``ruleTree`` has a list token at the top, and its arguments are a sequence of patterns.

    If the token at the top of ``exprTree`` is not a list, return false.

    Consider the elements of both lists as a sequence of :class:`terms <Term>`.

    Run :func:`matchTermSequence` on the terms.

    Each matched name is captured as a list with an entry for each time the name was matched.

.. function:: matchToken(ruleTree, exprTree)

    There is a match if the tokens at the top of ``ruleTree`` and ``exprTree`` are equal.

.. _match-sequence:

Matching a sequence of terms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Function arguments, list elements, and the operands of associative operations are considered as sequences of terms.

Both the pattern and the expression being matched produce a sequence of terms.
The aim is to match up terms in the pattern with terms in the expression.
Quantifiers on each term in the pattern specify how many terms in the expression can match against it.

To identify a sequence, we might need to apply the law of associativity for binary operations.

When matching a sequence pattern we might need to apply the law of commutativity, to match terms which appear in a different order to that used in the pattern.

It's convenient when matching sums or products of terms to treat ``x-y`` as ``x+(-y)`` and ``x/y`` as ``x*(/y)``.
There's no conventional symbol for a unary "reciprocal" operator analogous to the unary "negation" operator, but it's useful here.

.. class:: Term(tree)

    A ``Term`` objects represents a single term in a sequence.

    The same :class:`Term` class is used for terms in both the pattern and the expression.
    Terms in the expression only fill in the ``tree`` property; the rest of the defined properties are only for terms in the pattern.

    .. property:: tree
        :type: Tree

        The syntax tree corresponding to this term, with the outermost quantifiers, default value operators, or capturing operators removed.

    .. property:: names

        Names under which this term should be captured.

    .. property:: inside_equalnames

        Names captured inside a quantifier that have an equality condition - each term matching this term will be considered individually for equality.

    .. property:: outside_equalnames

        Names captured outside a quantifier that have an equality condition - all terms matching this term will be grouped together, and then any later matches to the same name will be considered for equality with these as a single expression.

    .. property:: quantifier
        
        How many terms in the expression can match against this pattern term.

        Possible values:

        * ``0`` - this term must not match.
        * ``1`` - match once
        * ```?`` - match once or not at all.
        * ```*`` - match any number of times.
        * ```+`` - match at least once.

    .. property:: defaultValue

        A value to capture if this term is not matched.

    To compute these values, any special operators on the outside of the input ``tree`` are peeled off, one by one:

    The initial value of ``quantifier`` is ``1``, or ``0`` if the term is ``$z``.

    Quantifiers are pulled through unary operations, so ``-(x`?)`` is equivalent to ``(-x)`?``.

    ``;``
      Add a name to ``names``.

    ``;=``
      Add a name to ``names``, and also add it to ``outside_equalnames`` if a quantifier has not been encountered yet, or ``inside_equalnames`` otherwise.

    ```?``, ```*`` or ```+``
      Change ``quantifier``.

      There are precedence relations between the current value of ``quantifier`` and the one being unpeeled:
  
      * ``0`` takes precedence over all others.
      * ``1`` has the lowest precedence.
      * ```?`` followed by ```*`` or ```+``, or the other way round, produce ```*``.
      * Otherwise, the new quantifier takes precedence.
  
      ```:`` - set ``defaultValue``.
  
      If ``quantifier`` is ``1``, change it to ```?``.
      If it's ```+``, change it to ```*``.
      (Implicitly, this term is optional)

    Once these operators have been peeled off, the remaining tree is saved as the ``tree`` property.

    Finally, any more identified capturing operators ``;=`` inside the tree are found and saved.
    Those under a quantifier are ignored.


.. function:: getTerms(tree, op, commutative, associative, strictInverse)

    Given a ``tree`` representing a series of terms ``t1 op t_2 op t_3 op ... op t_n``, return the terms as a list of :class:`Term` objects.

    * If the top of the tree is a unary minus operation, move it inside the tree so that it applies to the leftmost factor.
      For example, rewrite ``-((x*y)*z)`` to ``((-x)*y)*z``.

    * If the "Strict inverse" :ref:`option <pattern-matching-options>` is not turned on, and ``op`` is ``+`` or ``*``, then replace ``x-y`` with ``x+(-y)`` and ``x/y`` with ``x*(/y)``.

    * If ``op`` is a binary relation, then we want to make sure that the operation and its converse are handled together.
      For example, ``>`` is the converse of ``<``.
      If ``op`` is ``<``, then replace all instances in the tree of ``a > b`` with ``b < a``.

    * If the token at the top of the tree is the operator ``op``, then ``args`` is the list of arguments.
      Otherwise, ``args`` is the list whose only element is ``tree``.

    * For each argument ``arg`` in ``args``:

      * Make a :class:`Term` object ``term`` containing ``arg``.

      * Remove any capturing operators ``;`` or ``;=`` from the top of ``arg``.

      * If ``op`` is ``*`` and the token at the top of ``arg`` is a unary minus, then remove that (the :class:`Term` object will remember that it's there).

      * If using associativity and the token at the top of ``arg`` is the operator ``op``, then split it into more terms:

        * Run :func:`getTerms` on ``arg`` to obtain a list of terms.

        * Add the captured names from ``item`` to each of these terms.

        * If the ``quantifier`` for ``item`` is not ``1``, then combine the quantifiers on each of these terms, using the same logic as used when constructing :class:`Term` objects.
          For example, ``(x`+ * y)`?`` is equivalent to ``x`* * y`?``.

        * Add each of these terms to the list of terms to output.

        Otherwise, add ``term`` to the list of terms to output.

      * Return the list of identified terms.


.. function:: matchTermSequence(ruleTerms, exprTerms, options)

    Given a list of rule terms and a list of expression terms, try to come up with an assignment of expression terms to rule terms.

    A rule term might match more than one expression term, if quantifiers allow.

    An expression term might not match any rule terms, if the "Allow other terms" :ref:`option <pattern-matching-options>` is turned on.
    In order to allow rewriting rules to keep terms in roughly the same order, we track whether unmatched expression terms are towards the start or the end of the expression.

    Keep track of what names have been matched for each term in the expression.

    An expression term ``exprTerm`` matches a rule term ``ruleTerm`` if :func:`matchTree(exprTerm.tree, ruleTerm.tree)` returns ``true``.

    An assignment is valid if, for each identified name captured in an
    expression term, it's equal to all matches of the
    name in previous terms.

    There might be more than one valid matching of expression terms to rule terms: an expression term could match several rule terms, and a rule term might have a quantifier that allows it to match different numbers of expression terms.
    If "Allow other terms" is turned on, then for each expression term we could decide not to try to match it at all.

    The strategy is to move the input pointer along the list of expression terms, trying to match them greedily with the first rule term they match against.
    If either pointer reaches the end of the corresponding list and there are any unmatched terms, then backtrack, either looking to match an expression term against a later rule, or if "Allow other terms" is turned on, don't match it at all.

    When the "Commutative" :ref:`option <pattern-matching-options>` is turned on, there are lots more possible matches, increasing the maximum running time of the algorithm.

    The process of finding a match works as follows.

    Define:

    ``capture`` 
      A list storing which pattern term each expression term is matched against.
      Values are either an index in the list ``ruleTerms`` or the constants ``UNCAPTURED``, ``START`` or ``END``, denoting a term that did not match a rule term, not captured, at the start of the sequence or at the end.
      Initially, every value in this list is ``UNCAPTURED``.

    ``start`` 
      The index of the first term in the expression to consider matching, initially ``0``, meaning the first term in the list.
      Terms before this are not included in the match.

    ``pc`` 
      'Pattern pointer' - a pointer into the list of rule terms.
      Initially ``0``, meaning the first term.

    ``ic``
      'Input pointer' - a pointer into the list of expression terms.
      Initially ``0``, meaning the first term.

    Consumed
      A rule term is :dfn:`consumed` if its quantifiers allow no more expression terms to be matched against it.

    Enough
      A rule term has :dfn:`had enough` if the number of expression terms matched against it is at least the minimum required by its quantifiers.

    To find a match, repeat the following **loop** until done:

    .. proof:algorithm:: Main loop

        * Move to the next unconsumed rule term: as long as the rule term pointed to by ``pc`` is consumed, increment ``pc``.

        * If the input pointer ``ic`` has reached the end of the expression terms:

          * Move to the next rule term that hasn't had enough: while the rule term at ``pc`` has had enough, increment ``pc``.

          * If ``pc`` has reached the end of the list of rule terms:

            * If there is any rule term that has not had enough, :ref:`find-sequence-match-backtrack`.

            * Otherwise, **this is a match**.

          * Otherwise, there are still some unmatched rule terms, so :ref:`find-sequence-match-backtrack`.

        * Otherwise, if the pattern pointer ``pc`` has reached the end of the rule terms, there are unconsumed expression terms:

          * If "Allow other terms" isturned on:

            * If "Commutative" is turned on, then mark the expression term pointed to by ``ic`` as ``END``, and :ref:`find-sequence-match-advance-input`.

            * Otherwise, capture all the remaining expression terms as ``END``, and move the input pointer ``ic`` to the end.

          * Otherwise, :ref:`find-sequence-match-backtrack`.

        * Otherwise, check if the expression term pointed to by ``ic`` matches the rule term pointed to by ``pc``.

          If it does, and all captured name assignments are valid, capture ``ic`` as matching ``pc`` and :ref:`find-sequence-match-advance-input`.

        * Otherwise, this expression term doesn't match the current rule term. 
          If "Commutative" is turned on, or if the rule terms pointed to by ``pc`` has had enough, increment ``pc``.

        * If none of those apply, :ref:`find-sequence-match-backtrack`.

    .. _find-sequence-match-backtrack:

    .. proof:algorithm:: Backtrack

        Find the last place we made a choice:

        * If "Allow other terms" is turned on, ``ic = start``, the number of captured terms is equal to ``start`` and less than the number of input terms, then try ignoring the term pointed to by ``ic``:

          Capture the expression term pointed to by ``ic`` as ``START``, and :ref:`find-sequence-match-increment-start`.

        * Otherwise:

          * Move ``ic`` back at least one place, to the last term before ``start`` or the last term not captured as ``END`` or ``UNCAPTURED``, whichever is last.

          * If ``ic < start``:

            * If "Allow other terms" is turned on and ``start`` is not at the end:

              * :ref:`find-sequence-match-increment-start`.

              * Capture all terms before ``start`` as ``START``.

            * Otherwise, there is no match: no expression terms have matched any rule terms.

          * Set ``pc`` to the position after the one which the expression term pointed to by ``ic`` is captured as (or just the end, if the term at ``ic`` is captured as ``END``).

          * Mark all expression terms after ``ic`` as ``UNCAPTURED``.

    .. _find-sequence-match-increment-start:

    .. proof:algorithm:: Increment ``start``

        * Set ``ic = start``, so we ignore expression terms before that.

        * Set ``pc = 0``, since we're effectively starting the matching process again with a smaller list of expression terms.

    .. _find-sequence-match-advance-input:

    .. proof:algorithm:: Advance input

        * Increment ``ic``.

        * If "Commutative" is turned on, set ``pc = 0``, so that each expression term can eventually be tried against every rule term.

    If a match is found, then we need to match up captured names from each term to produce a final match result.

    For each expression term ``exprTerm`` matched against a rule term ``ruleTerm``, record that ``exprTerm`` was matched against each of the names captured by ``ruleTerm``, and merge this with any names captured inside ``ruleTerm``.

    For each rule term with a :attr:`Term.defaultValue` that did not match any expression terms, match the default value against all the rule term's capturing names.

    Record expression terms captured as ``START`` or ``END`` in separate lists, as well as the operator.
    These will be used in :func:`rewrite`.

.. _simplification-rules:

Simplification rules
####################

A *simplification rule* is a term rewriting rule :math:`l \to r`.
For example, :math:`x \times (y \times z) \to (x \times y) \times z` changes the order in which a product of three terms is evaluated.
In this instance, :math:`x`, :math:`y` and :math:`z` are arbitrary sub-expressions.

If this rule was applied repeatedly to an arbitrarily bracketed product of several terms, the final expression would end up looking like:

.. math::

    (((\ldots (t_1 \times t_2) \times t_3) \ldots ) \times t_n)

.. _simplify-algorithm:

.. function:: simplify(rules,exprTree)

    Apply this loop:

    * First, :ref:`simplify <simplify-algorithm>` all arguments of :math:`exprTree`.

    * Find the first rule ``r`` in ``rules`` that matches ``exprTree``.

      If there is none, exit the loop, returning the latest version of ``exprTree``.

    * Use ``r`` to :ref:`rewrite <rewrite-algorithm>` ``exprTree``.

.. _rewrite-algorithm:

.. function:: rewrite(ruleTree, resultTree, exprTree)

    :ref:`Match <matching-a-pattern>` ``exprTree`` against ``ruleTree``.

    If there's no match, return ``exprTree`` unchanged.

    We now have a set of captured names, and a corresponding sub-expression for each of them constructed from parts of ``exprTree`` or default values defined in the rule.

    For names defined in ``ruleTree`` that did not capture anything, associate them with a 'nothing' value.

    For each name captured in the match, substitute the corresponding values into ``resultTree``.

    Apply post-replacement rules:

    * Replace ``eval(expr)`` with the result of evaluating ``expr``.

    * Replace binary operations where one argument is 'nothing' with just the other argument, i.e. replace ``nothing (op) x`` and ``x (op) nothing`` with ``x``.

    If the match has any expression terms that were ignored in :func:`matchTermSequence`, add these: using the recorded operator ``op``, ignored terms ``rest_start`` and ``rest_end``, and the rewritten tree ``result``, produce ``rest_start (op) result (op) rest_end``.

This is a naive algorithm - with the wrong set of rules, it can get stuck in an infinite loop.

Problems
--------

“Identified names”, when interacting with commutative match, needs some
kind of backtracking over trees.
For example, in order for ``?*?;=y + ?*?;=y`` to match ``3*x + x*5``, each of the additive terms
needs to know about the others while matching the product operation.
It's not enough just to tell the second term that the name :math:`y` has
been matched to :math:`x` in the first term: it might be that the first
term needs to match differently.

So the identified names should maybe be applied at the very end, to the
whole expression, but we then need a way of asking for “the next” way of
matching each set of terms.

