Feedback
========

Problem
-------

e-assessment is used in different contexts, with different intentions for feedback.

Want to control how much feedback is given, and when.

Need to identify what feedback is always required.

Kinds of feedback:

* Scores for parts, questions, and the total.

* Exam-level:

  * Total score
  * Pass/fail
  * Guidance at the end, e.g. "you passed, but only just; maybe do more revision and try again"

* Part-level:

  * Error messages for invalid answers.
  * Tick/cross for correct/incorrect answer. Not appropriate for parts with no incorrect but valid answer.
  * Explanatory feedback in response to part answers, e.g. "your answer is not divisible by 6, but should be".

There are some things that don't count as "feedback" under some definitions, but are useful to consider at the same time:

* Correct answers.
* Question advice (fully worked solution)

Feedback can be given immediately, while the student can act on it, or after the part/question/exam has been locked, or after a certain date.

Consider feedback loops.
Which loops are allowed, and which not?

* Enter answer → answer is invalid → change answer.
* Enter answer → answer is incorrect → change answer.
* Complete question → still don't feel confident → try another similar question.
* End exam → did not pass → try again.

On receiving feedback, what should the student do?

* Try again.
* Think about where they went wrong.
* Think of another way of getting the right answer.
* Memorise the correct answer.
* Reflect on guidance given.
* Take a different course of action, e.g. moving on to a different activity, or abandoning this one.

Students report that often just seeing the correct answer or working is enough to see where they went wrong.
However, without further assessment, a student might believe they've understood a solution without being able to reproduce it.

Solution
--------

Settings at the part, question and exam level control most of the kinds of feedback identified above.

Feedback for invalid answers is always given.

It is always possible to change your answer to a part and resubmit, at no penalty.
In cases where the author wants to forbid the "answer is incorrect → change answer" loop, they should disable immediate feedback.

Rather than baking a date for releasing feedback into the exam, we use "entering in review mode" as something that the player can restrict by date.

Difficulties
------------

The exam-level feedback settings are a mess, as a result of settings being added for use cases as they come up.

Many of the names for settings are unclear, or easily misinterpreted.

It would be convenient to have presets for common cases, such as "revision material", "high-stakes final test", "weekly homework".
