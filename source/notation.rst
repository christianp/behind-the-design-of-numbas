Parsing mathematical notation
=============================

.. page_status::
    :kind: outline

Unfinished paper: `Formal grammars for informal mathematics <https://www.overleaf.com/project/5cd294a090889a4981925d8b>`__

Should this be several separate documents?

* History and development of JME in Numbas
* Ambiguities in linear mathematical notation
* Contexts for notation

Problem
-------

We need a syntax for students and question authors to enter mathematical expressions.

To avoid confusion, question authors and students should use the same syntax, where possible.

Mathematical notation is not rigorously defined, and contains many ambiguities and inconsistencies.

Want to specify allowed notation, and accept many conventions.

The validity and meaning of notation depends on context.

Students are not experts in notation.
When students use notation loosely, and an 'error' is beside the point of the assessment, we should make reasonable effort to interpret it.

When displaying a mathematical expression in the conventional 2D format, if two expressions are displayed the same then they should be considered equivalent.
Displayed expressions should match as closely as possible the linear input: the student should be able to use the display to check their input is interpreted correctly, and it shouldn't give away any equivalences that might be part of the assessment.

There are now some conventions for linear maths input, but still many conflicting standards.

While conventions around linear input have typically been limited to the ASCII character set, Unicode is increasingly accessible to students, and correctly-encoded mathematical symbols should be understood, e.g. ``√``.

Should provide good feedback for invalid input - the student should be able to work out how to resolve the problem quickly, and ideally should be offered a suggestion for a valid input.

What's the best input method? Linear plain text? WYSIWYG? 

GitHub issues:

* `Parsers for different kinds of notation <https://github.com/numbas/Numbas/issues/677>`__
* `Editable list of constants <https://github.com/numbas/Numbas/issues/691>`__

Difficulties with linear notation
#################################

* Implicit multiplication vs:

  * Function application: in ``x(t+1)``, is ``x`` a function or is it equivalent to ``x*(t+1)``?
  * Long names: ``speed`` or ``s*p*e*e*d``?

* Underscores: are ``x1`` and ``x_1`` synonyms?

* Conventions for powers of trig functions: ``sin^2(x) = (sin(x))^2``.

* Parentheses are often omitted when applying a function to a single atom, e.g. ``sin x``, ``ln 2``.

* Chaining division and multiplication: e.g. is ``1/2x`` equivalent to ``(1/2)*x`` or ``1/(2x)``? How does spacing affect this?

* Chained relations: e.g. ``a<b<c`` is equivalent to ``(a<b) and (b<c)``.

* Square brackets are commonly used for grouping, but are also used to delimit lists.

* Does ``y'`` mean the derivative of ``y``?

* Variable names are usually case-sensitive, but at certain levels it's not important.

* Differing conventions around the world:

  * Number literals, e.g. `1,234` is a big number in the UK, but a small number in most of Europe.
  * The symbol for division: ``÷`` is used in the UK, but ``:`` is used in many other countries.


Spacing can help to resolve ambiguities, but we can't rely on students to be sensitive to this.

Constants
#########

There are many conventional named constants, such as :math:`\pi`, :math:`e`, :math:`i`.

The meaning of these constants depends on the context.

There are also some conventions that allow you to infer some properties of a variable based on the symbol used, e.g. :math:`x` for an unknown, :math:`a` for a known quantity.


Solution
--------

Plain text input.

Abstracted parser.

"Expand juxtapositions" routines.

Still much to do.

Previous work
-------------

See :cite:t:`sangwin`.

`whystartat.xyz <https://whystartat.xyz>`_
