
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

.. code-block:: bash

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


HyML MiNiMaL codebase
----------------------

Because codebase for HyML MiNiMaL implementation is roughly 60 lines
only (without comments), it is provided here with structural comments and 
linebreaks for the inspection. More detailed comments are available in the
`minimal.hy <https://github.com/markomanninen/hyml/blob/master/hyml/minimal.hy>`__
source file.

.. code-block:: hylang
    :linenos:

    ; eval and compile variables, constants and functions for ml, defvar, deffun, and include macros
    (eval-and-compile
    
      ; global registry for variables and functions
      (setv variables-and-functions {})
    
      ; internal constants
      (def **keyword** "keyword") (def **unquote** "unquote")
      (def **splice** "unquote_splice") (def **unquote-splice** (, **unquote** **splice**))
      (def **quote** "quote") (def **quasi** "quasiquote")
      (def **quasi-quote** (, **quote** **quasi**))

      ; detach keywords and content from code expression
      (defn get-content-attributes [code]
        (setv content [] attributes [] kwd None)
        (for [item code]
             (do (if (iterable? item)
                     (if (= (first item) **unquote**) (setv item (eval (second item) variables-and-functions))
                         (in (first item) **quasi-quote**) (setv item (name (eval item)))))
                 (if-not (keyword? item)
                   (if (none? kwd)
                       (.append content (parse-mnml item))
                       (.append attributes (, kwd (parse-mnml item)))))
                 (if (and (keyword? kwd) (keyword? item))
                     (.append attributes (, kwd (name kwd))))
                 (if (keyword? item) (setv kwd item) (setv kwd None))))
        (if (keyword? kwd)
            (.append attributes (, kwd (name kwd))))
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

* parentheses to define hierarchical (nested) structure of the document
* all opened parentheses must have closing parentheses pair
* the first item of the expression is the tag name
* next items in the expression are either:

  * attribute-value pairs (:attribute "value")
  * content wrapped with double quotes ("content")
  * sub expression
  * nothing

* between keywords, keyword values, and content there must a whitespace
  separator
* whitespace is not needed when a new expression starts or ends
  (opening and closing parentheses).

There is no limit on nested levels. There is no limit on how many
attribute-value pairs you want to use. Also it doesn't matter in what
order you define tag content and keywords, althougt it might be easier
to read for others, if the keywords are introduced first and then the
content. However, all keywords are rendered in the same order they have
been presented in markup. Also a content and sub nodes are rendered
similarly in the given order.

Main differences to XML syntax are:

-  instead of wrappers ``<`` and ``>``, parentheses ``(`` and ``)`` are
   used
-  there can't be a separate end tag
-  given expression does not need to have a single root node
-  see other possible differences comparing to
   `wiki/XML <https://en.wikipedia.org/wiki/XML#Well-formedness_and_error-handling>`__


Special chars
~~~~~~~~~~~~~

In addition to basic syntax there are three other symbols for advanced
code generation. They are:

-  quasiquote `````
-  unquote ``~``
-  unquote splice ``~@``

These all are symbols used in Hy `macro
notation <http://docs.hylang.org/en/latest/language/api.html#quasiquote>`__,
so they should be self explanatory. But to make everything clear, in the
MiNiMaL macro they work other way around.

Unquote (``~``) and unquote-splice (``~@``) gets you back to the Hy code
evaluation mode. And quasiquote (`````) sets you back to MiNiMaL macro
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
keywords) in the ``tag``. Sub node instead has content
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

    (ml (~(+ "t" "a" "g"))) ; <tag/>

This is useful if tag names collide with Hy internal symbols and
datatypes. For example, the symbol ``J`` is reserved for complex number
type. Instead of writing: ``(ml (J))`` which produces ``<1j/>``, you
should use: ``(ml (~"J"))``.

Attribute name and value
^^^^^^^^^^^^^^^^^^^^^^^^

You can generate an attribute name or a value with Hy by using ~ symbol.
Generated attribute name must be a keyword however:

.. code-block:: hylang

    (ml (tag ~(keyword (.join "" ['a 't 't 'r])) "value")) ; <tag attr="value"/>

And same for value:

.. code-block:: hylang

    (ml (tag :attr ~(+ "v" "a" "l" "u" "e"))) ; <tag attr="value"/>

Content
^^^^^^^

You can generate content with Hy by using ~ symbol:

.. code-block:: hylang

    (ml (tag ~(.upper "content"))) ; <tag>CONTENT</tag>


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

Output:

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

Output:

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

Output:

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

Output:

.. code-block:: xml

    <tag>Generator inside: <sub>content</sub></tag>

Tag names, attribute values, and tag content can be also single
pre-quoted strings. It doesn't matter because in the final process of
evaluating the component the string representation of the symbol is
retrieved.

.. code-block:: hylang

    [(ml ('tag)) (ml (`tag)) (ml (tag)) (ml ("tag"))]


.. parsed-literal::

    ['<tag/>', '<tag/>', '<tag/>', '<tag/>']



With keywords, however, single pre-queted strings will get parsed as a
content.

.. code-block:: hylang

    [(ml (tag ':attr)) (ml (tag `:attr))]


.. parsed-literal::

    ['<tag>attr</tag>', '<tag>attr</tag>']



Also if keyword marker is followed by a string literal, keyword will be
empty, thus not a correctly wormed keyword value pair.

.. code-block:: hylang

    (ml (tag :"attr"))


.. code-block:: xml

    <tag ="attr"/>



So only working version of keyword notation is ``:{symbol}`` or unquoted
``~(keyword {expression})``. Also keywords without value are interpreted
as a keyword having the same value as the keyword name (called boolean
attributes).

.. code-block:: hylang

    [(ml (tag :disabled)) (ml (tag ~(keyword "disabled")))]


.. parsed-literal::

    ['<tag disabled="disabled"/>', '<tag disabled="disabled"/>']



If you wish to define multiple boolean attributes together with content,
you can collect them at the end of the expression. Note that in XML
boolean attributes cannot be minimized similar to HTML. Attributes
always needs to have a value pair.

.. code-block:: hylang

    (ml (tag "Content" :disabled :enabled))


.. code-block:: xml

    <tag disabled="disabled" enabled="enabled">Content</tag>



One more thing with keywords is that if the same keyword value pair is
given multiple times, it will show up in the mark up in the same order,
as multiple. Depending on the markup parser, the last attribute might be
valuated OR parser might give an error, because by XML Standard attibute
names should be unique and not repeated under the same element.

.. code-block:: hylang

    (ml (tag :attr :attr "attr2"))


.. code-block:: xml

    <tag attr="attr" attr="attr2"/>


Test main features
------------------

Assert tests for all main features presented above. There should be no
output after running these. If there is, then there is a problem!

.. code-block:: hylang

    ;;;;;;;;;
    ; basic ;
    ;;;;;;;;;
    ; empty things
    (assert (= (ml) ""))
    (assert (= (ml"") ""))
    (assert (= (ml "") ""))
    (assert (= (ml ("")) "</>"))
    ; tag names
    (assert (= (ml (tag)) "<tag/>"))
    (assert (= (ml (TAG)) "<TAG/>"))
    (assert (= (ml (~(.upper "tag"))) "<TAG/>"))
    (assert (= (ml (tag "")) "<tag></tag>"))
    ; content cases
    (assert (= (ml (tag "content")) "<tag>content</tag>"))
    (assert (= (ml (tag "CONTENT")) "<tag>CONTENT</tag>"))
    (assert (= (ml (tag ~(.upper "content"))) "<tag>CONTENT</tag>"))
    ; attribute names and values
    (assert (= (ml (tag :attr "val")) "<tag attr=\"val\"/>"))
    (assert (= (ml (tag ~(keyword "attr") "val")) "<tag attr=\"val\"/>"))
    (assert (= (ml (tag :attr "val" "")) "<tag attr=\"val\"></tag>"))
    (assert (= (ml (tag :attr "val" "content")) "<tag attr=\"val\">content</tag>"))
    (assert (= (ml (tag :ATTR "val")) "<tag ATTR=\"val\"/>"))
    (assert (= (ml (tag ~(keyword (.upper "attr")) "val")) "<tag ATTR=\"val\"/>"))
    (assert (= (ml (tag :attr "VAL")) "<tag attr=\"VAL\"/>"))
    (assert (= (ml (tag :attr ~(.upper "val"))) "<tag attr=\"VAL\"/>"))
    ; nested tags
    (assert (= (ml (tag (sub))) "<tag><sub/></tag>"))
    ; unquote splice
    (assert (= (ml (tag ~@(list-comp `(sub ~(str item)) [item [1 2 3]])))
               "<tag><sub>1</sub><sub>2</sub><sub>3</sub></tag>"))
    ; variables
    (defvar x "variable")
    (assert (= (ml (tag ~x)) "<tag>variable</tag>"))
    ; functions
    (deffun f (fn [x] x))
    (assert (= (ml (tag ~(f "function"))) "<tag>function</tag>"))
    ; templates
    (with [f (open "test.hy" "w")] (f.write "(tag)"))
    (assert (= (ml ~@(include "test.hy")) "<tag/>"))
    ;;;;;;;;;;;
    ; special ;
    ;;;;;;;;;;;
    ; tag names
    (assert (= (ml (J)) "<1j/>"))
    (assert (= (ml (~"J")) "<J/>"))
    (assert (= [(ml ('tag)) (ml (`tag)) (ml (tag)) (ml ("tag"))] (* ["<tag/>"] 4)))
    ; attribute values
    (assert (= [(ml (tag :attr 'val)) (ml (tag :attr `val)) (ml (tag :attr val)) (ml (tag :attr "val"))]
               (* ["<tag attr=\"val\"/>"] 4)))
    ; content
    (assert (= [(ml (tag 'val)) (ml (tag `val)) (ml (tag val)) (ml (tag "val"))]
               (* ["<tag>val</tag>"] 4)))
    ; keyword processing
    (assert (= [(ml (tag ':attr)) (ml (tag `:attr))] ["<tag>attr</tag>" "<tag>attr</tag>"]))
    (assert (= (ml (tag :"attr")) "<tag =\"attr\"/>"))
    (assert (= [(ml (tag :attr)) (ml (tag ~(keyword "attr")))] ["<tag attr=\"attr\"/>" "<tag attr=\"attr\"/>"]))
    (assert (= (ml (tag :attr1 :attr2)) "<tag attr1=\"attr1\" attr2=\"attr2\"/>"))
    (assert (= (ml (tag Content :attr1 :attr2)) "<tag attr1=\"attr1\" attr2=\"attr2\">Content</tag>"))
    (assert (= (ml (tag :attr1 :attr2 Content)) "<tag attr1=\"attr1\" attr2=\"Content\"/>"))
    ; no space between attribute name and value as a string literal
    (assert (= (ml (tag :attr"val")) "<tag attr=\"val\"/>"))
    ; no space between tag, keywords, keyword value, and content string literals
    (assert (= (ml (tag"content":attr"val")) "<tag attr=\"val\">content</tag>"))
    ;;;;;;;;;
    ; weird ;
    ;;;;;;;;;
    ; quote should not be unquoted or surpressed
    (assert (= (ml (quote :quote "quote" "quote")) "<quote quote=\"quote\">quote</quote>"))
    ; tag name, keyword name, value and content can be same
    (assert (= (ml (tag :tag "tag" "tag")) "<tag tag=\"tag\">tag</tag>"))
    ; multiple same attribute names stays in the markup in the reserved order
    (assert (= (ml (tag :attr "attr1" :attr "attr2")) "<tag attr=\"attr1\" attr=\"attr2\"/>"))


The `MIT <http://choosealicense.com/licenses/mit/>`__ License
-------------------------------------------------------------

Copyright (c) 2017 Marko Manninen
