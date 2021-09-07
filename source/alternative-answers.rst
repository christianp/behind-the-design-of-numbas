Alternative answers
===================

.. page_status::
    :kind: outline

Problem
-------

Want to provide feedback or partial marks for several answers you're expecting, either common errors or alternative correct answers.

Examples:

* Expected wrong answers corresponding to errors the author expects the student to make.
* A valid answer that is not captured by the main part's marking algorithm. (e.g. both 1 and 3 are correct answers to a number entry part; giving an answer in miles per gallon or litres per kilometre)
* Partial marks for close answers. (e.g. within 10% of the right answer, within 50%, etc.)

This could be implemented with custom marking algorithms, but it's a sufficiently common pattern that it's worth making convenient and consistent.

Solution
--------

Each part has a list of alternative answers, implemented as copies of the part with changed settings.

All settings can be changed - just changing "correct answer" isn't enough, for example when catching numbers given to the wrong precision, or expressions matching a different pattern)

Each alternative has a different maximum mark, which should be between 0 and the maximum mark for the main part.

When marking the answer, the main part and its alternatives are checked in order. 
The version that produces the most marks (or credit, if tied on marks) is used to provide the feedback.
If an alternative is used, its feedback message is shown to the student.
You don't always want to show all the feedback messages produced by an alternative - if it's using a built-in marking algorithm to catch an expected error, the built-in feedback will say "correct".
But for an alternate correct answer, you probably do want to show the marking algorithm's feedback.

Previous work
-------------

DEWIS common errors
