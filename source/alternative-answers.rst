Alternative answers
===================

.. page_status::
    :kind: outline

Problem
-------

Want to provide feedback or partial marks for several answers you're expecting, either common errors or alternative correct answers.

Examples:

* Expected wrong answers.
* A valid answer that is not captured by the main part's marking algorithm. (e.g. both 1 and 3 are correct answers to a number entry part)
* Partial marks for close answers. (e.g. within 10% of the right answer, within 50%, etc.)

This could be implemented with custom marking algorithms, but it's a sufficiently common pattern that it's worth making convenient and consistent.

Solution
--------

Each part has a list of alternative answers, implemented as copies of the part with changed settings.
Each alternative has a different maximum mark.

When marking the answer, the main part and its alternatives are checked in order. 
The version that produces the most credit is used to provide the feedback, and the student's score is the credit multiplied by the marks available for that version.

Previous work
-------------

DEWIS common errors
