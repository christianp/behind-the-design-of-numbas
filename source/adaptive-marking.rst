Adaptive marking
================

Problem
-------

Want to use the student's answer to a previous part in the marking of a later part.

Examples:

* Error-carried-forward - mark the later part as if the student's earlier incorrect answer was correct.
* Free input from the student, e.g. lab measurements.

Solution
--------

Each part can define a list of variable replacements, replacing the value of a question variable with the student's answer to another part.

Variables depending on the replaced variables are recalculated.

The author can decide whether this should always happen, or if marking without replacements should be tried first. The version that produces most credit is used.

Difficulties
------------

Adaptive-marked parts become invalid when the student changes their answer to a referred part.

Do students understand what is happening?

Certain answers to an earlier part could make later parts too easy to answer, e.g. ignore the question text and enter :math:`x` such that you already know what :math:`f(x)` is.

Alternative solutions
---------------------

Explore mode for free input questions.

Add alternative answers for errors you're expecting, and don't allow error-carried-forward for other mistakes.
