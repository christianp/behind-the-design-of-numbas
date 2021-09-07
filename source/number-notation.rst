Number notation
===============

.. page_status::
    :kind: outline

There are many different ways of writing numbers, depending on culture and context.

Consider "standard" decimal numbers.
These are a subset of :math:`\mathbb{R}` (and of :math:`\mathbb{Q}`!)
In English, normally this is a series of digits, with a dot separating the integer and fractional part.
In some contexts, the number of digits after the point might be significant, or you might want to group digits for readability.
Different context use different punctuation and grouping rules, e.g. `in India <https://en.wikipedia.org/wiki/Indian_numbering_system#Use_of_separators>`__ the integer part is written in groups of 2 and then a least-significant group of 3.

It is not true that every number has a unique decimal representation.

'Scientific' and 'engineering' notation describe numbers at different orders of magnitude, but to similar relative precision.
Sometimes a trailing dot is used to show a precision of zero decimal places in the significand, e.g. ``35.e+10``.
This notation represents the same set of decimal numbers as the usual English notation described above.

'Fractions' represent elements of :math:`\mathbb{Q}`.
In English, fractions are often written ``a / b``.
Mixed fractions, e.g. ``A b/c``, are common, but not understood everywhere.
Some countries use ``:`` as the separator for the numerator and denominator, e.g. ``a : b``.
Fractions don't encode precision - they are usually interpreted as completely precise.

Ratios represent fractions, but with different semantics.
A ratio of ``3 : 4`` could be interpreted as saying that the first quantity makes up three-sevenths of the whole.

Some contexts use mixed fractions with a fixed denominator, e.g. US gas prices (tenths of a cent); `stock prices <https://www.investopedia.com/ask/answers/why-nyse-switch-fractions-to-decimals/>`__ (sixteenths of a dollar).

There are many 'number-like' quantities, with their own notations:

* Percentages.
  There are *percentages of* and *percentage changes*, both written using the same symbols.
  0% and 100% should not be rounded to, when working with a 'percentage of'.

* Angles.
  While angles are dimensionless, there are many scales, including: degrees, radians, gradians, minutes and seconds.

* Measurements in Imperial units often use a mix of orders of magnitude, e.g. *3lb 4oz*.

* Complex numbers are often written in Cartesian (:math:`a + bi`) or polar (:math:`re^{i \theta}`) form.

* Vectors, written as a tuple of scalars :math:`(a,b,c)`.

* Currency.
  Must currencies have a subdivision with its own symbol, e.g. ¢.
  The currency symbol is not always in the same place and is not necessarily unique, e.g. $.
  Amounts of currency are often rounded to the nearest penny, but not always.

* Scores, e.g. in cricket when counting bowling, '2.5' means two overs and 5 balls.

* Ages of young children, e.g. '2.3' means '2 years and 3 months'.

* Times.
  "Time of day" and "time elapsed" are different.

Care must be taken when rounding near a critical value.
For example, if the pass mark for an exam is 70%, don't round 69.7% up.

In place-value systems, different bases exist.
Sometimes the base is implicit, other times it is denoted with a suffix or prefix, usually a subscript, e.g. :math:`1011_2`.

Styles of notation can conflict with each other, e.g. ``1.234`` in English vs French.

There are number-like objects that don't have any arithmetic:

* Phone numbers.
  Around the world there are different conventions for how the digits are grouped.

* ISBN codes.

* US zip codes.

* House numbers.

Here are some properties that number-like things might have:

* Ordering.

* The Intermediate Value Theorem.

* A selection of arithmetic operations.

* Being a (dense) subset of the real numbers.

* Multiple ways of representing the same amount.

* Having a meaningful 'zero'.

The difference between two number-like things might not be the same type of thing, e.g. percentage change, difference in time.

An important concept is the `torsor <https://math.ucr.edu/home/baez/torsors.html>`__ - a measurement that has well-defined differences but no meaningful 'zero'.
Temperatures and times are examples of torsors.

Another concept is `'levels of measurement' <https://en.wikipedia.org/wiki/Level_of_measurement>`__, based on how two values can be combined:

* Nominal: can be compared for equality.

* Ordinal: can be compared for ordering.

* Interval: Can be added and subtracted.

* Ratio: can be multiplied and divided.

Numbers can be written in words.
There are lots of conventions for this, even just in English:

* Include "and" after hundreds?
* When are hyphens included? e.g. "twenty-five" vs "twenty five"; "three-hundred" vs "three hundred".

Even ignoring these differences, it is not true that every number has a unique representation in words, e.g. "twelve hundred" and "one thousand, two hundred".

Problem
-------

Should the "number entry" part only be used for situations where the answer is an element of :math:`\mathbb{R}`?
Do percentages require a separate part type?
