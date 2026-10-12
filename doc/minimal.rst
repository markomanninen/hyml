
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
HyML needs Python 3.9 or newer and Hy 1.0 or newer. If Hy does not exist
on your computer, it will be installed (or updated to the version 1.0 or
greater) at the same time.

At the moment, the latest version of HyML is 1.0.0. It has been tested
with Hy 1.0.0 and Hy 1.3.1 on Python 3.9 - 3.14. Versions before 1.0 were
written for Hy 0.12 / 0.13 and do not run on Hy 1.x.


Import
~~~~~~

Then import MiNiMaL macros:

.. code-block:: hylang

    (require hyml.minimal *)

This will load the next macros for usage:

- main markup macro: ``ml``
- ``defvar`` and ``deffun`` macros for custom variable and function setter
- ``include`` macro for using templates
- ``macro`` macro for using inside templates
- ``list-comp*`` list comprehension helper macro (and ``list-comp`` in
  the old Hy 0.13 argument order)
- ``ml>`` render macro for Jupyter Notebook / IPython. ``IPython`` is
  imported only when ``ml>`` is used, so it is not needed otherwise.

If you intend to use xml code ``indent`` function, you should also import it:

.. code-block:: hylang

    (import hyml.minimal [indent])

With indent function you can make printed XML output prettier and more readable.

For babel / gettext localization there is also a shorthand reader macro
``#i``. Reader macros are required separately:

.. code-block:: hylang

    (require hyml.minimal :readers [i])

    #i"Hello" ; same as (_ "Hello")


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

Tests are written for `pytest <https://pytest.org/>`__. Clone the repository,
install HyML with the test extras, and run ``pytest`` in the repository root:

.. code-block:: bash

    $ pip install -e ".[test]"
    $ pytest

See `HyML tests <http://hyml.readthedocs.io/en/latest/tests.html>`__ for more.


Jupyter Notebook
~~~~~~~~~~~~~~~~

If you want to play with the provided HyML Notebook document, you should
download the whole `HyML
repository <https://github.com/markomanninen/hyml/archive/master.zip>`__
(or clone it with
``$ git clone https://github.com/markomanninen/hyml.git``) to your
computer. It contains all necessary templates to get everything running
as presented in the HyML MiNiMaL Notebook `document <http://nbviewer.jupyter.org/github/markomanninen/hyml/blob/master/HyML%20-%20Minimal.ipynb>`__.

.. note:: The Notebook document runs on the standard Python 3 kernel
          with the ``hyml.ipython`` extension: ``%load_ext hyml.ipython``
          and then ``%%hy`` at the start of the Hy cells.


HyML MiNiMaL codebase
----------------------

Because codebase for HyML MiNiMaL implementation is roughly 80 lines
only (without comments), it is provided here with structural comments and 
linebreaks for the inspection. More detailed comments are available in the
`minimal.hy <https://github.com/markomanninen/hyml/blob/master/hyml/minimal.hy>`__
source file. A few small helpers shared with the full HyML (``catch-tag``,
``namespace``, ``eval-in`` and so on) are in
`core.hy <https://github.com/markomanninen/hyml/blob/master/hyml/core.hy>`__,
and ``defvar`` / ``deffun`` are in
`variables.hy <https://github.com/markomanninen/hyml/blob/master/hyml/variables.hy>`__,
which is appended to the end of the listing.

.. code-block:: hylang
    :linenos:

    ; global registry for variables and functions
    (require hyml.variables [defvar deffun])
    (import hyml.core [variables-and-functions HyMLError])
    ; some helpers
    (require hyml.helpers [println ml> list-comp list-comp*])
    (import hyml.helpers [indent])

    ; eval and compile variables, constants and functions for ml, defvar, deffun, and include macros
    (eval-and-compile
      (import hyml.core [keyword? coll? head-name ->str eval-in
                         escape-attribute unquoted]
              hyml.core :as core)
      ; internal constants
      (setv **unquote** "unquote"
            **splice** "unquote-splice"
            **unquote-splice** #(**unquote** **splice**)
            **quote** "quote"
            **quasi** "quasiquote"
            **quasi-quote** #(**quote** **quasi**))
      ; unquoted code sees the macros of this module (list-comp*, include, ...)
      (defn evaluate [code vars-and-funcs]
        (eval-in code "hyml.minimal" vars-and-funcs))
      ; detach keywords and content from code expression
      (defn get-content-attributes [code [vars-and-funcs None]]
        (setv content [] attributes [] kwd None)
        (for [item code]
          ; should we evaluate keyword
          (setv head (head-name item))
          (cond (= head **unquote**)
                (setv item (unquoted (evaluate (get item 1) vars-and-funcs)))
                ; single pre-quoted symbols will get accepted
                ; this is practically to make attribute value and content part
                ; coherent with create-tag functionality. without this
                ; quotation symbols would be interpreted as tag names!
                (in head **quasi-quote**)
                (setv item (->str (hy.eval item))))
          (if (keyword? item)
              (do
                ; a keyword right after a keyword is a boolean attribute that
                ; has same value than the name of the attribute
                (when (is-not kwd None)
                  (.append attributes #(kwd (->str kwd))))
                (setv kwd item))
              (do
                ; keyword was not set, so item must be a content
                ; otherwise it is attribute
                (if (is kwd None)
                    (.append content (parse-mnml item vars-and-funcs))
                    (.append attributes #(kwd (parse-mnml item vars-and-funcs))))
                (setv kwd None))))
        ; trailing keyword is a boolean attribute too
        (when (is-not kwd None)
          (.append attributes #(kwd (->str kwd))))
        #(content attributes))
      ; recursively parse expression. take optional variables and functions
      ; dictionary for eval functionality. note that ml macro does NOT
      ; support this, only parse-mnml direct function call
      (defn parse-mnml [code [vars-and-funcs None]]
        (if (coll? code)
            (do (setv tag (catch-tag (if code (get code 0) None) vars-and-funcs))
                (cond
                  ; unquoted value may be markup too, so parse it again
                  (= tag **unquote**)
                  (parse-mnml (unquoted (evaluate (get code 1) vars-and-funcs)) vars-and-funcs)
                  ; process the list of code
                  (= tag **splice**)
                  (.join "" (gfor item (evaluate (get code 1) vars-and-funcs)
                              (parse-mnml item vars-and-funcs)))
                  ; normal tag creation
                  True
                  (do (setv [content attributes] (get-content-attributes (cut code 1 None) vars-and-funcs))
                      ; start tag with attributes
                      ; if there is no content, then we can use short tags
                      (+ (tag-start tag attributes (not content))
                         ; if there is no content, we don't need end tag
                         (if content
                             (+ (.join "" content) "</" tag ">")
                             "")))))
            ; returned value is always a string
            (->str code)))
      ; detach tag from expression
      (defn catch-tag [code [vars-and-funcs None]]
        (core.catch-tag code (fn [c] (evaluate c vars-and-funcs))))
      ; concat attributes
      (defn tag-attributes [attr]
        (if attr
            (+ " " (.join " " (gfor [kwd value] attr
                                (% "%s=\"%s\"" #((->str kwd) (escape-attribute value))))))
            ""))
      ; create start tag
      (defn tag-start [tag-name attr short]
        (+ "<" tag-name (tag-attributes attr) (if short "/>" ">"))))

    ; include functionality for template engine
    (defmacro include [template]
      ; content of the file must be wrapped with expression parentheses ()
      ; quasiquoted (`) and finally unquote-spliced (~@) so that
      ; final evaluation is done in the main parse-mnml loop
      `(with [f (open ~template :encoding "utf-8")]
         (list (hy.read-many (+ "~@`(" (.read f) "\n)")))))

    ; main MiNiMaL macro to be used. passes code to parse-mnml
    (defmacro ml [#* code]
      ; with map multiple expressions, not only nested ones, can be processed
      (.join "" (gfor item code (parse-mnml item))))

    ; macro is a wrapper around defmacro and it is used to return
    ; quoted body so that unquotes can be evaluated later on the process
    ; this is used mostly with render-template and inside template files
    (defmacro macro [name params #* body]
      `(do
        (defmacro ~name ~params
          `(quote ~~@body))
        ; return None to prevent printing created anonymous macro/function
        None))

    ; bhybel reader macro shortcut for babel/gettext localization and
    ; internalization: #i"message" -> (_ "message")
    ; enable with (require hyml.minimal :readers [i])
    (defreader i
      `(_ ~(.parse-one-form &reader)))

    ; hyml/variables.hy: global registry handlers
    ; for example: (defvar x 1 y 2 z 3)
    ; later values may refer to earlier ones: (defvar a 1 b (+ a 1))
    (defmacro defvar [#* args]
      (when (% (len args) 2)
        (raise (HyMLError "defvar needs an even number of arguments")))
      (for [i (range 0 (len args) 2)]
        (setv (get variables-and-functions (hy.mangle (get args i)))
              (hy.eval (get args (+ i 1)) (namespace) :module "hyml.variables")))
      None)

    ; for example: (deffun wholename (fn [x y] (+ y ", " x)))
    (defmacro deffun [name func]
      (setv (get variables-and-functions (hy.mangle name))
            (hy.eval func (namespace) :module "hyml.variables"))
      None)


Features
--------


Basic syntax
~~~~~~~~~~~~

MiNiMaL macro syntax is simple. It practically follows the rules of 
`Hy syntax <https://hylang.org/hy/doc/v1.0.0/syntax>`__. 

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
  when suitable. A keyword can be followed directly by a string, like
  ``:attr"val"``, but a symbol can't: ``(tag"content")`` is a reader
  error in Hy 1.x, because ``tag"`` would be read as a string prefix
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
notation <https://hylang.org/hy/doc/v1.0.0/api#quasiquote>`__,
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

Plain symbols are never evaluated as tag names, so they can't collide
with Hy internal symbols and datatypes. For example ``(ml (J))``,
``(ml (~"J"))``, and ``(ml ("J"))`` all produce ``<J/>``, and
``(ml (map (input) (object)))`` gives ``<map><input/><object/></map>``.
Hyphens are kept too: ``(ml (my-tag))`` gives ``<my-tag/>``.

.. note::  In Hy 0.13 tag symbols were evaluated first, so ``(ml (J))``
           produced ``<1j/>``. This is no longer the case.


Attribute name and value
^^^^^^^^^^^^^^^^^^^^^^^^

You can generate an attribute name or a value with Hy by using ``~`` symbol.
Generated attribute name must be a keyword type however:

.. code-block:: hylang

    (ml (tag ~(hy.models.Keyword (.join "" ['a 't 't 'r])) "value")) ; output: <tag attr="value"/>

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

``defvar`` evaluates the values when the variables are defined, so a
later value can refer to an earlier one: ``(defvar n 1 m (+ n 1))``. Names
with hyphens work as usual, ``~first-name`` finds a variable defined as
``first-name``. The registry is shared with the full HyML ``xml``,
``xhtml``, ``xhtml5``, ``html4``, and ``html5`` macros.

.. note::  Markup is generated when the code is compiled, so variables set
           with ``setv`` are not visible to unquoted code in the ``ml``
           macro. Use ``defvar`` and ``deffun`` for that. Also a function
           registered with ``deffun`` is compiled inside HyML, so it should
           return quasiquoted HyML code like ``(fn [] `(p "text"))``
           rather than call the ``ml`` macro itself.


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
    (ml (tag ~@(lfor item (range 5) `(sub ~(str item)))))

|Output:|

.. code-block:: xml

    <tag><sub>0</sub><sub>1</sub><sub>2</sub><sub>3</sub><sub>4</sub></tag>

The same can be done with ``list-comp*`` macro, which takes the list
first and an optional condition last, or with ``list-comp`` macro, which
uses the Hy 0.13 argument order:

.. code-block:: hylang

    (ml (tag ~@(list-comp* [item (range 5)] `(sub ~(str item)) (% item 2))))
    ; output: <tag><sub>1</sub><sub>3</sub></tag>
    (ml (tag ~@(list-comp `(sub ~(str item)) [item (range 5)])))
    ; output: <tag><sub>0</sub><sub>1</sub><sub>2</sub><sub>3</sub><sub>4</sub></tag>


Using templates
~~~~~~~~~~~~~~~

One useful extension of the HyML MiNiMaL is that you can define 
code on external templates and ``include`` them for generation.

Let us first show the template content existing in the external file:

.. code-block:: hylang

    (with [f (open "templates/note.hy")] (print (f.read)))

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

    (ml ~@(include "templates/note.hy"))

|Output:|

.. code-block:: xml

    <note src="https://www.w3schools.com/xml/note.xml"><to>Tove</to><from>Jani</from><heading>Reminder</heading><body>Don't forget me this weekend!</body></note>

To make it more readable, use the ``indent`` function:

.. code-block:: hylang

    (print (indent (ml ~@(include "templates/note.hy"))))

|Output:|

.. code-block:: xml

    <note src="https://www.w3schools.com/xml/note.xml">
        <to>Tove</to>
        <from>Jani</from>
        <heading>Reminder</heading>
        <body>Don't forget me this weekend!</body>
    </note>

``indent`` needs well-formed xml with a single root node. Otherwise it
raises ``HyMLError``.

.. Danger:: In HyML, but with templates especially, you must realize that 
            inside macro there is a full access to all Hy and Python modules
            including file systems access and so on. This might raise up some 
            security concerns that you should be aware of.


Templates extra
~~~~~~~~~~~~~~~

On HyML package there is also the ``render-template`` function and the
``extend-template`` macro available via ``hyml.template`` module.

``hyml.template`` is especially useful when embedding ``HyML MiNiMaL``
to webserver, `Flask <http://flask.pocoo.org/>`__ for example. Here just
the basic use case is shown, more examples you can find from `sHyte 0.2
HyML Edition <https://github.com/markomanninen/shyte>`__ codebase.

In practice, ``render-template`` function is a shortcut to call
``parse-mnml`` with parameters and ``include`` in sequence. The first
argument in ``render-template`` is the template name, and the rest of
the arguments are dictionaries to be used on the template. So this is
also an alternative way of using (bypassing the usage of) ``defvar`` and
``deffun`` macros. Explicitly passed dictionaries override the variables
of the ``defvar`` / ``deffun`` registry and the globals of the
``hyml.template`` module, and later dictionaries override earlier ones.

.. code-block:: hylang

    ; extend-template macro
    (require hyml.template *)
    ; render-template function
    (import hyml.template *)
    ; prepare template variables and functions
    (setv template-variables-and-functions
         {"var" "Variable 1" "func" (fn [] "Function 1")})
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

Default template directory is set to ``"templates/"``. You can change
directory by changing ``template-dir`` variable in the ``hyml.template``
module:

.. code:: hylang

    (import hyml.template)
    (setv hyml.template.template-dir "templates-extra/")


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
      (contacts
        ~@(do
          ; import parse-mnml function at the highest level of unquoted code
          (import hyml.minimal [parse-mnml])
          ; contact node
          (lfor contact contacts
            `(contact
              ; last contact detail node
              ~@(lfor [tag val] (.items contact)
                  (parse-mnml `(~tag ~val))))))))

|Output:|

.. code-block:: xml

    <contacts><contact><firstname>Eric</firstname><lastname>Johnson</lastname><telephone>+1-202-555-0170</telephone></contact><contact><firstname>Mary</firstname><lastname>Johnson</lastname><telephone>+1-202-555-0185</telephone></contact></contacts>

Or with ``indent``:

.. code-block:: xml

    <contacts>
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
    </contacts>


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
quasiquoted, if it contains ``HyML`` code. Global variables of the calling
module are available in the expression too:

.. code-block:: hylang

    (setv greeting "hello")
    (template `(p ~greeting)) ; output: <p>hello</p>


Wrapping up everything
----------------------

So all features of the MiNiMaL macro has now been introduced. Let us
wrap everything and create XHTML document that occupies the most of the
feature set. Additional comments will be given between the code lines.

First, let us just artificially create a body for the post and save it
to the external template file. Do this in a separate REPL / Notebook
cell before the rest, because the ``ml`` macro reads included files
already when the code is compiled:

.. code-block:: hylang

    (with [f (open "body.hy" "w")]
      (f.write "(div :class \"body\"
        \"I've been wondering if it is possible to create XHTML 1.0 Transitional
          document by using a brand new HyML?\")"))

Then the document itself:

.. code-block:: hylang

    ; define variables
    (defvar topic "How do you make XHTML 1.0 Transitional document with HyML?"
            tags ['html 'xhtml 'hyml]
            postedBy "Hege Refsnes"
            contactEmail "hege.refsnes@example.com")

    ; define function. it returns quasiquoted HyML code
    ; that the MiNiMaL macro will render
    (deffun valid (fn []
      `(p (a :href "http://validator.w3.org/check?uri=referer"
             (img :src "http://www.w3.org/Icons/valid-xhtml10"
                  :alt "Valid XHTML 1.0 Transitional"
                  :height "31" :width "88")))))

    ; start up the MiNiMaL macro, and indent the result for printing
    (print (indent (ml
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
              ~@(lfor tag tags `(span ~tag)))
            ; finally the footer
            (div :id "footer"
              (p "Posted by: " ~postedBy)
              (p "Email: "
                (a :href ~(+ "mailto:" contactEmail) ~contactEmail) ".")))
           ; proceed valid stamp by a defined function
           ~(valid))))))

|Output:|

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE html
      PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN'
      'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'>
    <html xmlns="http://www.w3.org/1999/xhtml" lang="en">
        <head>
            <title>Conforming XHTML 1.0 Transitional Template</title>
            <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
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
                    <img src="http://www.w3.org/Icons/valid-xhtml10" alt="Valid XHTML 1.0 Transitional" height="31" width="88"/>
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

Unrecognized symbols (that is they are not specified as literals with double quotas and have no whitespace) are regarded as string literals, unless they are unquoted.

.. code-block:: hylang

    (ml (tag :alfred J Kwak))

|Output:|

.. code-block:: xml

    <tag alfred="J">Kwak</tag>

Note that the symbol must still be valid Hy. For example ``J.`` with a
trailing dot is a reader error in Hy 1.x.


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
``~(hy.models.Keyword {expression})``.

.. note::  Keywords without value are interpreted as a keyword having the
           same value as the keyword name (called 
           `boolean attributes <http://www.w3.org/TR/html5/infrastructure.html#boolean-attributes>`__
           in HTML).

.. code-block:: hylang

    [(ml (tag :disabled)) (ml (tag ~(hy.models.Keyword "disabled"))) (ml (tag :disabled "disabled"))]

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

.. |Output:| replace:: [output]
