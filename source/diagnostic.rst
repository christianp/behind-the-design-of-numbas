Diagnostic mode
===============

.. page_status::
    :kind: outline

Motivation
----------

Want to administer a test to establish the student's strengths and weaknesses, in as few questions as possible.

Solution
--------

`Slides from EAMS 2021 talk <https://www.numbas.org.uk/talks/diagnostic-testing-eams-2021/#/start>`__

Questions asked depend on the student's answers to previous questions.

A "diagnostic" mode for exams.
This adds:

* A *knowledge graph*, consisting of *topics* and *learning objectives*.
  Topics are linked by "depends on" and "leads to" relations.
  Learning objectives collect many topics.

* A *diagnostic algorithm*, written in a similar format to marking algorithms: a collection of declarative notes.

Each topic corresponds to a group of questions.

When running the exam, the diagnostic algorithm has a *state* object, which the algorithm is responsible for initialising and updating.
This object can take any form.

The loop is:

* Pick a question to show to the student.
* When the student chooses to move on (this is usually after answering the question, but could be any time) give the student some options.
* Each option nominates the next question, and an updated state object.
* If there are no options, the exam ends.

During the exam the student is shown a feedback message, as well as a list of progress scores (in DIAGNOSYS, one for each learning objective).

After the exam ends, the student is shown a list of scores (in DIAGNOSYS, one for each learning objective) and a feedback message.

Previous work
-------------

`DIAGNOSYS <https://web.archive.org/web/20090123035303/http://www.staff.ncl.ac.uk/john.appleby/diagpage/diagindx.htm>`_

