Marking algorithms
==================

.. page_status::
    :kind: draft

Problem
-------

Built-in marking algorithms can't encompass every assessment someone might want to set.

We want a framework for writing a marking algorithm, which produces feedback based on student's answer.

In the first few versions of Numbas, the marking for each part type was carried out by a function written in JavaScript.
The ``Part`` object had some methods for modifying credit awarded and giving feedback.

Question authors could change the marking by writing their own JavaScript, either replacing the built-in or extending it.

JavaScript is not easy to write.

Could add more settings to allow for different marking behaviour, but this makes the editing interface very complicated.
Have to think about how all the different settings interact with each other, too.
For example, if you want to mark a number modulo :math:`n`, how does that interact with the notation style and precision settings?

There are three phases to a marking algorithm:

* **Interpreting**:
  Take the student's answer as they entered it into the system, and try to interpret it as a representation of a certain type of object, such as a numerical value, mathematical expression, or a selection of the choices presented to the student.

  This is difficult and complicated work, and it doesn't make sense for each question author to repeat it.

  The author should be able to choose what formats they will accept, and how strict the parsing should be - for example, allowing implicit multiplication in mathematical expressions, or not requiring trailing zeros when giving a number to a certain precision.

  If the student's answer can not be parsed, it is rejected as invalid and the submission is not counted.

* **Testing**:
  Test the student's answer for correctness, by comparing against expected values or testing that it satisfies certain conditions.

  Sometimes there's a combination of these: the answer must be equivalent to a given value, but must also be expressed in a certain form.

* **Feedback**:
  The system produces a score and a feedback message to display to the student.

  Detailed feedback is time-consuming to set up: while exactly pinpointing where the student went wrong can be helpful in a formative context, there are diminishing returns from setting up a marking algorithm to catch rarer errors.

  Some accounting of the marking process is useful for the teacher, to identify common patterns across all student attempts.

Use cases
*********

A custom marking algorithm is required when the built-in marking algorithm and its options can't do what you want.

A common pattern is a "give an example" question.
The built-in part types are set up to compare the student's answer against a given expected answer.
For "give an answer" questions, instead we want to test that the student's answer satisfies a certain condition.

Requirements
************

When a valid answer is submitted to a part, we need to produce:

* A score (really, an amount of credit, which is the proportion of the marks available to award).
* A list of feedback messages, whose main job is to explain the score.
* A representation of the student's answer as it was interpreted. 
  For example, in a number entry part, a number.

If the answer is invalid, we must produce a message explaining why.

Sometimes an answer could be invalid, but probably wrong: for example, ``sin^2(x)`` might be interpreted as ``(sin(x))^2`` or ``sin(sin(x))``.
The system could give the student a hint describing less ambiguous ways of writing the two options, while picking one interpretation to mark.

It would also be nice to produce extra information about the student's answer, for use by later parts or in analysis across all student attempts.
For example, flags representing properties the student's answer satisfies.

Previous work
-------------

STACK
*****

In STACK, a question is marked using a `*Potential Response Tree* <https://docs.stack-assessment.org/en/Authoring/Potential_response_trees/>`_, or *PRT*.
A PRT is not necessarily a tree - it is only required to be a rooted directed acyclic graph.

A question can have more than one PRT, and the final feedback is a combination of the feedback from each PRT.

The idea is that each node of the tree represents a decision about which path to follow, with feedback produced as a side-effect.

The inputs are:

* The student's answers to each of the inputs.
* The question's variables.
* 'Feedback variables', which are used to process the student's answers but don't represent any feedback themselves.

The variables are evaluated in order, and there's no control flow outside of an individual variable's definition.
Errors must be caught in each variable.
The student may not use a variable name which is assigned in the question or feedback variables in their answer.

Before the PRTs are evaluated, each input is validated.
PRTs are only evaluated once all inputs are valid.
Control over how an input is validated is limited to a few true/false options.

Each node in a PRT has the following properties:

* A test to perform, and two parameters.
  There are a limited number of tests, each designed to compare two values and return either 'true' or 'false'.

* For each possible result of the test:

  * A score value, and whether this should add to, subtract from or replace the current score.
  * A "penalty" amount, a percentage of the score to subtract for each incorrect attempt.
  * A node to visit next, or none.
  * An "answer note" used to record the path taken through the PRT, visible only to the teacher.
  * A feedback message to show to the student.

Evaluation of a PRT follows this algorithm:

* Start at the root node.

* Perform the test specified by the current node.
  Based on the result, modify the score, add the feedback message to the output, then move to the next node.

* If no next node is nominated, end the process.

The output of a PRT is:

* a **score**, which is a value between 0 and 1 representing how correct the student's answer is.
* feedback messages to show to the student
* an "answer note" string, which is the concatenation of the notes produced by the nodes visited, and whether they took the "true" or "false" branch.

The collected feedback messages are shown as a sequence of paragraphs.
There is no correct/incorrect/neutral feedback for individual messages, and no automatic accounting of the score.

Each PRT has a "value", which is multiplied by the score it produces to obtain the PRT's contribution to the total for the question.


Summary
~~~~~~~

The work of parsing the student's answer is not under the author's control.
  
Validation is separated from correctness - the real marking doesn't happen until the student has submitted a valid answer to each of the inputs, but what is valid isn't easily configured.
For example, it wouldn't be possible to reject an unexpanded polynomial as invalid, or to accept an answer in a syntax that STACK's built-in parse doesn't recognise.

Inputs and PRTs are separate.
Feedback variables are not shared between PRTs.
It's straightforward to use several inputs together, such as separate inputs for each of the roots of a quadratic, but the logic for things like error-carried-forward marking has to be implemented from scratch in PRT nodes each time.

To invent a new answer test, you would have to construct a value in feedback variables and compare it against ``true``.

You can construct quite sophisticated marking processes by combining the simple binary choice of an answer test.

There are no reusable or extensible built-in PRTs.

DEWIS
*****

A question is a Perl program, producing both the text and the marking routine.
I don't have access to any DEWIS questions, so this rough description is based on what I've gathered from conversations with the DEWIS team.

There are lots of built-in routines for common tasks, such as marking a number or matrix by comparison with an expected value, or marking a pair of roots of an equation.

The key mechanism for producing feedback is flags, which can be set at any point in a marking routine.
They're typically codes for certain situations, such as "exactly correct", "correct but not cancelled", "incorrect".

These flags can be used to [categorise common errors](https://eprints.whiterose.ac.uk/91174/).

WeBWorK
*******

Like DEWIS, WeBWorK questions are Perl programs which produce both the text and the marking routine.

There are built-in `contexts <https://webwork.maa.org/wiki/ContextList>`__ which provide validation and marking routines, called 'answer checkers'. 

The validation can be `configured by replacing individual methods <https://webwork.maa.org/wiki/Modifying_Contexts_(advanced)>`__, for example to parse different number notation styles.

You can write your own answer checker as a Perl subroutine, which might use the built-in checkers.

An `answer checker <https://webwork.maa.org/pod/pg/doc/MathObjects/MathObjectsAnswerCheckers.html#The-Context-and-Answer-Checkers>`__ returns a value between 0 and 1, representing the correctness of the student's answer, as well as a feedback message.

There doesn't seem to be any facility for reporting properties of the student's answer for later analysis.

Solution
--------

Each part has a *marking algorithm*, which is a script written in JME syntax.
The script consists of a set of notes, each of which produces both a JME value and (as a side-effect) a list of feedback items.
(I think this is a monad, in the Haskell sense)

Notes can refer to other notes.

There are two required notes:

* ``mark`` - The feedback produced by this note is used as the feedback for the part.
* ``interpreted_answer`` - A representation of the student's answer, as interpreted by the marking algorithm. 
  This allows other parts of the question to reuse this value without repeating the parsing process, which might rely on this part's settings.

There is a tension between declarative and imperative styles: want to perform a sequence of steps, producing a list of feedback items, for which imperative makes more sense, but declarative makes the note structure possible.
To enable imperative style, there is a left-associative infix operator ``;``, which evaluates first the left and then the right-hand side, and returns the right-hand side's value.

There are functions for producing feedback: ``set_credit``, ``multiply_credit``, ``feedback``, etc.
These all require a message, so that the final score is explained.

It can be useful to mark feedback items as "positive" or "negative" even if they don't affect the credit. 

There are two major elements of control flow: 

* once the student's answer is identified as invalid, no more work needs to be done.
* if the student's answer must pass a series of tests, once one has been failed there's no point doing the others.

Gap-fill parts combine feedback from each of the gaps.

Built-in part types use this system.

It's convenient to reuse the standard marking algorithms and just change a small part, usually the final ``mark`` note.
This means that the part uses the standard parsing and validation logic, which is often quite complicated and refined over years.

Separating the algorithm into notes allows each of the steps to be compartmentalised.
Notes can be referred to by name, returning their JME value, or have their feedback appended to the current state using the ``apply`` function.

The built-in marking algorithms in Numbas try to be as generous as possible when parsing the student's answer.
The author can usually configure how strict the parser is.

Evaluating a marking algorithm
******************************

Evaluation works similarly to question variable generation and diagnostic algorithms: 

* Each of the notes is evaluated in turn.
* Before evaluating a note, if it refers to another note, evaluate that note first.

Each note is evaluated within a *stateful scope*. 
The state of the scope is a list of feedback items, which is initially empty.
Operations can append to this list.

The scope maintains dictionaries of the final state of each note, and any error produced while evaluating each note.

The output is a dictionary, giving for each note:

* The final state - a list of feedback items.
* Whether the state is valid.
* The calculated JME value.
* An error message, if one was produced.

If a note produces an error, that does not stop evaluation of the algorithm, so notes that do not apply can be safely ignored without having to explicitly catch the error.

Errors cascade: if a note refers to another note which produced an error, it produces the same error and no attempt is made to evaluate it.

Marking a part
**************

The following is a description of the process of marking a student's answer to a question part.
This ignores the logic around adaptive marking and alternative answers.



The input is:

* the student answer
* the part's settings
* the number of marks available
* lists of the gaps and steps belonging to this part
* the names of all variables defined by the question
* a marking algorithm

The output is a final list of feedback items, as well as for each note the corresponding values, list of feedback items and any error produced.

A feedback item represents an operation on the part's feedback, such as changing the credit or giving the student a message.
Each item has a ``type`` describing what kind of operation the item performs, as well as one or more of the following properties, depending on the type:

* ``credit`` - an amount of credit to set, add, or multiply.
* ``reason`` - an extra note about why the operation is being performed, such as ``'correct'`` or ``'incorrect'`` when the credit is changed, or ``'invalid'`` when the student's answer is determined to be invalid.
* ``message`` - a message to show to the student explaining this item.
* ``concat_items`` - for the **Concatenate** operation, a list of items to add to the state.
* ``invalid`` - for the **End** operation, does this represent a decision that the student's answer is invalid?

The marking script is evaluated, with the other inputs available as variables.

The list of feedback items produced by the ``mark`` note is *finalised* with the following process, producing a final amount of credit, a determination if the student's answer is invalid, and a list of messages to show to the student:

* Initialise::

    valid = true
    end = false
    credit = 0
    output = empty list
    scale = 1
    lifts = empty stack

  The ``lifts`` are a mechanism for dealing with gap-fill parts, where the feedback from each of the gaps is scaled down and concatenated to give the feedback for the parent part.

* For each item in the input list, do the following depending on the item's type:

  * **Set credit**: set ``credit`` to the given amount, and add this item to the output.

  * **Multiply credit**: multiply ``credit`` by the given amount, and add this item to the output.

  * **Add credit**: add the given amount to ``credit``, and add this item to the output.

  * **Subtract credit**: subtract the given amount from ``credit``, and add this item to the output.

  * **End**: end the feedback here - ignore any subsequent items.
    If the item is marked as invalid, then set ``invalid`` to ``false``.
    If there is a lift on the stack, this represents the end of a gap's feedback, so instead skip ahead to the end of that gap's feedback and continue.
    
  * **Concatenate**: 

    * Add a lift to the stack, storing the current values of ``credit`` and ``scale``.
    * Set ``credit = 0`` and ``scale`` to the given value.
    * Insert the given items in the list just after this one, to be analysed next.
    * After those, add an **End lift** item.
    * Add this item to the output.

  * **End lift**: 

    * Take the last lift off the stack.
    * Multiply the current ``credit`` by the current ``scale`` and add to the stored credit, making that the new value of ``credit``.
    * Set ``scale`` to the stored scale.
    * Add this item to the output.

  * **Feedback** and **Warning**: Add this item to the output.

* Return the values of ``valid``, ``credit`` and ``output``.

The mark given to the student is the final ``credit`` multiplied by the marks available for the part.

Finally, the list of items in ``output`` is processed to produce a list of messages to show to the student.
Each message has a corresponding ``reason`` which determines whether it should be displayed as positive, negative or neutral feedback.
If the item changes the credit, the student is told the absolute change in credit, for example '1 mark was taken away'.
**Warning** items attach a message to the answer input field, rather than the list of feedback messages.

Examples
--------

An entire marking algorithm
***************************

As an example, here is the built-in marking algorithm for the number entry part.

We'll work backwards from the two final notes, ``mark`` and ``interpreted_answer``.

The ``interpreted_answer`` note is the simplest.
It first applies the check that the student's answer is valid, defined in ``validNumber`` and if it is, produces a numerical value calculated in the note ``studentNumber``::

    interpreted_answer (The student's answer, to be reused by other parts):
        apply(validNumber);
        studentNumber

In ``studentNumber``, we try to parse the student's answer using the notation styles chosen by the author::

    studentNumber (The student's answer, parsed as a number):
        if(settings["allowFractions"],
            parsedecimal_or_fraction(studentAnswer,settings["notationStyles"])
        ,
            parsedecimal(studentAnswer,settings["notationStyles"])
        )

This note will produce the value ``NaN`` ("not a number") if the student's answer is not in the right format.

The ``validNumber`` note produces feedback for this::

    validNumber (Is the student's answer a valid number?):
        if(isnan(studentNumber),
            warn(translate("part.numberentry.answer invalid"));
            fail(translate("part.numberentry.answer invalid"))
        ,
            true
        )

The ``cleanedStudentAnswer`` note produces a string in the canonical notation style, so that other parts of the algorithm don't need to worry about the notation style the student used::

    cleanedStudentAnswer:
        cleannumber(studentAnswer, settings["notationStyles"])

Now we can carry out the marking process, in the ``mark`` note::

    mark (Mark the student's answer):
        apply(validNumber);
        apply(numberInRange);
        assert(numberInRange,end());
        if(isFraction,
            apply(cancelled)
        ,
            apply(correctPrecision)
        )
     
First of all the ``validNumber`` note is applied, so if the student's answer is invalid then no more feedback is produced.

The student's answer is considered correct if it lies between the minimum and maximum accepted values specified by the author.
This is checked in ``numberInRange``::

    numberInRange (Is the student's number in the allowed range?):
        if(studentNumber>=minvalue and studentNumber<=maxvalue,
            correct()
        ,
            incorrect();
            end()
        )

If the student's answer is not in the required range, then the "your answer is incorrect" feedback is given, and marking stops here.
If the student's answer is in the required range, they are given the "your answer is correct" feedback, which provisionally sets the credit to 1.

Authors quite often get the minimum and maximum value the wrong way round, particularly when they're defined as ``x - tol`` and ``x + tol`` and they forget to account for the case that ``tol`` is negative.
It doesn't help anyone to have an impossible range, so the marking algorithm first computes ``raw_minvalue`` and ``raw_maxvalue``, then ensures the final ``minvalue`` and ``maxvalue`` are the right way round::

    minvalue: min(raw_minvalue,raw_maxvalue)

    maxvalue: max(raw_minvalue,raw_maxvalue)

The author can require that the student gives their answer to a certain precision, specified in terms of decimal places or significant figures.
The minimum and maximum values are rounded to the same precision as the student's answer, so that the author doesn't need to worry about rounding::

    studentPrecision:
        switch(
            settings["precisionType"]="dp", max(settings["precision"],countdp(cleanedStudentAnswer)),
            settings["precisionType"]="sigfig", max(settings["precision"],countsigfigs(cleanedStudentAnswer)),
            0
        )

    raw_minvalue:
        switch(
            settings["precisionType"]="dp", precround(settings["minvalue"],studentPrecision),
            settings["precisionType"]="sigfig", siground(settings["minvalue"],studentPrecision),
            settings["minvalue"]
        )

    raw_maxvalue:
        switch(
            settings["precisionType"]="dp", precround(settings["maxvalue"],studentPrecision),
            settings["precisionType"]="sigfig", siground(settings["maxvalue"],studentPrecision),
            settings["maxvalue"]
        )

The line ``assert(numberInRange,end());`` ends the marking if the student's number is not in the required range.
If it is, then there are penalties that might be applied, based on the precision of the student's answer.

If the student's answer is a fraction, they might be required to cancel it::

    isFraction (Is the student's answer a fraction?):
        "/" in studentAnswer

    numerator (The numerator of the student's answer, or 0 if not a fraction):
        if(isFraction,
            parsenumber(split(studentAnswer,"/")[0],settings["notationStyles"])
        ,
            0
        )

    denominator (The numerator of the student's answer, or 0 if not a fraction):
        if(isFraction,
            parsenumber(split(studentAnswer,"/")[1],settings["notationStyles"])
        ,
            0
        )

    cancelled (Is the student's answer a cancelled fraction?):
        assert(isFraction and gcd(numerator,denominator)=1,
            assert(not settings["mustBeReduced"],
                multiply_credit(settings["mustBeReducedPC"],translate("part.numberentry.answer not reduced"))
            );
            false
        )

The ``isFraction`` note produces a boolean value representing whether the student's answer is written as a fraction or not.
It doesn't apply any feedback items directly.

The ``cancelled`` note uses ``assert`` to exit if the condition is satisfied; if it's not, then a ``multiply_credit`` feedback item takes away a percentage of the credit awarded so far.
The ``false`` at the end of the ``assert`` block makes sure that the note's value represents whether the student's answer is cancelled (``assert`` returns true if the condition is satisfied).

If the student's answer is not a fraction, then it is an integer or a decimal, and a precision restriction might apply::

    correctPrecision (Has the student's answer been given to the desired precision?):     
        if(togivenprecision(cleanedStudentAnswer,settings['precisionType'],settings['precision'],settings["strictPrecision"]),
            true
        ,
            multiply_credit(settings["precisionPC"],settings["precisionMessage"]);
            false
        )

Like the ``cancelled`` note, this one both produces a boolean value representing whether the student's answer was given to the right precision, and a feedback item subtracting a percentage of the credit awarded so far if it wasn't.

An extended marking algorithm
*****************************

This extension to the built-in number entry algorithm marks the student's answer correct only if it is divisible by both 2 and 3::

    required_factors (Factors that the student's answer must have):
      [2,3]

    isInteger (Is the student's answer an integer?):
      assert(isint(studentNumber),
        fail("Your answer is not an integer.");
        warn("Your answer must be an integer.");
        false
      )

    divisible_by_factors (Is the student's answer divisible by all the required factors?):
      map(
        if(mod(studentNumber,n)=0,
          add_credit(1/len(required_factors), "Your number is divisible by "+n+"."),
          negative_feedback("Your number is not divisible by "+n+".")
        ),
        n,
        required_factors
      )

    mark (Mark the student's answer):
      apply(validNumber);
      apply(isInteger);
      apply(divisible_by_factors)

All of the notes defined in the base algorithm are available, so ``validNumber`` is used to check that the student's answer can be parsed, and ``studentNumber`` represents the numerical value.

The ``required_factors`` note is static - it's effectively used as a constant, so the list of required factors is only defined in one place and is easy to edit.

After checking that the student's answer can be parsed, the ``isInteger`` note marks the student's answer as invalid if it is not an integer.
When it's clear that the student has misunderstood the instructions, marking their answer as invalid rather than incorrect gives them an explanation of what they have done wrong, and an opportunity to try again.

Finally, the note ``divisible_by_factors`` runs through the required factors, and adds an equal proportion of the available credit for each one that is satisfied.
If the student's number does not have a certain factor, a ``negative_feedback`` item tells them this, without modifying the score.
