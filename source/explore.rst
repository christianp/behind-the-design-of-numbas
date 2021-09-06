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

* A list of variable replacements to make when making the next part, based using the current variables and the student's answer.

* A penalty to apply for choosing this option.

There can be more than one instance of each defined part.
A part can have its own definition in a next part option.

The loop is as follows:

* Show a part - create an instance of the part from its definition.

* Offer next part options.
  The list is updated each time the student submits an answer.

* When the student selects a next part, apply any penalty and create a new set of variables using the defined replacements.


