Explore mode
============

.. page_status::
    :kind: outline

Problem
-------

Want to:

* allow student to choose their own path through an activity.
* update some state based on student's answers.
* offer optional hints.

Use cases
#########

* Let the student choose to take each of several hints, one at a time.

* Choose how to answer a question, entailing different inputs, e.g. "does this equation have a root?" → "what is it?" or "why not?"

* Base the question on free input from the student, e.g. labe measurements.
  (This is possible with adaptive marking, but you can't update prompts that way)

* Questions like a state machine / text adventure.

Solution
--------

The question has a list of available parts.

The first part is shown to the student.

Each part has a list of "next part options", referring to another part.
They can have:

* An availability condition, depending on the student's answer, score, whether an answer has been submitted yet.

* A list of variable replacements to make when making the next part, using the current variables, the student's answer, and the values of marking algorithm notes.

* A penalty to apply for choosing this option.

There can be more than one instance of each defined part.
A part can have its own definition in a next part option.

The loop is as follows:

* Show a part - create an instance of the part from its definition.

* Offer next part options.
  The list is updated each time the student submits an answer.

* When the student selects a next part, apply any penalty and create a new set of variables using the defined replacements.

Scoring is tricky: you might be able to visit a part which awards marks arbitrarily often, so if the score for the question is just the sum of the scores for the parts, then the maximum score is unlimited.

Instead, each part feeds into a named *objective*, with a fixed limit on its total score.
Penalties are also named, with a maximum on each.
The score for the question is the sum of the objectives' scores, minus the sum of the penalties.
This helps to explain the marking to the student: their score is broken down into, for example, "identify critical points"; "classify solution" and so on.

Navigation might be difficult: if a student goes down a long optional path, we need to make sure they can go back.
The default theme displays breadcrumbs at the top of the question, and each part can optionally show a "go back to the previous part" link.

The "end" of the question is not well-defined: there might be more paths that the student could have taken.
It's up to the question author to tell the student when they're done.
