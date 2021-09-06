Custom part types
=================

.. page_status::
    :kind: outline

Problem
-------

Have a common assessment task that isn't covered by the built-in part types.

Want to customise the input method and/or the marking algorithm.

Should be reusable but configurable.

Solution
--------

A custom part type is:

* A list of settings for question authors to configure behaviour.
* An input method.
* A marking algorithm.

There are a few kinds of settings to choose from.
Most allow variables to be substituted in.

The input widgets are configurable following settings.
Input options can be marked as 'static', or given by a JME expression in the settings.

An input widget produces a JME value that the marking algorithm can use.
There's no mechanism for giving warnings before submission at the moment - this could be a note in the marking algorithm?

Some really simple custom part types just make it easier to set up common patterns, e.g. the "Yes/No" type, which is effectively a "choose one from a list" with a fixed list of choices, and the only option is "is the answer yes?"

Some extensions come with a custom part type, e.g. the "quantity with units" part type.
