
HyML ``MiNiMaL``
================

Minimal Markup Language generator in Hy
---------------------------------------

`HyML <https://github.com/markomanninen/hyml>`__ (acronym for Hy Markup
Language) is a set of macros to generate XML, XHTML, and HTML code in
Hy. HyML ``MiNiMaL`` is a minimal codebase to generate XML (Extensible
Markup Language) with next features:

1. closely resembling syntax with XML
2. tag names and attribute names are forced to be in lowercase format
3. ability to evaluate Hy program code on macro expansion
4. processing lists and templates
5. custom variables and functions

You can use HyML ``MiNiMaL`` for:

-  static xml / xhtml / html content and file generation
-  generate html code for Jupyter Notebook for example
-  attach it to the server for dynamic html output generation
-  practice and study macro (Lisp) programming
-  challenge your imagination

Install, import, and run
------------------------

Project is hosted at: https://github.com/markomanninen/hyml

For easy install, use:

.. code:: shell

    $ pip install hyml

Then import ``MiNiMaL`` macros:

.. code:: clojure

    (require (hyml.minimal (*)))

And run example:

.. code:: clojure

    (mnml (tag :attr "value" (sub "Content")))

That should output:

.. code:: xml

    <tag attr="value"><sub>Content</sub></tag>

Hy code (all)
-------------

Because codebase for HyML ``MiNiMaL`` implementation is roughly 50 lines
only, it will be provided here for introspection:

.. code:: python

    ; eval and compile variables, constants and functions for mnml, defvar, deffun, and include macros
    (eval-and-compile
      ; global registry for variables and functions
      (setv variables-and-functions {})
      ; internal constants
      (def **keyword** "keyword") (def **unquote** "unquote")
      (def **splice** "unquote_splice") (def **unquote-splice** (, **unquote** **splice**))
      ; dettach keywords and content from code expression
      (defn get-content-attributes [code]
        (setv content [] attributes [] kwd None)
        (for [item code]
             (do 
               (if (and (= (first item) **unquote**)
                        (= (first (second item)) **keyword**))
                   (setv item (eval (second item))))
               (if-not (keyword? item)
                 (if (none? kwd)
                     (.append content (parse-mnml item))
                     (.append attributes (, (.lower kwd) (parse-mnml item)))))
               (if (keyword? item) (setv kwd item) (setv kwd None))))
        (, content attributes))
      ; recursively parse expression
      (defn parse-mnml [code] 
        (if (coll? code)
            (do
              (setv tag (.lower (catch-tag (first code))))
              (if (in tag **unquote-splice**)
                  (.join "" (map parse-mnml (eval (second code) variables-and-functions)))
                  (do
                    (setv (, content attributes) (get-content-attributes (drop 1 code)))
                    (+ (tag-start tag attributes (empty? content))
                       (if (empty? content) ""
                           (+ (.join "" (map str content)) (+ "</" tag ">")))))))
            (if (none? code) "" (str code))))
      ; dettach tag from expression
      (defn catch-tag [code]
        (if (= (first code) **unquote**)
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
    ; global variable handler
    (defmacro defvar [&rest args]
      (setv l (len args) i 0)
      (while (< i l)
        (do
          (assoc variables-and-functions (get args i) (get args (inc i)))
          (setv i (+ 2 i)))))
    ; global function handler
    (defmacro deffun [name func]
      (assoc variables-and-functions name (eval func)))
    ; include functionality for template engine
    (defmacro include [template]
      `(do
        (import [hy.importer [tokenize]])
        (with [f (open ~template)]
          (tokenize (+ "~@`(" (f.read) ")")))))
    ; main MiNiMaL macro to be used. passes code to parse-mnml
    (defmacro mnml [&rest code]
      (.join "" (map parse-mnml code)))

Simple example
~~~~~~~~~~~~~~

.. code:: python

    (mnml (tag :attr "value" (sub "Content")))




.. parsed-literal::

    '<tag attr="value"><sub>Content</sub></tag>'



Features
--------

Process components with unquote syntax (~)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate tag name
^^^^^^^^^^^^^^^^^

.. code:: python

    (mnml (~(+ "t" "a" "g")))




.. parsed-literal::

    '<tag/>'



Generate attribute name and value
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    (mnml (tag ~(keyword (.join "" ['a 't 't 'r])) ~(+ "v" "a" "l")))




.. parsed-literal::

    '<tag attr="val"/>'



Generate content
^^^^^^^^^^^^^^^^

.. code:: python

    (mnml (tag ~(.upper "content")))




.. parsed-literal::

    '<tag>CONTENT</tag>'



Process lists with unquote splice syntax (~@)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Generate list of items
^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    (mnml (tag ~@(list-comp `(sub ~(str item)) [item [1 2 3]])))




.. parsed-literal::

    '<tag><sub>1</sub><sub>2</sub><sub>3</sub></tag>'



Custom variables and functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    ; define variables with defvar macro
    (defvar firstname "Dennis"
            lastname "McDonald")
    ; define functions with deffun macro
    (deffun wholename (fn [x y] (+ y ", " x)))
    ; use variables and functions with unquote / unquote splice
    (mnml (tag ~(wholename firstname lastname)))




.. parsed-literal::

    '<tag>McDonald, Dennis</tag>'



Templates
~~~~~~~~~

.. code:: python

    ; show template file content
    (with [f (open "note.hy")] (print (f.read)))


.. parsed-literal::

    (note :src "https://www.w3schools.com/xml/note.xml"
      (to ~to)
      (from ~from)
      (heading ~heading)
      (body ~body))
    

.. code:: python

    ; define variables for template
    (defvar to "Tove"
            from "Jani"
            heading "Reminder"
            body "Don't forget me this weekend!")
    ; include and render template
    (print
      (mnml ~@(include "note.hy")))


.. parsed-literal::

    <note src="https://www.w3schools.com/xml/note.xml"><to>Tove</to><from>Jani</from><heading>Reminder</heading><body>Don't forget me this weekend!</body></note>
    

Test main features
------------------

Assert tests for all main features:

.. code:: python

    (assert (= (mnml (tag)) "<tag/>"))
    (assert (= (mnml (TAG)) "<tag/>"))
    (assert (= (mnml (~(.upper "tag"))) "<tag/>"))
    (assert (= (mnml (tag "")) "<tag></tag>"))
    (assert (= (mnml (tag "content")) "<tag>content</tag>"))
    (assert (= (mnml (tag "CONTENT")) "<tag>CONTENT</tag>"))
    (assert (= (mnml (tag ~(.upper "content"))) "<tag>CONTENT</tag>"))
    (assert (= (mnml (tag :attr "val")) "<tag attr=\"val\"/>"))
    (assert (= (mnml (tag ~(keyword "attr") "val")) "<tag attr=\"val\"/>"))
    (assert (= (mnml (tag :attr "val" "")) "<tag attr=\"val\"></tag>"))
    (assert (= (mnml (tag :attr "val" "content")) "<tag attr=\"val\">content</tag>"))
    (assert (= (mnml (tag :ATTR "val")) "<tag attr=\"val\"/>"))
    (assert (= (mnml (tag ~(keyword (.upper "attr")) "val")) "<tag attr=\"val\"/>"))
    (assert (= (mnml (tag :attr "VAL")) "<tag attr=\"VAL\"/>"))
    (assert (= (mnml (tag :attr ~(.upper "val"))) "<tag attr=\"VAL\"/>"))
    (assert (= (mnml (tag (sub))) "<tag><sub/></tag>"))
    (assert (= (mnml (tag ~@(list-comp `(sub ~(str item)) [item [1 2 3]])))
               "<tag><sub>1</sub><sub>2</sub><sub>3</sub></tag>"))
    
    (defvar x "variable")
    (assert (= (mnml (tag ~x)) "<tag>variable</tag>"))
    
    (deffun f (fn [x] x))
    (assert (= (mnml (tag ~(f "function"))) "<tag>function</tag>"))
    
    (with [f (open "test.hy" "w")] (f.write "(tag)"))
    (assert (= (mnml ~@(include "test.hy")) "<tag/>"))

The `MIT <http://choosealicense.com/licenses/mit/>`__ License
-------------------------------------------------------------

Copyright (c) 2017 Marko Manninen
