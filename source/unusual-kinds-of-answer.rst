Unusual kinds of answer
=======================

.. page_status::
    :kind: outline

When the answer is not one of the built-in data types, what do you do?

* Use the 'closest' built-in part type.

* Ask for just bits of the answer, with some scaffolding, e.g. coefficients.

* Write a multiple choice question.

* Make a custom marking algorithm for a built-in part type.

* Make a custom part type.

There's a cost/benefit calculus for making a custom part type.

If making a custom marking algorithm, make it reusable - if you spot a bug or want to make a change, you don't want to track down every copy of the algorithm.

Think about:

* How does the student enter their answer?

* What answers are invalid?
  Try to accept all reasonable efforts, but reject mistakes which might not be what the students intended.

* How much feedback can you give?
  Want to explain the marking, but minimise hints as to the correct answer.
  Again, there's a cost/benefit calculus for how many cases to catch.

* Configuration options: if several questions ask the same sort of thing, use a single part type with options.
