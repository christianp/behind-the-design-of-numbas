.. _pattern-matching:

Pattern-matching mathematical expressions
=========================================

.. page_status::
    :kind: outline

https://www.overleaf.com/project/5b92712d47e18a0f04cc4763

Problem
-------

Want to decide if an expression is in a certain form, or capture parts of an expression for the purpose of further testing or rearrangement.

Regular expressions are a common solution for pattern-matching on strings.

Pattern-matching on trees is not as simple as on strings.

What is the right way to define a rewriting rule?

Match pattern → identify terms matched against parts of the pattern → write a new expression

Want to avoid combinatorial explosion in the number of rules that must be defined (the algorithm might have exponential running time, though)

Need built-in matchers for common things, e.g. rational polynomials, complex numbers in Cartesian or polar form.

Associativity and commutativity of operations/terms sometimes matter, and sometimes don't.

Quantifiers are complicated.

How to capture a missing term with a default value?

How do you combine terms that are captured more than once?

Back-references would allow you to identify terms that should cancel, such as common factors/denominators.

For the rewriting step, must be able to evaluate a captured term to an object that you can do arithmetic with.

Syntax should be at least as readable as Perl-style regular expressions (famously hard to read!)

Need a lot of new symbols for quantifiers, conjunctions and atoms.
(First go, using ``m_something``, was unreadable.

Once you've got pattern-matching, you can do lots of things:

* Check the form of an answer
* Symbolic differentiation
* Canonical forms for (classes of) expressions
* Other CAS techniques

Solution
--------

Quantifiers and special matching symbols, like regular expressions, but operating on syntax trees.

Previous work
-------------

* Regular expressions
* Mathematica
* Maxima
