
HyML - Markup Language generator for Hy
=======================================

`HyML <https://github.com/markomanninen/hyml>`__ (acronym for Hy Markup
Language) is a set of macros to generate XML, XHTML, and HTML code in
Hy.

Introduction
------------

Main features
~~~~~~~~~~~~~

1. resembling syntax with XML
2. ability to evaluate Hy program code on macro expansion
3. processing lists and templates
4. custom variables (and functions)
5. tag name validation and attribute with html4 and html5 macros
6. start and end tag omission for html4 and html5
7. custom div tag, class and id attribute handlers for (x)html

You can use HyML for:

* static xml/xhtml/html content and file generation
* generating html code for Jupyter Notebook for example
* attached it to the server for dynamic html output generation
* practice and study
* challenge your imagination for any creative use

If you want to skip the nostalgic background rationale part, you can jump straight to the `installation <http://hyml.readthedocs.io/en/latest/#installation>`__ and the `documentation <http://hyml.readthedocs.io/en/latest/full.html#documentation>`__ part.


Motivation
~~~~~~~~~~

My primary intention is simple and mundane. Study. Study. Study.

First of all, I wanted to study more Lisp language. Seven years ago, I tried `Scheme <https://cisco.github.io/ChezScheme/>`__ and `CommonLisp <http://cliki.net/>`__ for form generation and validation purposes. Then `Clojure <https://clojure.org/>`__ for `website session handler <https://github.com/markomanninen/websesstudy>`__. Now, in 2017, I found another nice Lisp dialect which was seemlessly interoperating with Python, the language I've already used for an another decade on many spare time research projects.

This implementation, Pythonic Lisp, is called with a concise two character name, `Hy <http://docs.hylang.org/en/latest/>`__. Well chosen name makes it possible to create many "Hylarious" module names and acronyms when prefixed, infixed, and affixed with other words. Playful compounds can be created such as Hymn, Hy5, Hyway, Shyte, HyLogic, Hyffix, Hypothesis (actually already a Python test library), Archymedes (could have been), and now: **HyML**.

For other Lisp interpreters written in Python should be mentioned. One is from iconic Peter Norvig: `Lispy2 <http://norvig.com/lispy2.html>`__. Other is McCarthy's original Lisp by Fogus: `lithp.py <http://fogus.me/fun/lithp/>`__. Yet one more implementation of Paul Graham's `Root Lisp <https://github.com/kvalle/root-lisp>`__ by Kjetil Valle.

But none of these interact with Python `AST <https://docs.python.org/3/library/ast.html>`__ so that both Lisp and Python modules can be called from each sides, which is why I think Hy is an exceptionally interesting implementation.

Previous similar work
~~~~~~~~~~~~~~~~~~~~~

As a web developer, most of my time, I'm dealing with different kinds of scripting and markup languages. Code generation and following specifications is the foremost concern. Lisp itself is famous for code generation and domain language oriented macro behaviours. I thought it would be nice to make a generator that creates html code, simplifies creation of it and produces standard well defined code. It turned out that I was not so unique on that endeavour after all:

    "There are plenty of Lisp Markup Languages out there - every Lisp programmer seems to write at least one during his career...""

    -- `cl-who <http://weitz.de/cl-who/>`__

And to be honest, I've made it several times with other languages.

**Python**

Since Hy is a rather new language wrapper, there was no dedicated generator available (natively written) for it. Or at least I didn't find them. Maybe this is also, because one could easily use Python libraries. Any Python library can be imported to Hy with a simple `import` clause. And vice versa, any Hy module can be imported to Python with the ordinary `(import)` command.

I had made tag generator module for Python four years ago, namely `tagpy`, which is now called `Remarkuple3 <https://github.com/markomanninen/remarkuple3>`__. It is a general purpose class with automatic tag object creation on the fly. It follows strictly XML specifications. I should show some core parts of it.

First the tag class:

.. code-block:: python

    class TAG(object):
        def __init__(self, *args, **kw):
            """ Construct object, args are content and keywords are attributes """
            for arg in args:
                self.__dict__['content'].append(arg)
            for key, val in kw.items():
                self.__dict__['attributes'][key.lower()] = val
        def __getattr__(self, key):
            """
            Get attribute by key by dot notation: tag.attr. This is a short and nice way, but
            drawback is that Python has some reserved words, that can't be used this way. Method
            is also not-case-sensitive, because key is transformed to lower letters. Returning
            None if attribute is not found.
            """
            return self.__dict__['attributes'].get(key.lower(), None)
        def __str__(self):
            """
            Represent tag in string format. This is also a nice and short way to output the actual
            xml content. Concat content retrieves all nested tags recursively.
            """
            if self.__dict__['content']:
                return '<%s%s>%s</%s>' % (self.__class__.__name__, strattr(self.__dict__['attributes']),
                                          concat(*self.__dict__['content']), self.__class__.__name__)
            else:
                return '<%s%s/>' % (self.__class__.__name__, strattr(self.__dict__['attributes']))

Then helper initialization:

.. code-block:: python

    # create helper class to automaticly create tags based on helper class attribute / method overloading
    class htmlHelper(object):
        def create(self, tag):
            return type(tag, (TAG,), {})()
        def __getattr__(self, tag):
            return type(tag.lower(), (TAG,), {})

    # init helper for inclusion on the module
    helper = htmlHelper()

And finally usage example:

.. code-block:: python

    # load xml helper
    from remarkuple import helper as h
    # create anchor tag
    a = h.a()
    # create attribute for anchor
    a.href = "#"
    # add bolded tag text to anchor
    a += h.b("Link")
    print(a) # <a href="#"><b>Link</b></a>


**PHP**

I also made a PHP version of the HTML generator even earlier in 2007. That program factored classes for each html4 specified tag, and the rest was quite similar to Python version. Here is some parts of the code for comparison, first the generation of the tag classes:

.. code-block:: php

    $evalstr = '';
    // Factorize elements to classes
    foreach ($elements as $abbreviation => $element) {
        $abbreviation = strtoupper($abbreviation);
        $arg0 = strtolower($abbreviation);
        $arg1 = $element['name'];
        $arg2 = $element['omitted'] ? 'true' : 'false';
        $arg3 = $element['nocontent'] ? 'true' : 'false';
        $arg4 = $element['strict'] ? 'true' : 'false';

        $evalstr .= <<<EOF
    class HE_$abbreviation extends HtmlElement
    {
        function HE_$abbreviation(\$Attributes = null, \$Content = null, \$Index = null) {
            parent::Mm_HtmlElement('$arg0', '$arg1', $arg2, $arg3, $arg4);
            if (isset(\$Attributes) && is_array(\$Attributes)) \$this->attributes->container(\$Attributes);
            if (isset(\$Content)) \$this->add_content(\$Content, \$Index);
        }
    }
    EOF;
        }
        eval($evalstr);
    }

Then usage of the HtmlElement class:

.. code-block:: php

    include 'HtmlElement.php';
    $a = new HE_A(array('href' => '#'));
    $a->addContent(new HE_B("Link"));
    echo $a->render(); // <a href="#"><b>Link</b></a>

Doesn't this feel distantly quite Lispy? I mean generating and modifying code is same what macros do. Here it is done with PHP, and can be done with any language. But the thing is that `eval` in other languages is regarded as `evil` but for Lisp users it is a "principia primaria".

**Javascript**

Both Python and PHP versions are object oriented approaches to xml/html generation. Which is quite good after all. You can collect xml elements inside each other, manipulate them anyway you want before rendering output. One could similarly use world-famous `jQuery <https://jquery.com/>`__ javascript library, which has become a standard for DOM manipulation:

.. code-block:: javascript

    var a = $('<a/>');
    a.attr('href', "#");
    a.html($('<b>Link</b>');
    // there is a small catch here, a -element must be inner element of other
    // tag to be possible to be rendered as a whole
    var d = $('<div/>').html(a);
    console.log(d.html()); //<a href="#"><b>Link</b></a>

jQuery will construct tag objects (DOM elements) which you can access by jQuery methods that are too manifold to mention here.


**Template engines**

Then there are plenty of domain specific html template languages for each and every programming language. `Haml <http://haml.info/>`__ for Ruby. `Jinja <http://jinja.pocoo.org/>`__, `Mako <http://www.makotemplates.org/>`__, and `Genchi <https://genshi.edgewall.org/>`__ for Python. `Twig <http://twig.sensiolabs.org/>`__, `Smarty <http://www.smarty.net/>`__, and `Mustache <https://github.com/bobthecow/mustache.php>`__ for PHP.

Common to all is that they separate user interface logic from business and database logic to follow model-view-controller architecture.

Actually by using output buffering control one can easily create a template engine with PHP, that, by the way, is a template language itself already. For example this file.php content:

.. parsed-literal::

    <a href="<?=$href?>"><b><?=$link?></b></a>

With this code:

.. code-block:: php

    <?php
    function render($file, $data) {
        $content = file_get_contents($file);
        ob_start() && extract($data);
        eval('?>'.$content);
        $content = ob_get_clean();
        ob_flush();
        return $content;
    }
    render('file.php', array('href'=>"#", 'link'=>"Link"));
    ?>

Would render:

.. code-block:: xml

    <a href="#"><b>Link</b></a>

But now it is time to get back to Python, Lisp, and Hy. While Hy didn't have html generators until now, there are many Lisp implementations as previously told. You can find out some from `cliki.net <http://www.cliki.net/html%20generator>`__. You may also want to compare different implementations and their final DSL syntax to HyML from `@com-informatimago <https://gitlab.com/com-informatimago/com-informatimago/blob/master/common-lisp/html-generator/html-generators-in-lisp.txt>`__.

Python xml/html generators and processors are available from `Pypi <https://pypi.python.org/pypi?%3Aaction=search&term=html>`__. Some do more or less same than HyML, some are just loosely related to HyML.


Benefits and Implementation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

One thing in the object oriented method is that code itself doesn't resemble much like xhtml and html. So you are kind of approaching one domain language syntax from other syntax. In some cases it looks like ugly, in many small projects and cases it gives overhead in the amoun of code you need to write to output XML.

In Hy (and List generally), language syntax already resembles structured and nested markup langauge. Basic components of the language are tag notation with <, >, and / characters, tag names, tag attributes, and tag content. This behaves exactly with Lisp notation where the first element inside parentheses is normally a function, but now gets interpreted as a tag name. Keywords are usually indicated with a pair notation (:key "value"). And content is wrapped with double quotation characters. Only difference is that when indicator of nested content in XML is done "outside" of the start tag element, for example:

.. code-block:: xml

    <tag>content</tag>

In Hy, the content is inside the expression:

.. code-block:: hylang

    (tag "Content")

This makes parenthesized notation less verbose, so it tends to save some space. Drawback is of cource the fact that in a large code block there will be a lot of ending parentheses,a s you will find later. This will make the famous LISP acronym expanded to "(L)ots of (I)rritating (S)uperfluous (P)arentheses". But don't let it scare you, like it did me at first. After all, it is like with playing guitars; more different types you play, less it matters what you get on your hands. Soon you find you can't get it enought!

Lisp is also known as "code is data, data is code" -paradigm. This is perfectly visible on the HyML implementation I'm going give some sights now.

**Three aspects**

Data, was it just data as data or code, in the information technology it has always to do with three different aspects, namely:

1. processing lists (did I mention this somewhere earlier?!)
2. hierarchic structures
3. data types

In HyML the third part is pretty simple. On the output everything is just a plain text. There are no datatypes. In HyML data types has a negligible meaning. You should only give attention keywords that starts with colon (:) punctuation mark and literals that start with " and ends to the counterpart ".

Hierachical structure is defined by nested parentheses. Simple as that.

Processing list can be thought as a core Hy / Lisp language syntax utility, but there is also a specific syntactic feature called `unquote-splice <http://hyml.readthedocs.io/en/latest/#unquote-splice>`__, that can delegate a rendered list of elements to the parent element in HyML.

**Catch tag if you can**

We are talking about internal implementation of the HyML module now, especially the `macros.hy <https://github.com/markomanninen/hyml/blob/master/hyml/macros.hy>`__ file.

Let us take a moment to think of this expression in HyML:

.. code-block:: hylang

    (tag :attr "value" (sub "Content"))

One of the core parts of the HyML implementation is where to catch a tag name. Because the first element after opening parentheses in Hy is normally referring to a function, in HyML we need to change that functionality so that it refers to a tag name. Thus we need to catch tag name with the following code:

.. code-block:: hylang

    (defn catch-tag [code]
      (try
        ; code can be a symbol or a sub program
        ; thats why try to evaluate it. internal symbols like "input"
        ; for example are handled here too. just about anything can be
        ; a tag name
        (name (eval code))
        ; because evaluation most probably fails when code contains
        ; a symbol name that has not been specified on the global namespace,
        ; thats why return quoted code which should work every time.
        ; tag will be tag and evaluation of the code can go on without failing
        ; in the catch-tag part
        (except (e Exception) (eval 'code))))

Then the rest of the HyML expression gets interpreted. It can contain basicly just key-value pairs or content. Content can be a string or yet another similar HyML expression. `get-content-attributes` in `macros.hy <https://github.com/markomanninen/hyml/blob/master/hyml/macros.hy>`__ will find out all keyword pairs first and then rest of the expression in regarded as content, which is a string or a nested HyML expression.

**Semantic sugar**

Then some tag names are specially handled like: `unquote`, `unquote_splice`, , `!__`, `<?xml`, `!DOCTYPE`, and in `html4/5` mode tag names starting with . or # (`dispatch_reader_macro`).

For example ~ (unquote) symbol is used to switch the following expression from macro mode to Hy program mode. Other are mroe closely discussed in the `documentation <http://hyml.readthedocs.io/en/latest/#documentation>`__.

Finally when tags are created some rules from specs.hy `<https://github.com/markomanninen/hyml/blob/master/hyml/specs.hy>`__ are used to create either long or short tags and to minimize attributes.

This is basicly it. Without html4/5 functionality code base would be maybe one third of the current code base. Tag validation and minimizing did add a lot of extra code to the module. Being a plain xml generator it would have been comparative to `Remarkuple <https://github.com/markomanninen/remarkuple3/blob/master/remarkuple/main.py>`__ code base.

Templating feature requires using globals variable dictionary as a registry for variables. Macro to expand and evaluate templates is pretty simple:

.. code-block:: hylang

    (defmacro include [template]
      `(do
        ; tokenize is needed to parse external file
        (import [hy.importer [tokenize]])
        (with [f (open ~template)]
          ; funky ~@` part is needed as a prefix to the template code
          ; so that code on template wont get directly expanded but only
          ; after everything had been collected by the macro for final evaluation
          (tokenize (+ "~@`(" (f.read) ")")))))

One more catch is to use variables from globals dictionary when evaluating code on parser:

.. code-block:: hylang

    (.join "" (map ~name (eval (second code) variables)))

This makes it possible to use custom variables at the moment in HyML module and maybe custom functions on templates later in future.

Now, with these simple language semantic modifications to Hy, I have managed to do a new programable markup language, HyML, that produces XML / XHTML, and HTML code as an output.

Future work
~~~~~~~~~~~

There is a nice feature set on arclanguage html generator, that still could optimize the size of the codebase of HyML: http://arclanguage.github.io/ref/html.html

Downside of this is that implementation like that adds more functionas to call and maintain, while HyML at this point is a pretty minimal implementation for its purposes.


Quick start
-----------

Project is hosted in GitHub: https://github.com/markomanninen/hyml/


Installation
~~~~~~~~~~~~

HyML can be installed effortlessly with `pip <https://pip.pypa.io/en/latest/installing/>`__:

    `$ pip install hyml`

HyML requires of cource Python and Hy on a computer. Hy will be automaticly installed, or updated at least to version 0.12.1, if it wasn't already.


Environment check
~~~~~~~~~~~~~~~~~

You should check that your environment meets the same requirements than mine. My environment for the sake of clarity:

.. code-block:: hylang

    (import hy sys)
    (print "Hy version: " hy.__version__)
    (print "Python" sys.version)


.. parsed-literal::

    Hy version:  0.12.1
    Python 3.5.2 |Anaconda custom (64-bit)| (default, Jul  5 2016, 11:41:13) [MSC v.1900 64 bit (AMD64)]


So this module has been run on Hy 0.12.1 and Python 3.5.2 installed by Anaconda package in Windows. If any problems occurs, you should report them to: https://github.com/markomanninen/hyml/issues


Import main macros
~~~~~~~~~~~~~~~~~~

After installation you can import ML macros with the next code snippet in Hy REPL or Jupyter Notebook with `calysto_hy <https://github.com/Calysto/calysto_hy>`__ kernel:

.. code-block:: hylang

    (require [hyml.macros [*]])
    (import (hyml.macros (*)))

Let us just try that everything works with a small test:

.. code-block:: hylang

    #㎖(tag :attr "val" (sub "Content"))

That should output:

.. code-block:: xml

    <tag attr="val"><sub>Content</sub></tag>

So is this it, the code generation at its best? With 35 characters of code we made 40 characters xml string. Not to mention some 500 lines of code on a module to make it work! Give me one more change and let me convince you with the next `all-in-one <http://hyml.readthedocs.io/en/latest/#all-in-one-example>`__ example.


Documentation
-------------

This is the core documentation part of the HyML.


All-in-one example
~~~~~~~~~~~~~~~~~~

First, I'd like to show an example that presents the most of the features included in the HyML module. Then I will go through all the features case by case.

.. code-block:: hylang

    (defvar rows [[1 2 3] [1 2 3]])
    (print (indent (xhtml5
      "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
      "<!DOCTYPE html>"
      (html :lang "en" :xmlns "http://www.w3.org/1999/xhtml"
        (head (title "Page title"))
        (body
          "<!-- body starts here -->"
          (.main-container
            (h1.main.header
              ~(.capitalize "page header"))
            (ul#main "List"
              ~@(list-comp* [[idx num] (enumerate (range 3))]
                `(li :class ~(if (even? idx) "even" "odd") ~num)))
            (table
              (thead
                (tr (th "Col 1") (th "Col 2") (th "Col 3")))
              (tbody
                ~@(include "rows.hy")))))))))

This will output:

.. code-block:: xml

    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE html>
    <html lang="en" xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <title>Page title</title>
        </head>
        <body>
            <!-- body starts here -->
            <div class="main_container">
                <h1 class="main header">Page header</h1>
                <ul id="main">
                    List
                    <li class="even">0</li>
                    <li class="odd">1</li>
                    <li class="even">2</li>
                </ul>
                <table>
                    <thead>
                        <tr>
                            <th>Col 1</th>
                            <th>Col 2</th>
                            <th>Col 3</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>1</td>
                            <td>2</td>
                            <td>3</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </body>
    </html>


XML, HTML4, HTML5, XHTML, and XHTML5
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

At the moment HyML module contains ``xml``, ``html4``, ``html5``,
``xhtml``, and ``xhtml5`` macros (called as ``ML`` macros in short) to
generate the (M)arkup (L)anguage code. ``xml`` is a generic generator
which allows using any tag names and attributes. ``html4`` and ``xhtml``
macros allows to use only html4 specified tag names. Same applies to
``html5`` and ``xhtml5``. Complete chart of the allowed elements are
listed at the end of the document.

Tags can be created with or without attributes, as well as with or
without content. For example:

.. code-block:: hylang

    (println
      (xml (node))
      (xml (node :attribute "")) ; force to use empty attribute
      (xml (node :attribute "value"))
      (xml (node :attribute "value" "")) ; force to use empty content
      (xml (node :attribute "value" "Content")))

Output:

.. code-block:: xml

    <node/>
    <node attribute=""/>
    <node attribute="value"/>
    <node attribute="value"></node>
    <node attribute="value">Content</node>


However in ``html4`` and ``html5`` there are certain tags that cannot
have endings so they will be rendered in correct form by the parser.
"Forbidden" labeled tags are listed at the end of the document. One of
them is for example the meta tag:

.. code-block:: hylang

    (html4 (meta :name "keywords" :content "HTML,CSS,XML,JavaScript"))

Output:

.. code-block:: xml

    <meta name=keywords content=HTML,CSS,XML,JavaScript>


To see and compare the difference in xhtml, let macro print the same:

.. code-block:: hylang

    (xhtml (meta :name "keywords" :content "HTML,CSS,XML,JavaScript"))

Output:

.. code-block:: xml

    <meta name="keywords" content="HTML,CSS,XML,JavaScript"/>


**Shorthand macro**

``#㎖`` (Square Ml) can be used as a shorthand `reader
macro <http://docs.hylang.org/en/latest/language/readermacros.html>`__
for generating xml/html/xhtml code:

.. code-block:: hylang

    #㎖(html
        (head (title "Page title"))
        (body (div "Page content" :class "container")))

Output:

.. code-block:: xml

    <html><head><title>Page title</title></head><body><div class="container">Page content</div></body></html>


``#㎖`` actually utilizes ``xml`` macro so same result can be achieved
with the next, maybe more convenient and recommended notation:

.. code-block:: hylang

    (xml
      (html
        (head (title "Page title"))
        (body (div "Page content" :class "container"))))

Output:

.. code-block:: xml

    <html><head><title>Page title</title></head><body><div class="container">Page content</div></body></html>


It is not possible to define other ``ML`` macro to be used with the
``#㎖`` shorthand reader macro. You could however define your own
shorthands following next quidelines:

    (defsharp {unicode-char} [code] (parse-{parser} code))

``{unicode-char}`` can be any `unicode
char <https://unicode-table.com/en/>`__ you want. ``{parser}`` must be
one of the following available parsers: xml, xhtml, xhtml5, html4, or
html5.

With ``#㎖`` shorthand you have to provide a single root node for
generating code. Directry using ``ML`` macros makes it possible to
generate multiple instances of code, and might be more informative
notation style anyway:

.. code-block:: hylang

    (xml (p "Sentence 1") (p "Sentence 2") (p "Sentence 3"))

Output:

.. code-block:: xml

    <p>Sentence 1</p><p>Sentence 2</p><p>Sentence 3</p>


Let us then render the code, not just printing it. This can be done via
``html5>`` macro imported earlier from helpers:

.. code-block:: hylang

    (html4> (p "Content is " (b king) !))

Output:

.. raw:: html

    <p Content is <b>king</b>!</p>


Renderers are available for all ``ML`` macros: ``xml>``, ``xhtml>``,
``xhtml5>``, ``html4>``, and ``html5>``.


Validation and minimizing
~~~~~~~~~~~~~~~~~~~~~~~~~

If validation of the html tag names is a concern, then one should use
``html4``, ``html5``, ``xhtml``, and ``xhtml5`` macro family. In the
example below if we try to use ``time`` element in ``html4``, which is
specifically available in ``html5`` only, we will get an ``HyMLError``
exception:

.. code-block:: hylang

    ;(try
    ; (html4 (time))
    ; (catch [e [HyMLError]]))
    ;hytml.macros.HyMLError: Tag 'time' not meeting html4 specs

Other features in ``html4`` and ``html5`` macros are attribute and tag
minimizing. Under the `certain
rules <https://html.spec.whatwg.org/multipage/syntax.html#optional-tags>`__
start and end tags can be removed from the output. Also boolean
attributes can be shortened. In ``html4`` and ``html5`` macros
minimizing is a default feature that can't be bypassed. If you do not
want to minimize code, you must use ``xhtml`` or ``xhtml5`` macro.
Contrary in ``xhtml`` and ``xhtml5`` macros attribute and tag minimizing
is NOT available. Instead all tags are strictly closed and attributes in
``key="value"`` format.

**HTML4**

.. code-block:: hylang

    ; valid html4 document
    (html4 (title) (table (tr (td "Cell 1") (td "Cell 2") (td "Cell 3"))))

Output:

.. code-block:: xml

    <title/><table><tr><td>Cell 1<td>Cell 2<td>Cell 3</table>

**XHTML**

.. code-block:: hylang

    ; in xhtml tags and attributes will be output in complete format
    (xhtml (title) (table (tr (td "Cell 1") (td "Cell 2") (td "Cell 3"))))

Output:

.. code-block:: xml

    <title/><table><tr><td>Cell 1</td><td>Cell 2</td><td>Cell 3</td></tr></table>


Note that above xhtml code is still not a valid xhtml document even tags
and attributes are perfectly output. ``ML`` macros do no validate
structure of the document just tag names. For validation one should use
official `validator <https://validator.w3.org/>`__ service and follow
the html `specifications <https://w3c.github.io/html/>`__ to create a
valid document. ``ML`` macros can be used to guide on that process but
more importantly it is meant to automatize the generation of the xml
code while adding programming capabilities on it.

``xml`` on the other hand doesn't give a dime of the used tag names.
They can be anything, even processed names. Same applies to keywords,
values, and contents. You should use more strict ``xhtml``, ``xhtml5``,
``html4``, and ``html5`` macros to make sure that tag names are
corresponding to HTML4 or HTML5 specifications.


.. code-block:: hylang

    ; see how boolean attribute minimizing works
    (html4 (input :disabled "disabled"))

Output:

.. code-block:: html

    <input disabled>


Unquoting code
~~~~~~~~~~~~~~

In all ``ML`` macros you can pass any code in it. See for example:

.. code-block:: hylang

    (xml (p "Sum: " (b (apply sum [[1 2 3 4]]))))

Output:

.. code-block:: xml

    <p>Sum: <b><apply>sum<[1, 2, 3, 4]/></apply></b></p>


But you see, the result was not possibly what you expected. ``ML``
macros will interpret the first item of the *expression* as a name of
the tag. Thus *apply* becomes a tag name. Until the next *expression*
everything else is interpreted either as a content or a keyword.

However using ``~`` (unquote) symbol, ``ML`` macro behaviour can be
stopped for a moment:

.. code-block:: hylang

    (xml (p "Sum: " (b ~(apply sum [[1 2 3 4]])) !))

Output:

.. code-block:: xml

    <p>Sum: <b>10</b>!</p>


So the following expression after ``~`` will be evaluated and then
result is returned back to the original parser. And the rest of the code
will be interpreted via macro. In this case it was just an exclamation
mark.

    Note that it is not mandatory to wrap strings with ``""`` if given input
    doesn't contain any spaces. You could also single quote simple
    non-spaced letter sequences. So ``!`` is same as ``"!"`` in this case.

Quoting and executing normal Hy code inside html gives almost unlimited
possibility to use HyML as a templating engine. Of cource there is also
a risk to evaluate code that breaks the code execution. Plus
uncontrolled template engine code may be a security consern.


Unquote splice
~~~~~~~~~~~~~~

In addition to unquote, one can handle lists and iterators with ``~@``
(unquote-splice) symbol. This is particularly useful when a list of html
elements needs to be passed to the parent element. Take for example this
table head generation snippet:

.. code-block:: hylang

    (xhtml
     (table (thead
       (tr ~@(list-comp
             `(th :class (if (even? ~i) "even" "odd") ~label " " ~i)
             [[i label] (enumerate (* ["col"] 3))])))))

Output:

.. code-block:: xml

    <table><thead><tr><th class="even">col 0</th><th class="odd">col 1</th><th class="even">col 2</th></tr></thead></table>


`List
comprehensions <https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions>`__
notation might seem a little bit strange for some people. It takes a
processing part (expression) as the first argument, and the actual list
to be processed as the second argument. On a nested code this will move
lists to be processed in first hand to the end of the notation. For
example:

.. code-block:: hylang

    (xml>
      ~@(list-comp `(ul (b "List")
          ~@(list-comp `(li item " " ~li)
              [li uls]))
        [uls [[1 2] [1 2]]]))

Output:

.. raw:: html

    <ul><b>List</b><li>item 1</li><li>item 2</li></ul><ul><b>List</b><li>item 1</li><li>item 2</li></ul>


But there is another slighly modified macro to use in similar manner:


``list-comp*``
~~~~~~~~~~~~~~

Let's do again above example but this time with a dedicated
``list-comp*`` macro. Now the lists to be processed is passed as the
first argument to the ``list-comp*`` macro and the expression for
processing list items is the second argument. Yet the second argument
itself contains a new list processing loop until final list item is to
be processed. This is perhaps easier to follow for some people:

.. code-block:: hylang

    (xhtml
      ~@(list-comp* [uls [[1 2] [1 2]]]
        `(ul (b "List")
          ~@(list-comp* [li uls]
            `(li item " " ~li)))))

Output:

.. code-block:: xml

    <ul><b>List</b><li>item 1</li><li>item 2</li></ul><ul><b>List</b><li>item 1</li><li>item 2</li></ul>


Of cource it is just a matter of the taste which one you like.
``list-comp*`` with ``unquote-splice`` symbol (``~@``) reminds us that
it is possible to create any similar custom macros for the HyML
processor. ``~@`` can be thought as a macro caller, not just unquoting
and executing Hy code in a normal lisp mode.

Here is a more complex table generation example from the
`remarkuple <http://nbviewer.jupyter.org/github/markomanninen/remarkuple3/blob/master/Remarkuple%203%20documentation.ipynb>`__
Python module docs. One should notice how variables (``col``, ``row``,
and ``cell``) are referenced by quoting them:

.. code-block:: hylang

    (html4>
      (table#data
        (caption "Data table")
        (colgroup
          (col :style "background-color:red")
          (col :style "background-color: green")
          (col :style "background-color: blue"))
        (thead
          (tr
            ~@(list-comp* [col ["Column 1" "Column 2" "Column 3"]]
              `(th ~col))))
        (tbody#tbody1
         ~@(list-comp* [row (range 1 3)]
           `(tr
             ~@(list-comp* [cell (range 3)]
               `(td  ~row "." ~cell)))))
        (tbody#tbody2
         ~@(list-comp* [row (range 1 3)]
           `(tr
             ~@(list-comp* [cell (range 3)]
               `(td  ~row "." ~cell)))))
        (tfoot
          (tr
            (td :colspan "3" "Footer")))))

Output:

.. raw:: html

    <table id=data><caption>Data table<colgroup><col style=background-color:red><col style="background-color: green"><col style="background-color: blue"><thead><tr><th>Column 1</th><th>Column 2</th><th>Column 3</th></thead><tbody id=tbody1><tr><td>1.0<td>1.1<td>1.2</tr><tr><td>2.0<td>2.1<td>2.2</tr></tbody><tbody id=tbody2><tr><td>1.0<td>1.1<td>1.2</tr><tr><td>2.0<td>2.1<td>2.2</tr><tfoot><tr><td colspan=3>Footer</tfoot></table>


**Address book table from CSV file**

We should of course be able to use external source for the html. Let's
try with a short csv file:

.. code-block:: hylang

    (xhtml>
     (table.data
       (caption "Contacts")
       ~@(list-comp*
         [[idx row] (enumerate (.split (.read (open "data.csv" "r")) "\n"))]
         (if (pos? idx)
             `(tbody
                ~@(list-comp* [item (.split row ",")]
                  `(td ~item)))
             `(thead
                ~@(list-comp* [item (.split row ",")]
                  `(th ~item)))))))

Output:

.. raw:: html

    <table class="data"><caption>Contacts</caption><thead><th>Title</th><th>Name</th><th>Phone</th></thead><tbody><td>Mr.</td><td>John</td><td>07868785831</td></tbody><tbody><td>Miss</td><td>Linda</td><td>0141-2244-5566</td></tbody><tbody><td>Master</td><td>Jack</td><td>0142-1212-1234</td></tbody><tbody><td>Mr.</td><td>Bush</td><td>911-911-911</td></tbody></table>


Templates
~~~~~~~~~

It is possible to load code from an external file too. This feature has
not been deeply implemented yet, but you get the feeling by the next
example. Firt I'm just going to show external template file content:

.. code-block:: hylang

    (with [f (open "template.hy")] (print (f.read)))

Output:

.. code-block:: hylang

    (html :lang ~lang
      (head (title ~title))
      (body
      	(p ~body)))


Then I use ``include`` macro to read and process the content:

.. code-block:: hylang

    (defvar lang "en"
            title "Page title"
            body "Content")

    (xhtml ~@(include "template.hy"))

Output:

.. code-block:: xml

    <html lang="en"><head><title>Page title</title></head><body><p>Content</p></body></html>


All globally defined variables are available on ``ML`` macros likewise:

.. code-block:: hylang

    (xhtml ~lang ", " ~title ", " ~body)

Output:

.. parsed-literal::

    en, Page title, Content


The `MIT <http://choosealicense.com/licenses/mit/>`__ License
-------------------------------------------------------------

Copyright (c) 2017 Marko Manninen
