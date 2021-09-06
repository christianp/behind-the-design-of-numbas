Themes
======

.. page_status::
    :kind: outline

Problem
-------

Separate display from logic.

Want to allow:

* Simple appearance changes - colours, logo, etc.
* Integrate with other interfaces, e.g. SCHOLAR.
* More complex changes to the way exams are presented, e.g. printed worksheets.

Solution
--------

A theme is a collection of HTML templates and associated static resources, as well as JavaScript that controls the binding between the page and the exam model.

For historical reasons, the exam is compiled to XML, and then content is transformed with XSLT to HTML.
