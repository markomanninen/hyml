
HyML MiNiMaL
============

Minimal markup language generator in Hy
---------------------------------------

`HyML <https://github.com/markomanninen/hyml>`__ (acronym for Hy Markup
Language) is a set of macros to generate XML, XHTML, and HTML code in
`Hy <http://hy.readthedocs.io/en/latest/>`__.

HyML MiNiMaL (``ml``) macro is departed from the more extensive document
and validation oriented "full" version of HyML.

HyML MiNiMaL is meant to be used as a minimal codebase to generate XML 
(Extensible Markup Language) with the next principal features:

1. closely resembling syntax with XML
2. ability to embed Hy / Python program code within markup
3. processing lists and external templates
4. using custom variables and functions

You can use HyML MiNiMaL:

-  for static XML / XHTML / HTML content and file generation
-  to render html code for the Jupyter Notebook, Sphinx docs, etc.
-  to attach it to a server for dynamic html output generation 
   (`sHyte 0.2 <https://github.com/markomanninen/shyte>`__)
-  for practice and study
   `DSL <https://en.wikipedia.org/wiki/Domain-specific_language>`__ and
   macro (Lisp) programming
-  challenge your imagination

To compare with the full HyML XML / HTML macros, MiNiMaL means that there 
is no tag name validation and no tag and attribute minimize techniques
utilized. If you need them, you should see 
`full HyML <http://hyml.readthedocs.io/en/latest/#>`__ documentation.

.. note::  HyML refers to XML, althought "Markup Language" -term itself is more 
           `generic <https://en.wikipedia.org/wiki/Markup_language>`__ term.


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
templates nor Jupyter Notebook files.

There are no other dependencies except Hy language upon Python of cource. 
If Hy does not exist on your computer, it will be installed (or updated to 
the version 0.12.1 or greater) at the same time.

At the moment, the latest version of HyML is 0.2.6 (pre-release).


Import
~~~~~~

Then import MiNiMaL macros:

.. code-block:: hylang

    (require (hyml.minimal (*)))

This will load the next macros for usage:

- main markup macro: ``ml``
- ``defvar`` and ``deffun`` macros for custom variable and function setter
- ``include`` macro for using templates
- ``list-comp*`` list comprehension helper macro

Optionally ``ml>`` render macro will be loaded, if code is executed on Jupyter 
Notebook / IPython environment with the ``display.HTML`` function available.

If you intend to use xml code ``indent`` function, you should also import it:

.. code-block:: hylang

    (import (hyml.minimal (indent)))

With indent function you can make printed XML output prettier and more readable.


Run
~~~

Finally, run the simple example:

.. code-block:: hylang

    (ml (tag :attr "value" (sub "Content")))

That should output:

.. code-block:: xml

    <tag attr="value"><sub>Content</sub></tag>


Tests
~~~~~

To run basic tests, you can use Jupyter Notebook `document <http://nbviewer.jupyter.org/github/markomanninen/hyml/blob/master/HyML%20-%20Minimal.ipynb#Test-main-features>`__ for now.


Jupyter Notebook
~~~~~~~~~~~~~~~~

If you want to play with the provided HyML Notebook document, you should 
download the whole `HyML
repository <https://github.com/markomanninen/hyml/archive/master.zip>`__
(or clone it with
``$ git clone https://github.com/markomanninen/hyml.git``) to your
computer. It contains all necessary templates to get everything running
as presented in the HyML MiNiMaL Notebook `document <http://nbviewer.jupyter.org/github/markomanninen/hyml/blob/master/HyML%20-%20Minimal.ipynb>`__.


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

    ; macro -macro to be used inside templates
    (defmacro macro [name params &rest body]
      `(do
        (defmacro ~name ~params
          `(quote ~~@body)) None))


Features
--------


Basic syntax
~~~~~~~~~~~~

MiNiMaL macro syntax is simple. It practically follows the rules of 
`Hy syntax <http://docs.hylang.org/en/latest/language/api.html>`__. 

MiNiMaL macro expression is made of four components:

1. tag name
2. tag attribute-value pair(s)
3. tag text content
4. sub expression(s)

Syntax of the expression consists of:

* parentheses to define hierarchical (nested) structure of the document
* all opened parentheses ``(`` must have closing parentheses pair ``)``
* the first item of the expression is the tag name
* next items in the expression are either:

  * tag attribute-value pairs
  * tag content wrapped with double quotes
  * sub tag expression
  * nothing at all

* between keywords, keyword values, and content there must a whitespace
  separator OR expression components must be wrapped with double quotes
  when suitable
* whitespace is not needed when a new expression starts or ends
  (opening and closing parentheses)

There is no limit on nested levels. There is no limit on how many
attribute-value pairs you want to use. Also it doesn't matter in what
order you define tag content and keywords, althougt it might be easier
to read for others, if keywords are introduced first and then the
content. However, all keywords are rendered in the same order they have
been presented in the markup. Also content and sub nodes (expressions) 
are rendered similarly in the given order.

Main differences to XML syntax are:

-  instead of ``<`` and ``>`` wrappers, parentheses ``(`` and ``)`` 
   are used
-  there can't be a separate end tag
-  given expression does not need to have a single root node
-  see other possible differences comparing HyML to
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
MiNiMaL macro they may look they work other way around.

Unquote (``~``) and unquote-splice (``~@``) gets you back to the Hy code
evaluation mode. And quasiquote (`````) sets you back to MiNiMaL macro
mode. This is natural when you think that MiNiMaL macro is a quoted
code in the first place. So if you want to evaluate Hy code inside it,
you need to do it inside unquote.


Simple example
~~~~~~~~~~~~~~

The simple example utilizing above features and all four components is:

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


Process components with unquote syntax (``~``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Any component (tag name, tag attribute / value, and tag content) can be 
generated instead of hardcoded to the expression.


Tag name
^^^^^^^^

You can generate a tag name with Hy code by using ``~`` symbol:

.. code-block:: hylang

    (ml (~(+ "t" "a" "g"))) ; output: <tag/>

This is useful, if tag names collide with Hy internal symbols and
datatypes. For example, the symbol ``J`` is reserved for complex number
type. Instead of writing: ``(ml (J))`` which produces ``<1j/>``, you
should use: ``(ml (~"J"))`` or ``(ml ("J"))``.


Attribute name and value
^^^^^^^^^^^^^^^^^^^^^^^^

You can generate an attribute name or a value with Hy by using ``~`` symbol.
Generated attribute name must be a keyword type however:

.. code-block:: hylang

    (ml (tag ~(keyword (.join "" ['a 't 't 'r])) "value")) ; output: <tag attr="value"/>

And same for value:

.. code-block:: hylang

    (ml (tag :attr ~(+ 'v 'a 'l 'u 'e))) ; output: <tag attr="value"/>


Content
^^^^^^^

You can generate content with Hy by using ``~`` symbol:

.. code-block:: hylang

    (ml (tag ~(.upper "content"))) ; output: <tag>CONTENT</tag>


Using custom variables and functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can define custom variables and functions for the MiNiMaL macro.
Variables and functions are stored on the common registry and available
on the macro expansion. You can access predefined symbols when quoting
``~`` the expression.

.. code-block:: hylang

    ; define variables with defvar macro
    (defvar firstname "Dennis"
            lastname "McDonald")

    ; define functions with deffun macro
    (deffun wholename (fn [x y] (+ y ", " x)))

    ; use variables and functions with unquote / unquote splice
    (ml (tag ~(wholename firstname lastname)))

|Output:|

.. code-block:: xml

    <tag>McDonald, Dennis</tag>


Process lists with unquote splice syntax (``~@``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

|Output:|

.. code-block:: xml

    <tag><sub>0</sub><sub>1</sub><sub>2</sub><sub>3</sub><sub>4</sub></tag>


Using templates
~~~~~~~~~~~~~~~

One useful extension of the HyML MiNiMaL is that you can define 
code on external templates and ``include`` them for generation.

Let us first show the template content existing in the external file:

.. code-block:: hylang

    (with [f (open "note.hy")] (print (f.read)))

.. code-block:: hylang

    (note :src "https://www.w3schools.com/xml/note.xml"
      (to ~to)
      (from ~from)
      (heading ~heading)
      (body ~body))


Then we will define variables to be used inside the template:

.. code-block:: hylang

    (defvar to "Tove"
            from "Jani"
            heading "Reminder"
            body "Don't forget me this weekend!")

And finally use ``include`` macro to render the template:

.. code-block:: hylang

    (ml ~@(include "note.hy"))

|Output:|

.. code-block:: xml

    <note src="https://www.w3schools.com/xml/note.xml">
      <to>Tove</to>
      <from>Jani</from>
      <heading>Reminder</heading>
      <body>Don't forget me this weekend!</body>
    </note>

.. Danger:: In HyML, but with templates especially, you must realize that 
            inside macro there is a full access to all Hy and Python modules
            including file systems access and so on. This might raise up some 
            security concerns that you should be aware of.


Templates extra
~~~~~~~~~~~~~~~

On HyML package there is also the ``render-template`` function and the
``extend-template`` macro available via ``HyML.template`` module.

``HyML.template`` is especially useful when embedding ``HyML MiNiMaL``
to webserver, `Flask <http://flask.pocoo.org/>`__ for example. Here just
the basic use case is shown, more examples you can find from `sHyte 0.2
HyML Edition <https://github.com/markomanninen/shyte>`__ codebase.

In practice, ``render-template`` function is a shortcut to call
``parse-mnml`` with parameters and ``include`` in sequence. The first
argument in ``render-template`` is the template name, and the rest of
the arguments are dictionaries to be used on the template. So this is
also an alternative way of using (bypassing the usage of) ``defvar`` and
``deffun`` macros.

.. code-block:: hylang

    ; extend-template macro
    (require [hyml.template [*]])
    ; render-template function
    (import [hyml.template [*]])
    ; prepare template variables and functions
    (setv template-variables-and-functions 
         {"var" "Variable 1" "func" (fn[]"Function 1")})
    ; render template
    (render-template "render.hyml" template-variables-and-functions)

|Output:|

.. code-block:: xml

    <root><var>Variable 1</var><func>Function 1</func></root>


On template engines it is a common practice to extend sub template with
main template. Say we have a layout template, that is used as a wapper
for many other templates. We can refactor layout xml code to another
file and keep the changing sub content on other files.

In ``HyML MiNiMaL``, ``extend-template`` macro is used for that.

Lets show an example again. First we have the content of the
``layout.hyml`` template file:

.. code-block:: hylang

    (with [f (open "templates/layout.hyml")] (print (f.read)))


.. code-block:: hylang

    (html
      (head (title ~title))
      (body ~body))
    

And the content of the ``extend.hyml`` sub template file:

.. code-block:: hylang

    (with [f (open "templates/extend.hyml")] (print (f.read)))


.. code-block:: hylang

    ~(extend-template "layout.hyml" 
        {"body" `(p "Page content")})
    

We have decided to set the ``title`` as a "global" variable but define
the ``body`` on the sub template. The render process goes like this:

.. code-block:: hylang

    (setv locvar {"title" "Page title"})
    (render-template "extend.hyml" locvar)

|Output:|

.. code-block:: xml

    <html><head><title>Page title</title></head><body><p>Page content</p></body></html>

Note that extension name ``.hyml`` was used here even though it doesn't
really matter what file extension is used.

At first it may look overly complicated and verbose to handle templates
this way. Major advantage is found when processing multiple nested
templates. Difference to simply including template files
``~@(include "templates/template.hy")`` is that on ``include`` you pass
variables (could be evaluated ``HyML`` code) to template, but on
``extend-template`` you pass unevaluated ``HyML`` code to another
template. This will add one more dynamic level on using ``HyML MiNiMaL``
for XML content generation.


**Template directory**

Default template directory is set to ``"template/"``. You can change
directory by changing ``template-dir`` variable in the ``HyML.template``
module:

.. code:: hylang

    (import hyml.template)
    (def hyml.template.template-dir "templates-extra/")


**Macro -macro**

One more related feature to templates is a ``macro`` -macro that can be
used inside template files to factorize code for local purposes. If our
template file would look like this:

.. code:: hylang

    ~(macro custom [attr]
      `(p :class ~attr))

    ~(custom ~class)

Then rendering it, would yield:

.. code-block:: hylang

    (render-template "macro.hyml" {"class" "main"}) ; output: <p class="main"/>



Directly calling the ``parse-mnml`` function
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You are not forced to use ``ml`` macro to generate XML. You can pass
quoted code directly to ``parse-mnml`` function. This can actually be a
good idea, for example if you want to generate tags based on a
dictionary. First lets see the simple example:

.. code-block:: hylang

    (parse-mnml '(tag)) ; output: <tag/>

Then let us make it a bit more complicated:

.. code-block:: hylang

    ; define contacts dictionary
    (defvar contacts [
        {:firstname "Eric"
         :lastname "Johnson"
         :telephone "+1-202-555-0170"}
        {:firstname "Mary"
         :lastname "Johnson"
         :telephone "+1-202-555-0185"}])
    (ml
      ; root contacts node
      (contacs
        ~@(do
          ; import parse-mnml function at the highest level of unquoted code
          (import (hyml.minimal (parse-mnml)))
          ; contact node
          (list-comp `(contact
            ; last contact detail node
            ~@(list-comp (parse-mnml `(~tag ~val))
                [[tag val] (.items contact)]))
          [contact contacts]))))

|Output:|

.. code-block:: xml

    <contacs>
      <contact>
        <firstname>Eric</firstname>
        <lastname>Johnson</lastname>
        <telephone>+1-202-555-0170</telephone>
      </contact>
      <contact>
        <firstname>Mary</firstname>
        <lastname>Johnson</lastname>
        <telephone>+1-202-555-0185</telephone>
      </contact>
    </contacs>


With ``parse-mnml`` function it is also possible to pass an optional dictionary 
to be used for custom variables and functions on evaluation process. This is NOT 
possible with ``ml`` macro.

.. code-block:: hylang

    (parse-mnml '(tag :attr ~val) {"val" "val"}) ; output: <tag attr="val"/>

With ``template`` macro you can actually see a very similar behaviour. In cases 
where variables can be hard coded, you might want to use this option:

.. code-block:: hylang

    (template {"val" "val"} `(tag :attr ~val)) ; output: <tag attr="val"/>

It doesn't really matter in which order you pass expression and dictionary to 
the ``template`` macro. It is also ok to leave dictionary out if expression does 
not contain any variables. For ``template`` macro, expression needs to be 
quasiquoted, if it contains ``HyML`` code.


Wrapping up everything
----------------------

So all features of the MiNiMaL macro has now been introduced. Let us
wrap everything and create XHTML document that occupies the most of the
feature set. Additional comments will be given between the code lines.

.. code-block:: hylang
    
    ; define variables
    (defvar topic "How do you make XHTML 1.0 Transitional document with HyML?"
            tags ['html 'xhtml 'hyml]
            postedBy "Hege Refsnes"
            contactEmail "hege.refsnes@example.com")
    
    ; define function
    (deffun valid (fn []
      (ml (p (a :href "http://validator.w3.org/check?uri=referer" 
             (img :src "http://www.w3.org/Icons/valid-xhtml10" 
                  :alt "Valid XHTML 1.0 Transitional" 
                  :height "31" :width "88"))))))
    
    ; let just arficially create a body for the post
    ; and save it to the external template file
    (with [f (open "body.hy" "w")]
      (f.write "(div :class \"body\"
        \"I've been wondering if it is possible to create XHTML 1.0 Transitional 
          document by using a brand new HyML?\")"))
    
    ; start up the MiNiMaL macro
    (ml
      ; xml document declaration
      "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
      "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Transitional//EN\" 
      \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\">"
      ; create html tag with xml namespace and language attributes
      (html :xmlns "http://www.w3.org/1999/xhtml" :lang "en"
        (head
          ; title of the page
          (title "Conforming XHTML 1.0 Transitional Template")
          (meta :http-equiv "Content-Type" :content "text/html; charset=utf-8"))
        (body
          ; wrap everything inside the post div
          (div :class "post"
            ; first is the header of the post
            (div :class "header" ~topic)
            ; then body of the post from external template file
            ~@(include "body.hy")
            ; then the tags in spans
            (div :class "tags"
              ~@(list-comp `(span ~tag) [tag tags]))
            ; finally the footer
            (div :id "footer"
              (p "Posted by: " ~postedBy)
              (p "Email: " 
                (a :href ~(+ "mailto:" contactEmail) ~contactEmail) ".")))
           ; proceed valid stamp by a defined function
           ~(valid))))

|Output:|

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE html
      PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN'
      'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'>
    <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <title>Conforming XHTML 1.0 Transitional Template</title>
        <meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
      </head>
      <body>
        <div class="post">
          <div class="header">How do you make XHTML 1.0 Transitional document with HyML?</div>
          <div class="body">I've been wondering if it is possible to create XHTML 1.0 Transitional 
          document by using a brand new HyML?</div>
          <div class="tags">
            <span>html</span>
            <span>xhtml</span>
            <span>hyml</span>
          </div>
          <div id="footer">
            <p>Posted by: Hege Refsnes</p>
            <p>
              Email: 
              <a href="mailto:hege.refsnes@example.com">hege.refsnes@example.com</a>
              .
            </p>
          </div>
        </div>
        <p>
          <a href="http://validator.w3.org/check?uri=referer">
            <img alt="Valid XHTML 1.0 Transitional" height="31" src="http://www.w3.org/Icons/valid-xhtml10" width="88"/>
          </a>
        </p>
      </body>
    </html>


Unintended features
-------------------

These are not deliberately implemented features, but a consequence of the
HyML MiNiMaL implementation and how Hy works.


Nested MiNiMaL macros
~~~~~~~~~~~~~~~~~~~~~

It is possible to call MiNiMaL macro again inside unquoted code:

.. code-block:: hylang

    (ml (tag ~(+ "Generator inside: " (ml (sub "content")))))

|Output:|

.. code-block:: xml

    <tag>Generator inside: <sub>content</sub></tag>


Unrecognized symbols
~~~~~~~~~~~~~~~~~~~~

Unrecognized symbols (that is they are not specified as literals with double quotas and have no whitespace) are regarded as string literals, unless they are unquoted and they are not colliding with internal Hy symbols.

.. code-block:: hylang

    (ml (tag :alfred J. Kwak))

|Output:|

.. code-block:: xml

    <tag alfred="J.">Kwak</tag>


Quote and quasiquote
~~~~~~~~~~~~~~~~~~~~

Tag names, attribute values, and tag content can be also single
pre-quoted strings. It doesn't matter because in the final process of
evaluating the component, a string representation of the symbol is
retrieved.

.. code-block:: hylang

    [(ml ('tag)) (ml (`tag)) (ml (tag)) (ml ("tag"))]

|Output:|

.. parsed-literal::

    ['<tag/>', '<tag/>', '<tag/>', '<tag/>']


With keywords, however, single pre-queted strings will get parsed as a
content.

.. code-block:: hylang

    [(ml (tag ':attr)) (ml (tag `:attr))]

|Output:|

.. parsed-literal::

    ['<tag>attr</tag>', '<tag>attr</tag>']


Keyword specialties
~~~~~~~~~~~~~~~~~~~

Also, if keyword marker is followed by a string literal, keyword will be
empty, thus not a correctly wormed keyword value pair.

.. code-block:: hylang

    (ml (tag :"attr")) ; output: <tag ="attr"/>

So only working version of keyword notation is ``:{symbol}`` or unquoted
``~(keyword {expression})``. 

.. note::  Keywords without value are interpreted as a keyword having the
           same value as the keyword name (called 
           `boolean attributes <http://www.w3.org/TR/html5/infrastructure.html#boolean-attributes>`__
           in HTML).

.. code-block:: hylang

    [(ml (tag :disabled)) (ml (tag ~(keyword "disabled"))) (ml (tag :disabled "disabled"))]

|Output:|

.. parsed-literal::

    ['<tag disabled="disabled"/>', '<tag disabled="disabled"/>', '<tag disabled="disabled"/>']


If you wish to define multiple boolean attributes together with content,
you can collect them at the end of the expression.

.. note::   In XML boolean attributes cannot be minimized similar to HTML. 
            Attributes always needs to have a value pair.

.. code-block:: hylang

    (ml (tag "Content" :disabled :enabled))

|Output:|

.. code-block:: xml

    <tag disabled="disabled" enabled="enabled">Content</tag>


One more thing with keywords is that if the same keyword value pair is
given multiple times, it will show up in the mark up in the same order,
as multiple. Depending on the markup parser, the last attribute might be
valuated OR parser might give an error, because by XML Standard attibute
names should be unique and not repeated under the same element.

.. code-block:: hylang

    (ml (tag :attr :attr "attr2")) ; output: <tag attr="attr" attr="attr2"/>


Test main features
------------------

Assert tests for all main features presented above. There should be no 
output after running these. If there is, then *Houston, we have a problem!*

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
    ; boolean attributes
    (assert (= [(ml (tag :attr "attr")) (ml (tag :attr)) (ml (tag ~(keyword "attr")))]
               ["<tag attr=\"attr\"/>" "<tag attr=\"attr\"/>" "<tag attr=\"attr\"/>"]))
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

.. |Output:| replace:: ⎑ *output*
