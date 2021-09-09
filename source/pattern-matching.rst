.. _pattern-matching:

Pattern-matching mathematical expressions
=========================================

.. page_status::
    :kind: in-progress

https://www.overleaf.com/project/5b92712d47e18a0f04cc4763

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

Things we want:

-  Match any sub-expression.

-  Consider all terms of an associative operation together, e.g. terms
   in a sum, joined by :math:`+` or :math:`-`.

-  Match if a subset of the terms match the given pattern, leaving the other terms unmatched.

-  Accept several different forms with the same rule, to avoid
   repetition, e.g. :math:`x+By` is a special case of :math:`Ax+By` with
   :math:`A=1`.

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
fundamentally pattern-matching and rewriting systems.

The problem is that how the algorithms in those systems work on a
technical level isn't well documented, and because Numbas runs entirely
on the client, we need an algorithm written in JavaScript.

Thanks to a very fruitful discussion with a couple of attendees at EAMS
2018, I came up with a rough description of the tools that a good
pattern-matching system should offer.

I've spent the time since then implementing the system, and in using it
I came up with some more features that greatly widened the range of
possible uses.


What is the right way to define a rewriting rule?

Match pattern → identify terms matched against parts of the pattern → write a new expression.

Want to avoid combinatorial explosion in the number of rules that must be defined (the algorithm might have exponential running time, though)

Need built-in matchers for common things, e.g. rational polynomials, complex numbers in Cartesian or polar form.

Associativity and commutativity of operations/terms sometimes matter, and sometimes don't.

Quantifiers are complicated.

How to capture a missing term with a default value?

How do you combine terms that are captured more than once?

Back-references would allow you to identify terms that should cancel, such as common factors/denominators.
But "back-reference" isn't well-defined when terms commute.

For the rewriting step, must be able to evaluate a captured term to an object that you can do arithmetic with.

Come up with a fairly readable (and writable) syntax for defining
patterns which match expressions.

Doesn't need to make immediate sense, but shouldn't be too complicated:
regular expressions don't make sense to someone who hasn't seen them
before, but there are very few things to learn.

Should be easy to diagram how it matches, like railway diagrams for
regular expressions.

Need a lot of new symbols for quantifiers, conjunctions and atoms.

I originally had lots of functions of the form ``m_X``, which led to
quite long and hard-to-read patterns.
Operators are a lot easier to read, especially the postfix quantifiers which look more like regex
quantifiers.

Once you've got pattern-matching, you can do lots of things:

* Check the form of an answer
* Symbolic differentiation and integration
* Canonical forms for (some classes of) expressions
* Other CAS techniques

Determining the form of an expression
#####################################

In a 'mathematical expression' question, the student's answer
:math:`f_{\mathrm{S}}` is an algebraic expression which must match the
teacher's expected answer :math:`f_{\mathrm{T}}`.
We can numerically establish that the student has given an equivalent expression by substituting values
for :math:`x` into both :math:`f_{\mathrm{S}}` and
:math:`f_{\mathrm{T}}`, but this tells us nothing about the *form* of
:math:`f_{\mathrm{S}}`.

Examples
~~~~~~~~

* The student must expand :math:`(x+\alpha)(x+\beta)`.
  The expanded expression will be of the form :math:`x^2+Ax+B`.
  Necessary conditions for 'expanded' include 'contains no brackets', and 'each term
  is an integer multiplied by a power of :math:`x`'.
  
  The opposite task, factorise :math:`x^2+Ax+B`, will produce an
  expression of the form :math:`(x+\alpha)(x+\beta)`.
  A condition for 'factorised' is 'the expression is a product of irreducible
  polynomials'.

* Write a complex number in argument-modulus form, :math:`re^{i\theta}` - :math:`r` and :math:`\theta` could be literal real numbers, or expressions producing real numbers.

Algorithm
---------

.. todo::

    Examples

.. todo::

    Stuff that doesn't work right at the moment:

    * Combining names that are captured in more than one place.

Similarities with regular expressions.
######################################

Similarities: quantifiers, choice.

Differences: and, condition.

Do we need positive/negative lookahead/lookbehind?

Syntax trees
############

A string representing a mathematical expression or pattern is parsed into a syntax tree.

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

Matching a pattern
##################

.. function:: matchTree(ruleTree, exprTree)

    To decide whether the given ``exprTree`` matches the given ``ruleTree``, and return any matched names if so.

    This algorithm operates recursively.
    Its behaviour depends on the type of the token at the top of ``ruleTree``:

    * A capturing operator: the rule must be of the form ``subRule ; name`` - if ``exprTree`` matches ``subRule``, then capture it under ``name``.

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
      Annotations can specify extra conditions, or match other kinds of numbers, such as fractions or complex numbers:

        * ``complex``
        * ``imaginary``
        * ``real``
        * ``positive``
        * ``nonnegative``
        * ``negative``
        * ``integer``
        * ``decimal``
        * ``rational``

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
    tree.

    The match is 'commutative' if the commutative :ref:`option <pattern-matching-options>` is turned on and the operator is commutative.

    The match is 'associative' if the associative :ref:`option <pattern-matching-options>` is turned on and the operator is associative.

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

.. function:: matchToken(ruleTree, exprTree);

    There is a match if the tokens at the top of ``ruleTree`` and ``exprTree`` are equal.

Matching a sequence of terms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Function arguments, list elements, and the operands of associative operations are considered as sequences of terms.

Both the pattern and the expression being matched produce a sequence of terms.
The aim is to match up terms in the pattern with terms in the expression.
Quantifiers on each term in the pattern specify how many terms in the expression can match against it.

The same :class:`Term` class is used for terms in both the pattern and the expression.
Terms in the expression only fill in the ``term`` property.

.. class:: Term(tree)

    A ``Term`` objects represents a single term in a sequence.

    .. property:: term 
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

    * ``;`` - add a name to ``names``.

    * ``;=`` - add a name to ``names``, and also add it to ``outside_equalnames`` if a quantifier has not been encountered yet, or ``inside_equalnames`` otherwise.

    * ```?``, ```*`` or ```+`` - change ``quantifier``.

      There are precedence relations between the current value of ``quantifier`` and the one being unpeeled:

      * ``0`` takes precedence over all others.
      * ``1`` has the lowest precedence.
      * ```?`` followed by ```*`` or ```+``, or the other way round, produce ```*``.
      * Otherwise, the new quantifier takes precedence.

    * ```:`` - set ``defaultValue``.

      If ``quantifier`` is ``1``, change it to ```?``.
      If it's ```+``, change it to ```*``.
      (Implicitly, this term is optional)

    Once these operators have been peeled off, the remaining tree is saved as the ``term`` property.

    Finally, any more identified capturing operators ``;=`` inside the tree are found and saved.
    Those under a quantifier are ignored.


.. function:: getTerms(tree, op, commutative, associative, strictInverse)

    Given a ``tree`` representing a series of terms ``t1 op t_2 op t_3 op ... op t_n``, return the terms as a list of :class:`Term` objects.


    .. code-block:: javascript

        /** Options for {@link Numbas.jme.rules.getTerms}.
         *
         * @typedef Numbas.jme.rules.getTerms_options
         * @type {object}
         * @property {boolean} commutative - Should the operator be considered as commutative, for the purposes of matching ops with opposites? If yes, `a>c` will produce terms `c` and `a` when `op='<'`.
         * @property {boolean} associative - Should the operator be considered as associative? If yes, `(a+b)+c` will produce three terms `a`,`b` and `c`. If no, it will produce two terms, `(a+b)` and `c`.
         * @property {boolean} strictInverse - If `false`, `a-b` will be interpreted as `a+(-b)` when finding additive terms.
         */

        /** Information to do with a term found in an expression by {@link Numbas.jme.rules.getTerms}.
         *
         * @typedef Numbas.jme.rules.term
         * @type {object}
         * @property {Numbas.jme.tree} term
         * @property {Array.<string>} names - Names captured by this term.
         * @property {Array.<string>} equalnames - Identified names captured by this term.
         * @property {string} quantifier - Code describing how many times the term can appear, if it's a pattern term.
         * @property {number} min - The minimum number of times the term must appear.
         * @property {number} max - The maximum number of times the term can appear.
         * @property {Numbas.jme.tree} defaultValue - A value to use if this term is missing.
         */

        /** Replacements to make when identifying terms in a sequence of applications of a given op.
         * When looking for terms joined by `op`, `nonStrictReplacements[op]` is a list of objects with keys `op` and `replacement`. 
         * A tree `A op B` should be replaced with `replacement(tree)`.
         * For example, `x-y` should be rewritten to `x+(-y)`.
         */
        var nonStrictReplacements = {
            '+': {
                '-': function(tree) {
                    return {tok: new jme.types.TOp('+',false,false,2,true,true), args: [tree.args[0],insertUnaryMinus(tree.args[1])]};
                }
            },
            '*': { 
                '/': function(tree) {
                    tree = {tok: new jme.types.TOp('*',false,false,2,true,true), args: [tree.args[0],{tok:new jme.types.TOp('/u',false,true,1,false,false),args:[tree.args[1]]}]};
                    return tree;
                }
            }
        };

        /** Dictionary of 'canonical' ops to match in non-strict mode.
         * For example, `a-b` will be matched as `a+(-b)`.
         */
        var nonStrictCanonicalOps = {
            '-': '+',
            '/': '*'
        }

        /** Insert a unary minus in this tree.
         * If it's a product, the minus applies to the leftmost factor.
         *
         * @param {Numbas.jme.tree} tree
         * @returns {Numbas.jme.tree}
         */
        function insertUnaryMinus(tree) {
            if(jme.isOp(tree.tok,'*')) {
                return {tok: tree.tok, args: [insertUnaryMinus(tree.args[0]),tree.args[1]]};
            } else if(jme.isOp(tree.tok,'/')) {
                return {tok: tree.tok, args: [insertUnaryMinus(tree.args[0]),tree.args[1]]};
            } else {
                return {tok: new jme.types.TOp('-u',false,true,1,false,false), args: [tree]};
            }
        }

        /** Given a tree representing a series of terms t1 <op> t2 <op> t3 <op> ..., return the terms as a list.
         *
         * @memberof Numbas.jme.rules
         * @param {Numbas.jme.tree} tree - The tree to find terms in.
         * @param {string} op - The name of the operator whose terms are to be found.
         * @param {Numbas.jme.rules.getTerms_options} options
         * @param {boolean} calculate_minimum - Should the minimum allowed number of occurrences of each term be calculated? This is a pre-process step when getting the terms in a pattern expression.
         * @returns {Array.<Numbas.jme.rules.term>}
         */
        var getTerms = Numbas.jme.rules.getTerms = function(tree,op,options,calculate_minimum) {
            /** Add the list of existing names passed in at the start to each term.
             *
             * @param {Array.<Numbas.jme.rules.term>} items
             * @param {Array.<Numbas.jme.tree>} existing_names - Names captured higher up the tree.
             * @param {Array.<Numbas.jme.tree>} existing_equal_names - Identified names captured higher up the tree.
             * @returns {Array.<Numbas.jme.rules.term>}
             */
            function add_existing_names(items,existing_names,existing_equal_names) {
                return existing_names.length==0 && existing_equal_names.length==0 ? items : items.map(function(item) {
                    return {
                        term: item.term, 
                        names: existing_names.concat(item.names),
                        inside_equalnames: item.inside_equalnames,
                        outside_equalnames: existing_equal_names.concat(item.outside_equalnames),
                        quantifier: item.quantifier, 
                        min: item.min, 
                        max: item.max,
                        defaultValue: item.defaultValue,
                    };
                });
            }

            // we'll cache the results of this call in the tree object, to save time if the same thing is asked for again
            var intree = tree;
            if(intree.terms === undefined) {
                intree.terms = {};
            }
            if(intree.terms[op] === undefined) {
                intree.terms[op] = {};
            }
            var option_signature = options.associative*2 + (options.strictInverse);

            if(intree.terms[op][option_signature]) {
                return intree.terms[op][option_signature];
            }


            if(jme.isOp(tree.tok,'-u') && op=='*') {
                tree = insertUnaryMinus(tree.args[0]);
            }

            if(!options.strictInverse && op in nonStrictReplacements) {
                for(var subop in nonStrictReplacements[op]) {
                    if(jme.isOp(tree.tok,subop)) {
                        tree = nonStrictReplacements[op][subop](tree);
                    }
                };
            }

            /** Is the given token the op we're looking for?
             * True if it's literally that operator, it's the converse of that operator, or it would be replaced to that op in non-strict mode.
             *
             * @param {Numbas.jme.token} tok
             * @returns {boolean}
             */
            function isThisOp(tok) {
                if(jme.isOp(tok,op)) {
                    return true;
                }
                if(options.commutative && jme.converseOps[op] && jme.isOp(tok,jme.converseOps[op])) {
                    return true;
                }
                if(!options.strictInverse && op in nonStrictReplacements && tok.type=='op' && tok.name in nonStrictReplacements[op]) {
                    return true;
                }
            }

            var args = jme.isOp(tree.tok,op) ? tree.args : [tree];
            if(options.commutative && jme.converseOps[op] && jme.isOp(tree.tok,jme.converseOps[op])) {
                args = tree.args.slice().reverse();
            }

            var terms = [];

            for(var i=0; i<args.length;i++) {
                var arg = args[i];
                var item = new Term(arg);
                var res = unwrapCapture(arg);
                var argtok = res.tree.tok;
                if(op=='*' && jme.isOp(argtok,'-u')) {
                    argtok = unwrapCapture(args[i].args[0]).tree.tok;
                }
                if(options.associative && (isThisOp(argtok) || (!options.strictInverse && op=='+' && jme.isOp(argtok,'-')))) {
                    var sub = getTerms(res.tree,op,options,false);
                    sub = add_existing_names(sub,item.names,item.outside_equalnames);
                    if(item.quantifier!='1') {
                        sub = sub.map(function(t){ t.quantifier = quantifier_combo[t.quantifier][item.quantifier]; });
                    }
                    terms = terms.concat(sub);
                } else {
                    if(item.max>0) {
                        terms.push(item);
                    }
                }
            }

            if(calculate_minimum) {
                terms.min_total = 0;
                terms.forEach(function(t) {
                    terms.min_total += t.min;
                });
            }

            intree.terms[op][option_signature] = terms;
            return terms;
        }



Simplification rules
####################

A *simplification rule* is a term rewriting rule :math:`l \to r`.
For example, :math:`x \times (y \times z) \to (x \times y) \times z` changes the order in which a product of three terms is evaluated.
In this instance, :math:`x`, :math:`y` and :math:`z` are arbitrary
sub-expressions.

If this rule was applied repeatedly to an arbitrarily bracketed product of several terms, the final expression would end up looking like:

.. math::

    (((\ldots (t_1 \times t_2) \times t_3) \ldots ) \times t_n)

The process of 'simplification' works as follows, starting with an
input tree :math:`T` and a list of rules :math:`R`:

* First, simplify all arguments of :math:`T`.

* Apply this loop:

  * Find the first rule :math:`r \in R` that matches :math:`T`
    If there is none, exit the loop.

  * Use :math:`r` to rewrite :math:`T`.

.. class:: Rule

    The ``Rule`` object represents a pattern-matching rule.
    It can also provide a transformation for matched expressions, making it a rewriting rule.

    .. property:: pattern 
        :type: Tree

        A tree representing the pattern to match.

    .. property:: result
        :type: Tree

        A tree representing the transformation this rewriting rule represents - names matched in :attr:`pattern` are substituted into this.

    .. property:: options

        :ref:`pattern-matching-options` dictating how the pattern matches.


    .. code-block:: javascript

        /** Simplification rule.
         *
         * @memberof Numbas.jme.rules
         * @class
         *
         * @param {JME} pattern - Expression pattern to match. Variables will match any sub-expression.
         * @param {JME} result - Expression pattern to rewrite to.
         * @param {string|Numbas.jme.rules.matchTree_options} options
         * @param {string} [name] - A human-readable name for the rule
         *
         * @property {JME} patternString - The JME string defining the pattern to match.
         * @property {JME} resultString - The JME string defining the result of the rule.
         * @property {Numbas.jme.rules.matchTree_options} options - Default options for the match algorithm.
         * @property {JME} conditionStrings - JME strings defining the conditions.
         * @property {Numbas.jme.tree} patternTree - `patternString` compiled to a syntax tree.
         * @property {Numbas.jme.tree} result - The parameter `result` compiled to a syntax tree.
         * @property {Numbas.jme.tree[]} conditions - The parameter `conditions` compiled to syntax trees.
         */
        var Rule = jme.rules.Rule = function(pattern,result,options,name) {
            this.name = name;
            this.patternString = pattern;
            this.pattern = patternParser.compile(pattern);
            if(typeof(options)=='string') {
                options = parse_options(options);
            }
            this.options = options || {};
            this.resultString = result;
            this.result = jme.compile(result);
        }
        Rule.prototype = /** @lends Numbas.jme.rules.Rule.prototype */ {
            toString: function() {
                return this.patternString+' -> '+this.resultString;
            },

            /** Extend this rule's default options with the given options.
             *
             * @param {Numbas.jme.rules.matchTree_options} options
             * @returns {Numbas.jme.rules.matchTree_options}
             */
            get_options: function(options) {
                if(!options) {
                    return this.options;
                } else {
                    return extend_options(this.options,options);
                }
            },
            /** Match a rule on given syntax tree.
             *
             * @memberof Numbas.jme.rules.Rule.prototype
             * @param {Numbas.jme.tree} exprTree - The syntax tree to test.
             * @param {Numbas.jme.Scope} scope - Used when checking conditions.
             * @returns {boolean|Numbas.jme.rules.jme_pattern_match} - `false` if no match, or a dictionary of matched subtrees.
             * @see Numbas.jme.rules.matchTree
             */
            match: function(exprTree,scope) {
                return matchTree(this.pattern,exprTree,this.get_options({scope:scope}));
            },

            /** Find all matches for the rule, anywhere within the given expression.
             *
             * @param {Numbas.jme.tree} exprTree - The syntax tree to test.
             * @param {Numbas.jme.Scope} scope - Used when checking conditions.
             * @returns {Array.<Numbas.jme.rules.jme_pattern_match>}
             * @see {Numbas.jme.rules.matchAllTree}
             */
            matchAll: function(exprTree,scope) {
                return matchAllTree(this.pattern,exprTree,this.get_options({scope:scope}));
            },

            /** Transform the given expression if it matches this rule's pattern.
             *
             * @param {Numbas.jme.tree} exprTree - The syntax tree to transform.
             * @param {Numbas.jme.Scope} scope - Used when checking conditions.
             * @returns {Numbas.jme.rules.transform_result}
             * @see Numbas.jme.rules.transform
             */
            replace: function(exprTree,scope) {
                return transform(this.pattern, this.result, exprTree, this.get_options({scope:scope}));
            },

            /** Transform all occurences of this rule's pattern in the given expression.
             *
             * @param {Numbas.jme.tree} exprTree - The syntax tree to transform.
             * @param {Numbas.jme.Scope} scope - Used when checking conditions.
             * @returns {Numbas.jme.rules.transform_result}
             * @see Numbas.jme.rules.transform
             */
            replaceAll: function(exprTree,scope) {
                return transformAll(this.pattern, this.result, exprTree, this.get_options({scope: scope}));
            }
        }


.. _match-sequence:

Sequences
#########

Many routines rely on matching sequences of terms, either joined by associative operations of equal precedence, or a tuple.

To identify a sequence, we might need to apply the law of associativity for binary operations.

When matching a sequence pattern we might need to apply the law of commutativity, to match terms which appear in a different order to that used in the pattern.

It's convenient when matching sums or products of terms to treat ``x-y`` as ``x+(-y)`` and ``x/y`` as ``x*(/y)``.
There's no conventional symbol for a unary "reciprocal" operator analogous to the unary "negation" operator, but it's useful here.

.. function:: matchTermSequence

    Given a list of rule terms and a list of expression terms, return a
    dictionary mapping captured names to lists of expressions matched
    against them.

    Keep track of what names have been matched for each term in the
    expression.

    Try to come up with an assignment of expression terms to rule terms,
    'ignored start', or 'ignored end'.
    A rule term might match more than one expression term, if quantifiers allow.

    An expression term matches a rule term if matchTree returns true.

    An assignment is valid if, for each identified name captured in an
    expression term, it's equal under compareTrees to all matches of the
    name in previous terms.

    Run ``findSequenceMatch`` to find an acceptable assignment.

    pretend the default value matched it.
    merge captured names from each expression term.

    add the expression to the corresponding list.

    Capture any ignored terms as ``rest_start``, ``rest_end`` and collected
    together as ``rest``.

    .. code-block:: javascript

        /** Match a sequence of terms.
         * Calls {@link Numbas.jme.rules.findSequenceMatch}, and uses {@link Numbas.jme.rules.matchTree} to match individual terms up.
         *
         * @param {Array.<Numbas.jme.rules.Term>} ruleTerms - The terms in the pattern.
         * @param {Array.<Numbas.jme.rules.Term>} exprTerms - The terms in the expression.
         * @param {boolean} commuting - Can the terms match in any order?
         * @param {boolean} allowOtherTerms - Allow extra terms which don't match any of the pattern terms?
         * @param {Numbas.jme.rules.matchTree_options} options
         * @param {Numbas.jme.rules.matchTree_options} term_options - Options to use when matching individual terms.
         * @returns {boolean|object.<Numbas.jme.jme_pattern_match>} - False if no match, or a dictionary mapping names to lists of subexpressions matching those names (it's up to whatever called this to join together subexpressions matched under the same name).
         */
        function matchTermSequence(ruleTerms, exprTerms, commuting, allowOtherTerms, options, term_options) {
            term_options = term_options || options;
            var matches = {};
            exprTerms.forEach(function(_,i){ matches[i] = {} });

            /** Does the given input term match the given rule term?
             * The indices of the input and rule terms are given so the result of the match can be cached.
             *
             * @param {Numbas.jme.rules.term} exprTerm - The input term.
             * @param {Numbas.jme.rules.term} ruleTerm - The term in the pattern which must be matched.
             * @param {number} ic - The index of the input term.
             * @param {number} pc - The index of the rule term.
             * @returns {boolean}
             */
            function term_ok(exprTerm,ruleTerm,ic,pc) {
                if(matches[ic][pc]===undefined) {
                    var m = matchTree(ruleTerm.term,exprTerm.term,term_options);
                    var inside_equalnames = {};
                    ruleTerm.inside_equalnames.forEach(function(name) {
                        if(m[name]) {
                            inside_equalnames[name] = m[name];
                        } else if(ruleTerm.names.some(function(n){return resolveName(n).name==name})) {
                            inside_equalnames[name] = m._match;
                        }
                    });
                    var outside_equalnames = {};
                    ruleTerm.outside_equalnames.forEach(function(name) {
                        if(m[name]) {
                            outside_equalnames[name] = m[name];
                        } else if(ruleTerm.names.some(function(n){return resolveName(n).name==name})) {
                            outside_equalnames[name] = m._match;
                        }
                    });
                    matches[ic][pc] = {
                        match: m,
                        inside_equalnames: inside_equalnames,
                        outside_equalnames: outside_equalnames
                    }
                }
                return matches[ic][pc].match!==false; 
            }

            /** Does the given assignment satisfy the constraints of the matching algorithm?
             * At the moment, the only constraint is that all subexpressions matched with the same name using the `;=` operator must be equal, according to {@link Numbas.jme.compareTrees}.
             *
             * @param {object} assignment - The result of {@link Numbas.jme.rules.findSequenceMatch}.
             * @param {number} ic - The current index in the list of input terms. Only matches introduced by this term are considered - previous terms are assumed to have already passed the constraint check.
             * @param {number} pc - The current index in the list of pattern terms.
             * @returns {boolean}
             */
            function constraint_ok(assignment,ic,pc) {
                var m1 = matches[ic][pc];
                var ruleTerm = ruleTerms[pc];
                if(ruleTerm.inside_equalnames.length==0 && ruleTerm.outside_equalnames.length==0) {
                    return true;
                }
                var ok = assignment.every(function(p,i) {
                    if(p<0 || p>=ruleTerms.length) {
                        return true;
                    }
                    var m2 = matches[i][p];
                    var equalnames = p==pc ? 'inside_equalnames' : 'outside_equalnames';
                    return ruleTerm[equalnames].every(function(name) {
                        var e1 = m1[equalnames][name];
                        var e2 = m2[equalnames][name];
                        if(e1===undefined || e2===undefined) {
                            return true;
                        }
                        var res = jme.compareTrees(e1, e2) == 0;
                        return res;
                    });
                });
                return ok;
            }

            var assignment = findSequenceMatch(ruleTerms,exprTerms,{checkFn: term_ok, constraintFn: constraint_ok, commutative: commuting, allowOtherTerms: allowOtherTerms});
            if(assignment===false) {
                return false;
            }

            var namedTerms = {};

            var identified_names = {};
            ruleTerms.forEach(function(ruleTerm,i) {
                var equalnames = ruleTerm.outside_equalnames;
                equalnames.forEach(function(name) {
                    identified_names[name] = identified_names[name] || ruleTerm;
                });
            });
            /** Record that `exprTree` was captured with the given name.
             *
             * @param {string} name
             * @param {Numbas.jme.tree} exprTree
             * @param {Numbas.jme.rules.Term} ruleTerm
             * @param {boolean} allowReservedName - If `false`, reserved names such as `_match` and `_rest`, which are introduced by the matching algorithm, will be ignored.
             */
            function nameTerm(name,exprTree,ruleTerm,allowReservedName) {
                if(!allowReservedName && name.match(/^_/)) {
                    return;
                }
                if(!namedTerms[name]) {
                    namedTerms[name] = [];
                }
                if(identified_names[name]!==undefined && identified_names[name]!==ruleTerm && namedTerms[name].length) {
                    return;
                }
                namedTerms[name].push(exprTree);
            }
            /** Record that `exprTree` was matched against `ruleTerm` - add `exprTree` to all of `ruleTerm`'s names.
             *
             * @param {Numbas.jme.rules.term} ruleTerm
             * @param {Numbas.jme.tree} exprTree
             */
            function matchTerm(ruleTerm,exprTree){ 
                ruleTerm.names.forEach(function(name) {
                    var o = resolveName(name,exprTree);
                    nameTerm(o.name,o.value,ruleTerm);
                });
            }

            assignment.result.forEach(function(is,j) {
                var ruleTerm = ruleTerms[j];

                if(is.length) {
                    is.forEach(function(i) {
                        var match = matches[i][j].match;
                        for(var name in match) {
                            nameTerm(name,match[name],ruleTerm);
                        }
                        matchTerm(ruleTerm,exprTerms[i].term);
                    });
                } else if(ruleTerm.defaultValue) {
                    matchTerm(ruleTerm,ruleTerm.defaultValue);
                }
            });
            assignment.ignored_start_terms.forEach(function(i) {
                nameTerm('_rest',exprTerms[i].term,undefined,true);
                nameTerm('_rest_start',exprTerms[i].term,undefined,true);
            });
            assignment.ignored_end_terms.forEach(function(i) {
                nameTerm('_rest',exprTerms[i].term,undefined,true);
                nameTerm('_rest_end',exprTerms[i].term,undefined,true);
            });

            return namedTerms;
        }

.. function:: findSequenceMatch

    Given a sequence of rule terms and a sequence of expression terms;
    routines to decide if an expression term matches a rule term, and if an
    assignment satisfies all constraints.
    Return an array containing a list of expression terms matched against each rule term, and lists of ignored
    terms at the start and end of the expression sequence.

    Each rule term has a minimum and a maximum bound on the number of times
    it must be matched.

    The match can be commutative, in which case expression terms can match
    out of order, and optionally allow expression terms to be ignored in
    order to obtain a match with the remainder.

    This is a backtracking algorithm.

    .. code-block:: javascript

        /** Options for {@link Numbas.jme.rules.findSequenceMatch}.
         *
         * @type {object}
         * @typedef Numbas.jme.rules.findSequenceMatch_options
         * @property {boolean} allowOtherTerms - If `true`, terms that don't match any term in the pattern can be ignored.
         * @property {boolean} commutative - Can the input terms be considered in any order?
         * @property {Function} constraintFn - Function to test if the current set of matches satisfies constraints.
         * @property {Function} checkFn - Function to test if an input term matches a given pattern term.
         */

        /** Match a sequence of terms against a given pattern sequence of terms.
         * Try to find an assignment of input terms to the pattern, satisfying the quantifier for each term in the pattern.
         * The match is greedy - input terms will match earlier pattern terms in preference to later ones.
         *
         * @function
         * @memberof Numbas.jme.rules
         *
         * @param {Array.<Numbas.jme.rules.term>} pattern
         * @param {Array.<Numbas.jme.tree>} input
         * @param {Numbas.jme.rules.findSequenceMatch_options} options
         * @returns {object} - `ignored_start_terms` is terms at the start that weren't used in the match, `ignored_end_terms` is any other terms that weren't used, and `result[i]` is a list of indices of terms in the input that were matched against pattern term `i`.
         */
        var findSequenceMatch = jme.rules.findSequenceMatch = function(pattern,input,options) {
            var capture = [];
            var start = 0;
            var done = false;
            var failed = false;
            var pc = 0;
            var ic = 0;

            /** Count the number of times we have matched pattern term `p` so far.
             *
             * @param {number} p - The index of the term.
             * @returns {number}
             */
            function count(p) {
                return capture.filter(function(x){return x==p}).length;
            }
            /** Have we consumed pattern term `p` as many times as allowed?
             *
             * @param {number} p
             * @returns {boolean}
             */
            function consumed(p) {
                return count(p)>=pattern[p].max;
            }
            /** Have we matched this pattern term at least its minimum number of times?
             *
             * @param {number} p - The index of the pattern term.
             * @returns {boolean}
             */
            function enough(p) {
                return count(p)>=pattern[p].min;
            }
            /** Move the start pointer along one.
             * Terms before the start will be returned in `ignored_start_terms`.
             */
            function increment_start() {
                //debug('increment start position');
                start += 1;
                ic = start;
                pc = 0;
            }
            /** Backtrack to the last time we made a free choice.
             * If we're already at the start and `allowOtherTerms` is enabled, advance the start pointer.
             */
            function backtrack() {
                //debug('backtrack');
                if(options.allowOtherTerms && ic==start && capture.length==start && start<input.length-1) {
                    capture.push(-1);
                    increment_start();
                    return;
                } 
                
                ic -= 1;
                while(ic>=start && (ic>=capture.length || capture[ic]>=pattern.length)) {
                    ic -= 1;
                }
                //debug('backtracked to '+ic);

                if(ic<start) {
                    if(options.allowOtherTerms && start<input.length-1) {
                        capture = [];
                        increment_start();
                        for(var i=0;i<start;i++) {
                            capture.push(-1);
                        }
                        return;
                    } else {
                        failed = true;
                        return;
                    }
                }
                pc = capture[ic]+1;
                capture = capture.slice(0,ic);
            }
            /** Move the input pointer along one.
             * If using commutativity, set the pattern pointer back to the start.
             */
            function advance_input() {
                ic += 1;
                if(options.commutative) {
                    pc = 0;
                }
            }
            var steps = 0;
            while(!done && !failed) {
                //show();
                steps += 1;
                while(pc<pattern.length && consumed(pc)) { // if have consumed this term fully, move on
                    //debug('term '+pc+' consumed, move on');
                    pc += 1;
                }
                if(ic==input.length) { // if we've reached the end of the input
                    while(pc<pattern.length && enough(pc)) {
                        //debug('got enough of '+pc+', skip forward');
                        pc += 1;
                    }
                    if(pc==pattern.length) { // if we've consumed all the terms
                        if(!pattern.every(function(_,p) { return enough(p); })) {
                            //debug('reached end but some terms not matched enough times');
                            backtrack();
                        } else {
                            //debug('reached end of pattern and end of input: done');
                            done = true;
                        }
                    } else {
                        //debug('end of input but still pattern to match')
                        backtrack();
                    }
                } else if(pc>=pattern.length) {
                    //debug("end of pattern but unconsumed input");
                    if(pc==pattern.length && options.commutative && options.allowOtherTerms) {
                        //debug('capturing '+ic+' as ignored end term');
                        capture.push(pattern.length);
                        advance_input();
                    } else if(pc==pattern.length && !options.commutative && options.allowOtherTerms) {
                        while(ic<input.length) {
                            //debug('capturing '+ic+' as ignored end term');
                            capture.push(pattern.length);
                            advance_input();
                        }
                    } else {
                        backtrack();
                    }
                } else if(options.checkFn(input[ic],pattern[pc],ic,pc) && options.constraintFn(capture,ic,pc)) {
                    //debug('capture '+ic+' at '+pc);
                    capture.push(pc);
                    advance_input();
                } else if(options.commutative || enough(pc)) {
                    //debug('trying the next pattern term');
                    pc += 1;
                } else {
                    //debug('can\'t match next input')
                    backtrack();
                }
            }
            if(failed) {
                return false;
            }
            var result = pattern.map(function(p,i) {
                return capture.map(function(_,j){return j}).filter(function(j){ return capture[j] == i;});
            });
            if(options.commutative) {
                var ignored_start_terms = [];
                var ignored_end_terms = [];
                var ignored = ignored_start_terms;
                capture.forEach(function(p,i) {
                    if(p==pattern.length) {
                        ignored.push(i);
                    } else {
                        ignored = ignored_end_terms;
                    }
                });
            } else {
                var ignored_start_terms = input.slice(0,start).map(function(_,j){return j});
                var ignored_end_terms = capture.map(function(_,j){return j}).filter(function(j){return capture[j]==pattern.length});
            }
            //debug(result);
            return {ignored_start_terms: ignored_start_terms, result: result, ignored_end_terms: ignored_end_terms};
        }


.. _pattern-matching-options:

Options
#######

-  Commutative - When matching terms joined by a commutative operation
   such as :math:`\times` or :math:`+`, match terms in any order.

-  Associative - When matching terms joined by an associative operation,
   collect as many terms as possible to match at once, instead of just
   the two subtrees of the first application of the operation. 
   e.g., :math:`(a+b)+c` is matched as a list of three terms :math:`a`,
   :math:`b`, :math:`c`, not two terms :math:`a+b` and :math:`c`.

-  Allow other terms - Match a sequence of terms where the pattern is
   satisfied by a subset of the terms. e.g., :math:`1+2+x` matches
   ``n +n`` - the extra :math:`x` is ignored. In a non-commutative
   match, the pattern must match a contiguous subsequence of the terms.

-  Strict inverse - If turned off, ``x-y`` will be considered as
   ``x+(-y)``, so will match patterns like ``?+?``.
   Similar for ``x/y`` being interpreted as ``x*(/y)``.
   If turned on, plus means plus!

- Gather as a sequence - If turned off, then multiple terms matched under the same name will be stored in a list.
  If turned on, then they will be captured as a sequence of terms joined by the same operator used to find them, e.g. addition or multiplication.


.. function:: matchAnywhere

    .. code-block:: javascript

        /** Match if the given pattern occurs as a subexpression anywhere in the given expression.
         *
         * @param {Numbas.jme.tree} ruleTree
         * @param {Numbas.jme.tree} exprTree
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {boolean|Numbas.jme.jme_pattern_match}
         */
        function matchAnywhere(ruleTree,exprTree,options) {
            var m = matchTree(ruleTree,exprTree,options);
            if(m!==false) {
                return m;
            }
            if(exprTree.args) {
                for(var i=0;i<exprTree.args.length;i++) {
                    var am = matchAnywhere(ruleTree,exprTree.args[i],options);
                    if(am!==false)  {
                        return am;
                    }
                }
            }
            return false;
        }

.. function:: matchGenericOp

    .. code-block:: javascript

        /** Match the application of any operator. The first argument of `ruleTree` is a pattern that the operator's name, considered as a string, must satisfy, and the second argument is a pattern that the operator's arguments, considered as a list, must satisfy.
         *
         * @param {Numbas.jme.tree} ruleTree - The pattern to match.
         * @param {Numbas.jme.tree} exprTree - The expression being considered.
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {boolean|Numbas.jme.jme_pattern_match}
         */
        function matchGenericOp(ruleTree,exprTree,options) {
            if(exprTree.tok.type!='op') {
                return false;
            }
            var nameRule = ruleTree.args[0];
            var argsRule = ruleTree.args[1];
            var exprNameTree = {tok: new jme.types.TString(exprTree.tok.name)};
            var argsTree = {tok: new jme.types.TList(), args: exprTree.args};
            var m_name = matchTree(nameRule, exprNameTree, options);
            var m_args = matchTree(argsRule, argsTree, options);
            if(m_name && m_args) {
                return mergeMatches([m_name,m_args]);
            } else {
                return false;
            }
        }

.. function:: matchWhere

    .. code-block:: javascript

        /** Match a `where` condition - the expression must match the given pattern, and the condition specified in terms of the matched names must evaluate to `true`.
         *
         * @param {Numbas.jme.tree} pattern - The pattern to match.
         * @param {Numbas.jme.tree} condition - The condition to evaluate.
         * @param {Numbas.jme.tree} exprTree - The expression being considered.
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {boolean|Numbas.jme.jme_pattern_match}
         */
        function matchWhere(pattern,condition,exprTree,options) {
            var scope = new Numbas.jme.Scope(options.scope);

            var m = matchTree(pattern,exprTree,options);
            if(!m) {
                return false;
            }

            condition = Numbas.util.copyobj(condition,true);
            condition = jme.substituteTree(condition,new jme.Scope([{variables:m}]),true);
            try {
                var cscope = new jme.Scope([scope,{variables:m}]);
                var result = cscope.evaluate(condition,null,true);
                if(result.type=='boolean' && result.value==false) {
                    return false;
                }
            } catch(e) {
                return false;
            }
            return m;
        }

.. function:: matchMacro

    .. code-block:: javascript

        /** Substitute sub-patterns into a bigger pattern before matching.
         *
         * @param {Numbas.jme.tree} subPatterns - A dictionary of patterns.
         * @param {Numbas.jme.tree} pattern - The pattern to substitute into.
         * @param {Numbas.jme.tree} exprTree - The expression being considered.
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {boolean|Numbas.jme.jme_pattern_match}
         */
        function matchMacro(subPatterns, pattern, exprTree, options) {
            if(subPatterns.tok.type!='dict') {
                throw(new Numbas.Error('jme.matchTree.match macro first argument not a dictionary'));
            }
            var d = {}
            subPatterns.args.forEach(function(keypair) {
                var name = keypair.tok.key;
                var tree = keypair.args[0];
                d[name] = tree;
            });
            pattern = jme.substituteTree(pattern,new jme.Scope([{variables:d}]),true);
            return matchTree(pattern,exprTree,options)
        }

.. function:: matchOrdinaryFunction

    .. code-block:: javascript

        /** Match the application of a function.
         * Matches if the expression is the application of the same function, and all of the arguments match the arguments of the pattern.
         *
         * @param {Numbas.jme.tree} ruleTree - The pattern to match.
         * @param {Numbas.jme.tree} exprTree - The expression being considered.
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {boolean|Numbas.jme.jme_pattern_match}
         */
        function matchOrdinaryFunction(ruleTree,exprTree,options) {
            var ruleTok = ruleTree.tok;
            var exprTok = exprTree.tok;
            if(exprTok.type!='function' || (ruleTok.name!='?' && ruleTok.name!=exprTok.name)) {
                return false;
            }
            var ruleArgs = ruleTree.args.map(function(t){ return new Term(t); });
            var exprArgs = exprTree.args.map(function(t){ return new Term(t); });

            var namedTerms = matchTermSequence(ruleArgs,exprArgs,false,false,options);
            if(namedTerms===false) {
                return false;
            }

            /** Is the given name captured by this tree?
             *
             * @param {string} name
             * @param {Numbas.jme.tree} tree
             * @returns {boolean}
             */
            function name_captured(name,tree) {
                if(jme.isOp(tree.tok,';')) {
                    var res = resolveName(tree.args[1]);
                    if(res.name==name) {
                        return true;
                    }
                }
                if(tree.args) {
                    return tree.args.some(function(t2){ return name_captured(name,t2); });
                }
                return false;
            }

            // collate the named groups
            var match = {};
            for(var name in namedTerms) {
                var occurrences = 0;
                for(var i=0;i<ruleTree.args.length;i++) {
                    if(name_captured(name,ruleTree.args[i])) {
                        occurrences += 1;
                    }
                }
                var terms = namedTerms[name];
                match[name] = occurrences<=1 ? terms[0] : {tok: new jme.types.TList(terms.length), args: terms};
            }
            return match;
        }

.. function:: resolveName

    .. code-block:: javascript

        /** Resolve the name and value to store when capturing a subexpression.
         *
         * @param {Numbas.jme.tree} nameTree - The right-hand side of the `;` capturing operator. Either a name, or a keypair giving a name and the value to store.
         * @param {Numbas.jme.tree} value - The value to store, if `nameTree` doesn't override it.
         * @returns {object} - `name` is the name to store under, and `value` is the value.
         */
        function resolveName(nameTree,value) {
            var nameTok = nameTree.tok;
            if(!(nameTok.type=='name' || nameTok.type=='keypair')) {
                throw(new Numbas.Error('jme.matchTree.group name not a name'));
            }
            var name;
            if(nameTok.type=='name') {
                name = nameTok.name;
            } else if(nameTok.type=='keypair') {
                name = nameTok.key;
                value = nameTree.args[0];
            }
            return {name: name, value: value};
        }

.. function:: findCapturedNames

    .. code-block:: javascript

        /** Find names captured by this pattern.
         *
         * @param {Numbas.jme.tree} ruleTree
         * @returns {Array.<string>}
         */
        var findCapturedNames = jme.rules.findCapturedNames = function(ruleTree) {
            var tok = ruleTree.tok;
            var names = [];
            if(jme.isOp(tok,';') || jme.isOp(tok,';=')) {
                var res = resolveName(ruleTree.args[1]);
                names.push(res.name);
            }
            if(ruleTree.args) {
                for(var i=0;i<ruleTree.args.length;i++) {
                    var argnames = findCapturedNames(ruleTree.args[i]);
                    names = names.merge(argnames);
                }
            }
            return names;
        }

.. function:: matchAny

    .. code-block:: javascript

        /** Match any of the given patterns.
         * The first pattern which successfully matches is used.
         *
         * @param {Array.<Numbas.jme.tree>} patterns
         * @param {Numbas.jme.tree} exprTree
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {boolean|Numbas.jme.rules.jme_pattern_match}
         */
        function matchAny(patterns,exprTree,options) {
            for(var i=0;i<patterns.length;i++) {
                var m = matchTree(patterns[i],exprTree,options);
                if(m) {
                    return m;
                }
            }
            return false;
        }

.. function:: matchDefault

    .. code-block:: javascript

        /** Perform a match with a default value.
         * This operation only makes sense when matching a sequence of terms, so just match the pattern.
         *
         * @param {Numbas.jme.tree} ruleTree
         * @param {Numbas.jme.tree} defaultValue - Ignored.
         * @param {Numbas.jme.tree} exprTree
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {boolean|Numbas.jme.rules.jme_pattern_match}
         */
        function matchDefault(ruleTree, defaultValue, exprTree, options) {
            var m = matchTree(ruleTree,exprTree,options);
            return m;
        }

.. function:: matchOptionalPrefix

    .. code-block:: javascript

        /** Match `rule`, or `prefix(rule)` - allow any of a list of optional unary operators at the top of the tree.
         *
         * @param {Array.<string>} prefixes - The names of the optional operators.
         * @param {Numbas.jme.tree} ruleTree
         * @param {Numbas.jme.tree} exprTree
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {boolean|Numbas.jme.rules.jme_pattern_match}
         */
        function matchOptionalPrefix(prefixes,ruleTree,exprTree,options) {
            var originalExpr = exprTree;
            exprTree = extractLeadingMinus(exprTree);
            for(var i=0;i<prefixes.length;i++) {
                var prefix = prefixes[i];
                if(jme.isOp(exprTree.tok,prefix)) {
                    exprTree = exprTree.args[0];
                    break;
                }
            }
            var m = matchTree(ruleTree,exprTree,options);
            if(m) {
                m._match = originalExpr;
                return m;
            } else {
                return false;
            }
        }
        /** Bring any unary minus to the top of the tree.
         *
         * @param {Numbas.jme.tree} tree
         * @returns {Numbas.jme.tree}
         */
        var extractLeadingMinus = jme.rules.extractLeadingMinus = function(tree) {
            if(jme.isOp(tree.tok,'*') || jme.isOp(tree.tok,'/')) {
                if(jme.isOp(tree.args[0].tok,'-u')) {
                    return {tok:tree.args[0].tok, args: [{tok:tree.tok, args: [tree.args[0].args[0],tree.args[1]]}]};
                } else {
                    var left = extractLeadingMinus(tree.args[0]);
                    if(jme.isOp(left.tok,'-u')) {
                        return {tok: left.tok, args: [{tok: tree.tok, args: [left.args[0], tree.args[1]]}]};
                    } else {
                        return tree;
                    }
                }
            } else {
                return tree;
            }
        }

.. function:: matchNot

    .. code-block:: javascript

        /** Match if the expression doesn't match the given pattern.
         *
         * @param {Numbas.jme.tree} ruleTree - The pattern which must not be matched.
         * @param {Numbas.jme.tree} exprTree - The expression to test.
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {boolean|Numbas.jme.rules.jme_pattern_match}
         */
        function matchNot(ruleTree,exprTree,options) {
            if(!matchTree(ruleTree,exprTree,options)) {
                return preserve_match({},exprTree);
            } else {
                return false;
            }
        }

.. function:: matchUses

    .. code-block:: javascript

        /** Match if the expression uses all of the given names as free variables.
         *
         * @param {Array.<string>} names
         * @param {Numbas.jme.tree} exprTree
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {boolean|Numbas.jme.rules.jme_pattern_match}
         */
        function matchUses(names,exprTree,options) {
            var vars = jme.findvars(exprTree,[],options.scope);
            for(var i=0;i<names.length;i++) {
                if(!vars.contains(names[i])) {
                    return false;
                }
            }
            return {};
        }

.. function:: matchType

    .. code-block:: javascript

        /** Match if the top token of the given expression is of the given type.
         *
         * @param {string} wantedType - The required type.
         * @param {Numbas.jme.tree} exprTree
         * @returns {boolean|Numbas.jme.rules.jme_pattern_match}
         */
        function matchType(wantedType,exprTree) {
            if(exprTree.tok.type==wantedType) {
                return {};
            } else {
                return false;
            }
        }

.. function:: matchAnd

    .. code-block:: javascript

        /** Match all of the given patterns against the given expression. 
         * Return `false` if any of the patterns don't match.
         *
         * @param {Array.<Numbas.jme.tree>} patterns
         * @param {Numbas.jme.tree} exprTree
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {boolean|Numbas.jme.rules.jme_pattern_match}
         */
        function matchAnd(patterns,exprTree,options) {
            var matches = [];
            for(var i=0;i<patterns.length;i++) {
                var m = matchTree(patterns[i],exprTree,options);
                if(m) {
                    matches.push(m);
                } else {
                    return false;
                }
            }
            return mergeMatches(matches);
        }

.. function:: matchAllTree

    .. code-block:: javascript

        /** Find all matches for the rule, anywhere within the given expression.
         *
         * @memberof Numbas.jme.rules
         * @function
         * @param {Numbas.jme.tree} ruleTree - The pattern to match.
         * @param {Numbas.jme.tree} exprTree - The syntax tree to test.
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {Array.<Numbas.jme.rules.jme_pattern_match>}
         */
        var matchAllTree = jme.rules.matchAllTree = function(ruleTree,exprTree,options) {
            var matches = [];
            var m = matchTree(ruleTree,exprTree,options);
            if(m) {
                matches = [m];
            }
            if(exprTree.args) {
                exprTree.args.forEach(function(arg) {
                    var submatches = matchAllTree(ruleTree,arg,options);
                    matches = matches.concat(submatches);
                });
            }
            return matches;
        }

.. function:: mergeMatches

    .. code-block:: javascript

        /** Merge a list of matches into one match object.
         * Later matches override earlier ones: if two matches have the same captured name, the later one is used.
         *
         * @param {Array.<Numbas.jme.rules.jme_pattern_match>} matches
         * @returns {Numbas.jme.rules.jme_pattern_match}
         */
        function mergeMatches(matches) {
            var ms = matches.slice();
            ms.splice(0,0,{});
            return util.extend_object.apply(this,ms);
        }

.. function:: applyPostReplacement

    .. code-block:: javascript

        /** Apply operations specified in the result of a tree transformation: `eval(x)` is replaced with the result of evaluating `x`.
         *
         * @memberof Numbas.jme.rules
         * @function
         * @param {Numbas.jme.tree} tree
         * @param {Numbas.jme.rules.matchTree_options} options
         * @returns {Numbas.jme.tree}
         */
        var applyPostReplacement = jme.rules.applyPostReplacement = function(tree,options) {
            var tok = tree.tok;
            if(tree.args) {
                var args = tree.args.map(function(arg) {
                    return applyPostReplacement(arg,options);
                });
                tree = {tok:tok, args: args};
            }
            if(jme.isFunction(tok,'eval')) {
                return {tok: jme.evaluate(tree.args[0],options.scope)};
            } else if(jme.isFunction(tok,'m_listval')) {
                var n = tree.args[1].tok.value;
                return tree.args[0].args[n];
            } else if(tok.type=='op') {
                var filled_args = tree.args.filter(function(a) { return a.tok.type!='nothing'; });
                if(filled_args.length==1 && filled_args.length<tree.args.length) {
                    return filled_args[0];
                }
            }

            return tree;
        }

.. function:: transform

    .. code-block:: javascript

        /** Object returned by {@link Numbas.jme.rules.transform}.
         *
         * @type {object}
         * @typedef Numbas.jme.rules.transform_result
         * @property {boolean} changed - Is the result expression different to the input expression?
         * @property {Numbas.jme.tree} expression - The result expression.
         */

        /** Replace one expression with another, if it matches the given rule.
         *
         * @memberof Numbas.jme.rules
         * @function
         * @param {Numbas.jme.tree} ruleTree - The rule to test against.
         * @param {Numbas.jme.tree} resultTree - The tree to output, with named groups from the rule substituted in.
         * @param {Numbas.jme.tree} exprTree - The expression to be tested.
         * @param {Numbas.jme.rules.matchTree_options} options - Options for the match.
         * @returns {Numbas.jme.rules.transform_result}
         */
        var transform = jme.rules.transform = function(ruleTree,resultTree,exprTree,options) {
            var match = matchTree(ruleTree,exprTree,options);
            if(!match) {
                return {expression: exprTree, changed: false};
            }
            var names = findCapturedNames(ruleTree);
            names.forEach(function(name) {
                if(!(name in match)) {
                    match[name] = {tok: new jme.types.TNothing()};
                }
            });

            var out = jme.substituteTree(resultTree,new jme.Scope([{variables: match}]), true);
            out = applyPostReplacement(out,options);
            var ruleTok = ruleTree.tok;
            if(match._rest_start) {
                out = {tok: new jme.types.TOp(match.__op__), args: [match._rest_start, out]};
            }
            if(match._rest_end) {
                out = {tok: new jme.types.TOp(match.__op__), args: [out, match._rest_end]};
            }
            return {expression: out, changed: !jme.treesSame(exprTree,out,options.scope)};
        }

.. function:: transformAll

    .. code-block:: javascript

        /** Replace anything matching the rule with the given result, at any position in the given expression.
         *
         * @memberof Numbas.jme.rules
         * @function
         * @param {Numbas.jme.tree} ruleTree - The rule to test against.
         * @param {Numbas.jme.tree} resultTree - The tree to output, with named groups from the rule substituted in.
         * @param {Numbas.jme.tree} exprTree - The expression to be tested.
         * @param {Numbas.jme.rules.matchTree_options} options - Options for the match.
         * @returns {Numbas.jme.rules.transform_result}
         */
        var transformAll = jme.rules.transformAll = function(ruleTree,resultTree,exprTree,options) {
            var changed = false;
            if(exprTree.args) {
                var args = exprTree.args.map(function(arg){ 
                    var o = transformAll(ruleTree,resultTree,arg,options);
                    changed = changed || o.changed;
                    return  o.expression;
                });
                exprTree = {tok: exprTree.tok, args: args};
            }

            var o = transform(ruleTree,resultTree,exprTree,options);
            changed = changed || o.changed;
            return {expression: o.expression, changed: changed};
        }

.. class:: Ruleset

    .. code-block:: javascript

        /** Set of simplification rules.
         *
         * @class
         * @memberof Numbas.jme.rules
         * @param {Numbas.jme.rules.Rule[]} rules
         * @param {Numbas.jme.rules.ruleset_flags} flags
         */
        var Ruleset = jme.rules.Ruleset = function(rules,flags) {
            this.rules = rules;
            this.flags = util.extend_object({},displayFlags,flags);
        }

        Ruleset.prototype = /** @lends Numbas.jme.rules.Ruleset.prototype */ {
            /** Test whether flag is set.
             *
             * @param {string} flag
             * @returns {boolean}
             */
            flagSet: function(flag) {
                flag = jme.normaliseRulesetName(flag);
                if(this.flags.hasOwnProperty(flag))
                    return this.flags[flag];
                else
                    return false;
            },

            /** Apply this set's rules to the given expression until they don't change any more.
             *
             * @param {Numbas.jme.tree} exprTree
             * @param {Numbas.jme.Scope} scope
             * @see Numbas.jme.rules.transform
             * @see Numbas.jme.rules.matchTree
             * @returns {Numbas.jme.tree}
             */
            simplify: function(exprTree,scope) {
                var rs = this;
                var changed = true;
                var depth = 0;
                var seen = [];
                while(changed) {
                    if(exprTree.args) {
                        var nargs = exprTree.args.map(function(arg) { return rs.simplify(arg,scope); });
                        exprTree = {tok: exprTree.tok, args: nargs};
                    }
                    changed = false;
                    for(var i=0;i<this.rules.length;i++) {
                        var result = this.rules[i].replace(exprTree,scope);
                        if(result.changed) {
                            if(depth > 100) {
                                var str = Numbas.jme.display.treeToJME(exprTree);
                                if(seen.indexOf(str)!=-1) {
                                    throw(new Numbas.Error("jme.display.simplifyTree.stuck in a loop",{expr:str}));
                                }
                                seen.push(str);
                            }
                            changed = true;
                            exprTree = result.expression;
                            depth += 1;
                            break;
                        }
                    }
                }
                return exprTree;
            }
        }

Problems
########

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

Maybe ``findSequenceMatch`` should be a generator for all valid
assignments, not just return the first one.

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
`Martell-Montanari <http://www.nsl.com/misc/papers/martelli-montanari.pdf>`__
unification algorithm to identify values of free variables on either
side of an equation so that they are equivalent.

It doesn't allow for missing values, or alternate forms in one
expression - you'd have to give an equation for each form.

STACK
#####

STACK has a few answer tests to do with the form of the student's
answer: LowestTerms, Expanded, FacForm, SingleFrac, PartFrac,
CompletedSquare.

For anything else, you can apply simplification rules to expressions
before comparing - the two expressions should end up exactly equal after
simplifying.

Maxima
######

Maxima deals with everything as S-expressions, and seems to require
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

Rubi
####

`Rubi <http://www.apmaths.uwo.ca/%7Earich/>`__ symbolically integrates.

