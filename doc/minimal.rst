
HyML MiNiMaL
============

Minimal markup language generator in Hy
---------------------------------------

`HyML <https://github.com/markomanninen/hyml>`__ (acronym for Hy Markup
Language) is a set of macros to generate XML, XHTML, and HTML code in
Hy.

HyML MiNiMaL macro is departed from the more extensive document and
validation oriented "full" version of HyML. HyML MiNiMaL is meant to be
used as a minimal codebase to generate XML (Extensible Markup Language)
with the next features:

1. closely resembling syntax with XML
2. ability to mix Hy / Python program code within markup
3. processing lists and external templates
4. using custom variables and functions

You can use HyML MiNiMaL for:

-  static XML / XHTML / HTML content and file generation
-  render html code for the Jupyter Notebook for example
-  attach it to a server for dynamic html output generation
-  practice and study
   `DSL <https://en.wikipedia.org/wiki/Domain-specific_language>`__ and
   macro (Lisp) programming
-  challenge your imagination

To compare with HyML XML / HTML macros, MiNiMaL means that there is
no tag name validation and no tag and attribute minimize techniques
utilized. If you need them, you should see `full HyML
documentation <http://hyml.readthedocs.io/en/latest/#>`__.

Ready, steady, go!
------------------

Project is hosted at: https://github.com/markomanninen/hyml

Install
~~~~~~~

For easy install, use
`pip <https://pip.pypa.io/en/stable/installing/>`__ Python repository
installer:

.. code-block:: shell

    $ pip install hyml

This will install only the necessary source files for HyML, no example
templates or Jupyter Notebook files that are for presentation only.

Import
~~~~~~

Then import MiNiMaL macros:

.. code-block:: hylang

    (require (hyml.minimal (*)))

Run
~~~

And run the simple example:

.. code-block:: hylang

    (ml (tag :attr "value" (sub "Content")))

That should output:

.. code-block:: xml

    <tag attr="value"><sub>Content</sub></tag>

Jupyter Notebook
~~~~~~~~~~~~~~~~

If you want to play with HyML Notebook documents, you should download
the whole `HyML
repository <https://github.com/markomanninen/hyml/archive/master.zip>`__
(or clone it with
``$ git clone https://github.com/markomanninen/hyml.git``) to your
computer. It contains all necessary templates to get everything running
as presented in the HyML MiNiMaL `Notebook document <http://nbviewer.jupyter.org/github/markomanninen/hyml/blob/master/HyML%20-%20Minimal.ipynb>`__.

Hy MiNiMaL code (all)
---------------------

Because codebase for HyML MiNiMaL implementation is roughly 50 lines
only (without comments), it is provided here with structural comments and 
linebreaks for introspection. More detailed comments are available in the
`minimal.hy <https://github.com/markomanninen/hyml/blob/master/hyml/minimal.hy>`__
source file.

.. code-block:: hylang
   :linenos:

    ; eval and compile variables, constants and functions for ml, defvar, deffun, and include macros
    (eval-and-compile

      ; global registry for variables and functions
      (setv variables-and-functions {})

      ; internal constants
      (def **keyword** "keyword")
      (def **unquote** "unquote")
      (def **splice** "unquote_splice")
      (def **unquote-splice** (, **unquote** **splice**))

      ; detach keywords and content from code expression
      (defn get-content-attributes [code]
        (setv content [] attributes [] kwd None)
        (for [item code]
             (do (if (and (= (first item) **unquote**)
                          (= (first (second item)) **keyword**))
                     (setv item (eval (second item))))
                 (if-not (keyword? item)
                   (if (none? kwd)
                       (.append content (parse-mnml item))
                       (.append attributes (, kwd (parse-mnml item)))))
                 (if (keyword? item) (setv kwd item) (setv kwd None))))
        (, content attributes))

      ; recursively parse expression
      (defn parse-mnml [code] 
        (if (coll? code)
            (do (setv tag (catch-tag (first code)))
                (if (in tag **unquote-splice**)
                    (if (= tag **unquote**)
                        (str (eval (second code) variables-and-functions))
                        (.join "" (map parse-mnml (eval (second code) variables-and-functions))))
                    (do (setv (, content attributes) (get-content-attributes (drop 1 code)))
                        (+ (tag-start tag attributes (empty? content))
                           (if (empty? content) ""
                               (+ (.join "" (map str content)) (+ "</" tag ">")))))))
            (if (none? code) "" (str code))))

      ; detach tag from expression
      (defn catch-tag [code]
        (if (and (iterable? code) (= (first code) **unquote**))
            (eval (second code))
            (try (name (eval code))
                 (except (e Exception) (str code)))))

      ; concat attributes
      (defn tag-attributes [attr]
        (if (empty? attr) ""
            (+ " " (.join " " (list-comp
              (% "%s=\"%s\"" (, (name kwd) (name value))) [[kwd value] attr])))))

      ; create start tag
      (defn tag-start [tag-name attr short]
        (+ "<" tag-name (tag-attributes attr) (if short "/>" ">"))))

    ; global variable registry handler
    (defmacro defvar [&rest args]
      (setv l (len args) i 0)
      (while (< i l) (do
        (assoc variables-and-functions (get args i) (get args (inc i)))
        (setv i (+ 2 i)))))

    ; global function registry handler
    (defmacro deffun [name func]
      (assoc variables-and-functions name (eval func)))

    ; include functionality for template engine
    (defmacro include [template]
      `(do (import [hy.importer [tokenize]])
           (with [f (open ~template)]
             (tokenize (+ "~@`(" (f.read) ")")))))

    ; main MiNiMaL macro to be used. passes code to parse-mnml
    (defmacro ml [&rest code]
      (.join "" (map parse-mnml code)))


Features
--------

Basic syntax
~~~~~~~~~~~~

MiNiMaL macro syntax is simple and mostly follows the rules of Hy
code. Syntax of the expression consists of:

-  parentheses to define hierarchical (nested) structure of the document
-  all opened parentheses must have closing parentheses pair
-  the first item of the expression is the tag name
-  next items in the expression are either:
-  attribute-value pairs (:attribute "value") or
-  content wrapped with double quotes ("content") or
-  sub expression or
-  nothing
-  between keywords, keyword values, and content there must a whitespace
   separator
-  whitespace is not needed when a new expression starts or ends
   (opening and closing parentheses).

There is no limit on nested levels. There is no limit on how many
attribute-value pairs you want to use. Also it doesn't matter in what
order you define tag content and keywords, althougt it might be easier
to read for others, if the keywords are introduced first and then the
content. However, all keywords are rendered in the same order they have
been presented in markup. Also a content and sub nodes are rendered
similarly in the given order.

Main differences to XML syntax are:

-  instead of wrapper ``<`` and ``>`` parentheses ``(`` and ``)`` are
   used
-  there is no need to have a separate end tag
-  given expression does not need to have a single root node
-  see other possible differences comparing to
   `wiki/XML <https://en.wikipedia.org/wiki/XML#Well-formedness_and_error-handling>`__

Special chars
~~~~~~~~~~~~~

In addition to basic syntax there are three other symbols for advanced
code generation. They are:

-  quasiquote (\`)
-  unquote (``~``)
-  unquote splice (``~@``)

These all are symbols used in Hy `macro
notation <http://docs.hylang.org/en/latest/language/api.html#quasiquote>`__,
so they should be self explanatory. But to make everything clear, in the
MiNiMaL macro they work other way around.

Unquote (``~``) and unquote-splice (``~@``) gets you back to the Hy code
evaluation mode. And quasiquote (\`) sets you back to MiNiMaL macro
mode. This is natural when you think that MiNiMaL macro is a quoted
code in the first place. So if you want to evaluate Hy code inside it,
you need to do it inside unquote.

But let us start from the simple example first.

Simple example
~~~~~~~~~~~~~~

The simple example utilizing above features is:

.. code-block:: hylang

    (tag :attr "value" (sub "Content"))

``tag`` is the first element of the expression, so it regarded as a tag
name. ``:attr "value"`` is the keyword-value (attribute-value) -pair.
``(sub`` starts a new expression. So there is no other content (or
keywords) in the tag. Sub node instead has titlecase content
``"Content"`` given.

Output would be:

.. code-block:: xml

    <tag attr="value"><sub>Content</sub></tag>

Process components with unquote syntax (~)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any element (tag name, tag attribute and value, tag content) can be generated instead of hardcoded to the expression.

Tag name
^^^^^^^^

You can generate a tag name with Hy code by using ~ symbol:

.. code-block:: hylang

    (ml (~(+ "t" "a" "g")))




.. code-block:: xml

    <tag/>



This is useful if tag names collide with Hy internal symbols and
datatypes. For example, the symbol ``J`` is reserved for complex number
type. Instead of writing: ``(ml (J))`` which produces ``<1j/>``, you
should use: ``(ml (~"J"))``.

Attribute name and value
^^^^^^^^^^^^^^^^^^^^^^^^

You can generate an attribute name or a value with Hy by using ~ symbol.
Generated attribute name must be a keyword however:

.. code-block:: hylang

    (ml (tag ~(keyword (.join "" ['a 't 't 'r])) "value"))




.. code-block:: xml

    <tag attr="value"/>



.. code-block:: hylang

    (ml (tag :attr ~(+ "v" "a" "l" "u" "e")))




.. code-block:: xml

    <tag attr="value"/>



Content
^^^^^^^

You can generate content with Hy by using ~ symbol:

.. code-block:: hylang

    (ml (tag ~(.upper "content")))




.. code-block:: xml

    <tag>CONTENT</tag>



Using custom variables and functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can define custom variables and functions for the MiNiMaL macro.
Variables and functions are stored on the common registry and availble
on the macro expansion. You can access predefined symbols when quoting
(~) the expression.

.. code-block:: hylang

    ; define variables with defvar macro
    (defvar firstname "Dennis"
            lastname "McDonald")

    ; define functions with deffun macro
    (deffun wholename (fn [x y] (+ y ", " x)))

    ; use variables and functions with unquote / unquote splice
    (ml (tag ~(wholename firstname lastname)))




.. code-block:: xml

    <tag>McDonald, Dennis</tag>



Process lists with unquote splice syntax (~@)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unquote-splice is a special symbol to be used with the list and the
template processing. It is perhaps the most powerful feature in the
MiNiMaL macro.

Generate list of items
^^^^^^^^^^^^^^^^^^^^^^

You can use list comprehension function to generate a list of xml
elements. Hy code, sub expressions, and variables / functions work
inside unquote spliced expression. You need to quote a line, if it
contains a sub MiNiMaL expression.

.. code-block:: hylang

    ; generate 5 sub tags and use enumerated numeric value as a content
    (ml (tag ~@(list-comp `(sub ~(str item)) [item (range 5)])))




.. code-block:: xml

    <tag><sub>0</sub><sub>1</sub><sub>2</sub><sub>3</sub><sub>4</sub></tag>



Using templates
~~~~~~~~~~~~~~~

Let us first show the template content existing in the external file:

.. code-block:: hylang

    (with [f (open "note.hy")] (print (f.read)))


.. code-block:: hylang

    (note :src "https://www.w3schools.com/xml/note.xml"
      (to ~to)
      (from ~from)
      (heading ~heading)
      (body ~body))
    

Then we will define variables and a function to be used inside
MiNiMaL macro:

.. code-block:: hylang

    (defvar to "Tove"
            from "Jani"
            heading "Reminder"
            body "Don't forget me this weekend!")

And finally include and render the template:

.. code-block:: hylang

    (import (hyml.helpers (indent)))
    (print (indent (ml ~@(include "note.hy"))))


.. code-block:: xml

    <note src="https://www.w3schools.com/xml/note.xml">
    	<to>Tove</to>
    	<from>Jani</from>
    	<heading>Reminder</heading>
    	<body>Don't forget me this weekend!</body>
    </note>
    

Special features
----------------

These are not deliberately implemented features, but a conequence of the
HyML MiNiMaL implementation and how Hy works.

Nested MiNiMaL macros
~~~~~~~~~~~~~~~~~~~~~~~~~

It is possible to call MiNiMaL macro again inside unquoted code:

.. code-block:: hylang

    (ml (tag ~(+ "Generator inside: " (ml (sub "content")))))




.. code-block:: xml

    <tag>Generator inside: <sub>content</sub></tag>



Test main features
------------------

Assert tests for all main features presented above. There should be no
output after running these. If there is, then there is a problem!

.. code-block:: hylang

    (assert (= (ml ("")) "</>"))
    (assert (= (ml (tag)) "<tag/>"))
    (assert (= (ml (TAG)) "<TAG/>"))
    (assert (= (ml (~(.upper "tag"))) "<TAG/>"))
    (assert (= (ml (tag "")) "<tag></tag>"))
    (assert (= (ml (tag "content")) "<tag>content</tag>"))
    (assert (= (ml (tag "CONTENT")) "<tag>CONTENT</tag>"))
    (assert (= (ml (tag ~(.upper "content"))) "<tag>CONTENT</tag>"))
    (assert (= (ml (tag :attr "val")) "<tag attr=\"val\"/>"))
    (assert (= (ml (tag ~(keyword "attr") "val")) "<tag attr=\"val\"/>"))
    (assert (= (ml (tag :attr "val" "")) "<tag attr=\"val\"></tag>"))
    (assert (= (ml (tag :attr "val" "content")) "<tag attr=\"val\">content</tag>"))
    (assert (= (ml (tag :ATTR "val")) "<tag ATTR=\"val\"/>"))
    (assert (= (ml (tag ~(keyword (.upper "attr")) "val")) "<tag ATTR=\"val\"/>"))
    (assert (= (ml (tag :attr "VAL")) "<tag attr=\"VAL\"/>"))
    (assert (= (ml (tag :attr ~(.upper "val"))) "<tag attr=\"VAL\"/>"))
    (assert (= (ml (tag (sub))) "<tag><sub/></tag>"))
    (assert (= (ml (tag ~@(list-comp `(sub ~(str item)) [item [1 2 3]])))
               "<tag><sub>1</sub><sub>2</sub><sub>3</sub></tag>"))
    
    (defvar x "variable")
    (assert (= (ml (tag ~x)) "<tag>variable</tag>"))
    
    (deffun f (fn [x] x))
    (assert (= (ml (tag ~(f "function"))) "<tag>function</tag>"))
    
    (with [f (open "test.hy" "w")] (f.write "(tag)"))
    (assert (= (ml ~@(include "test.hy")) "<tag/>"))
    
    ; special
    (assert (= (ml (J)) "<1j/>"))

The `MIT <http://choosealicense.com/licenses/mit/>`__ License
-------------------------------------------------------------

Copyright (c) 2017 Marko Manninen
