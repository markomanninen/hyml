
HyML - XML / (X)HTML generator for Hy
=====================================

Introduction
------------

HyML (acronym for Hy Markup Language) is a set of macros to generate XML, XHTML and HTML code in Hy.

Motivation
~~~~~~~~~~

My intention is simple and mundane. Study. Study. Study.

First of all I wanted to study more Lisp. A decade back I tried `Scheme<https://cisco.github.io/ChezScheme/>`__ and `CommonLisp<http://cliki.net/>`__ for form generation and validation purposes. Then `Clojure<https://clojure.org/>`__ for `website session handler<https://github.com/markomanninen/websesstudy>`__. Now, in 2017, I found another nice Lisp dialect which was seemlessly interoperating with Python, the language I've already used for an another decade on many spare time research projects.

This implementation, Pythonic Lisp, is called with a concise two character name, `Hy<http://docs.hylang.org/en/latest/>`__. Well chosen name makes it possible to create many "Hylarious" module names and acronyms when prefixed, infixed and affixed with other words. Compounds like Hymn, Hy5, Hyway, Shyte, HyLogic, Hyffix, Hypothesis (actually already a Python test library), and now: HyML.


Previous similar work
~~~~~~~~~~~~~~~~~~~~~

As a web developer, most of my time, I'm dealing with different kinds of scripting and markup languages. Code generation and following specifications is the foremost concern. Lisp itself is famous for code generation and domain language oriented macro behaviours. I thought it would be nice to make a generator that creates html code, simplifies creation of it and produces standard well defined code. It turned out that I was not so unique on that endeavour after all:

    There are plenty of Lisp Markup Languages out there - every Lisp programmer seems to write at least one during his career

    -- `<http://weitz.de/cl-who/>`__

**Python**

Since Hy is a rather new language wrapper, there was no dedicated generator available (natively written) for it. Or at least I didn't find them. Maybe this is also, because one could easily use Python libraries. Any Python library can be imported to Hy with a simple import clause. And vice versa, any Hy module can be imported to Python with the ordinary import command. I have made such html generator module for Python 4 years ago, namely `tagpy` which is now called `Remarkuple3<https://github.com/markomanninen/remarkuple3>`__. It is a general purpose class with automatic tag object creation on the fly. I should show somne core parts of it. First the tag class:

.. code:: python

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
            Represent tag in string format. This is also a nice and short way to ouput the actual
            xml content. Concat content retrieves all nested tags recursively.
            """
            if self.__dict__['content']:
                return '<%s%s>%s</%s>' % (self.__class__.__name__, strattr(self.__dict__['attributes']),
                                          concat(*self.__dict__['content']), self.__class__.__name__)
            else:
                return '<%s%s/>' % (self.__class__.__name__, strattr(self.__dict__['attributes']))

Then helper initialization:

.. code:: python

    # create helper class to automaticly create tags based on helper class attribute / method overloading
    class htmlHelper(object):
        def create(self, tag):
            return type(tag, (TAG,), {})()
        def __getattr__(self, tag):
    return type(tag.lower(), (TAG,), {})

    # init helper fpr inclusion on the module
    helper = htmlHelper()

and finally a frontend usage example:

.. code:: python

    # load html helper
    from remarkuple import helper as h
    # create anchor tag
    a = h.a()
    # create attribute for anchor
    a.href = "#"
    # add bolded tag text to anchor
    a += h.b("Link")
    print(a)

**PHP**

I also made a PHP version of the HTML generator even earlier in 2007. It factored classes for each html4 specified tag, and the rest was quite similar to Python version. Here is some parts of the code for comparison, first the generation of the tag classes:

.. code:: php

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

Then front end usage:

.. code:: php

    include 'HtmlElement.php';
    $a = new HE_A(array('href' => '#'));
    $a->addContent(new HE_B("Link"));
    echo $a->render();

Both Python and PHP versions are object oriented approaches to html generation. Which is quite good after all. You can collect html elements inside each other, manipulate them anyway you want before rendering ouput. One could similarly use world-famous `jQuery<https://jquery.com/>`__ javascript library, which has become a standard for DOM manipulation.

**Javascript**

.. code:: javascript

    var a = $('<a/>');
    a.attr('href', "#");
    a.html($('<b>Link</b>');
    console.log(a.html());

This will construct tag objects which you can access by jQuery methods that are too manifold to mention here.

**Template engines**

Then there are plenty of domain specific html template languages for each and every programming language. `Haml<http://haml.info/>`__ for Ruby. `Jinja<http://jinja.pocoo.org/>`__, `Mako<http://www.makotemplates.org/>`__, and `Genchi<https://genshi.edgewall.org/>`__ for Python. `Twig<http://twig.sensiolabs.org/>`__, `Smarty<http://www.smarty.net/>`__ and `Mustache<https://github.com/bobthecow/mustache.php>`__ for PHP. They separate user interace logic from business logic mostly following model-view-controller architecture. I did several similar approaches to create a template engine with PHP, that is a template language itself already.


Benefits
~~~~~~~~

One thing in object oriented method is that code itself ...

Static file generation

Attached to the server html output generation

http://www.cliki.net/html%20generator

https://pypi.python.org/pypi?%3Aaction=search&term=html


Quick start
-----------

...

Installation
~~~~~~~~~~~~



Environment check
~~~~~~~~~~~~~~~~~

My environment for the sake of clarity:

.. code:: lisp

    (import hy sys)
    (print "Hy version: " hy.__version__)
    (print "Python" sys.version)


.. parsed-literal::

    Hy version:  0.12.1
    Python 3.5.2 |Anaconda custom (64-bit)| (default, Jul  5 2016, 11:41:13) [MSC v.1900 64 bit (AMD64)]
    

Import main macros
~~~~~~~~~~~~~~~~~~

.. code:: lisp

    (require [hyml.macros [*]]
             [hyml.helpers [*]])
    (import (hyml.macros (*)))
    (import (hyml.helpers (indent)))

Then we are ready for the show!

Documentation
-------------

All-in-one example
------------------

First, I’d like to show an example that presents the most of the features included in the HyML module. Then I will go through all the features case by case.

.. code:: lisp

    ; by default there is no indentation, thus for pretty print we use indent
    (print (indent 
      ; specify parser macro (ML macros) that must be one of the following:
      ; xml, xhtml, xhtml5, html4, or html5 
      (xhtml5
      ; plain text content
      ; xml declaration below could also be done with a custom tag: (?xml :version "1.0" :encoding "UTF-8")
      "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
      ; more plain text content
      ; doctype could also be done with a custom tag: (!DOCTYPE "html")
      "<!DOCTYPE html>"
      ; define tag name as the first parameter
      ; define attributes by keywords
      (html :lang "en" :xmlns "http://www.w3.org/1999/xhtml"
        ; define nested tags and content by similar manner
        (head
          ; everything else except the first parameter and keywords are
          ; regarded as inner html content
          (title "Page title"))
        (body
          ; plain text content
          ; comments could also be done with a custom tag: (!-- "comments")
          "<!-- body starts here -->"
          ; short notation for div element and class attribute <div class=""/>
          ; note that - character in main-container will become to main_container due to Hy
          ; internal language construction
          (.main-container
             ; short notation for class attribute for specified element: <h1 class=""/>
             ; with multiple dot notation classes are concatenated with space
             (h1.main.header
               ; unquote macro with ~ to evaluate normal Hy code
               ; after unquoted expression rest of the code is continued to be parsed by ML macros again
               ~(.capitalize "page header"))
             ; short notation for id attribute for specified element: <ul id=""/>
             ; you should not use joined #main#sub similar to class notation, althought it is not prohibited,
             ; because id="main sub" is not a good id according to html attribute specifications
             (ul#main "List"
               ; unquote splice ~@ processes lists and concatenates results
               ; list-comp* is a slightly modified vesion of list-comp
               ; in list-comp* the list argument is the first and the expression is
               ; the second argument. in native list-comp those arguments are in reverse order
               ~@(list-comp* [[idx num] (enumerate (range 3))]
                             ; quote (`) a line and unquote variables and expressions to calculate
                             ; and set correct class for even and odd list items
                             `(li :class ~(if (even? idx) "even" "odd") ~num)))))))))


.. parsed-literal::

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
    		</div>
    	</body>
    </html>
    

XML, HTML4, HTML5, XHTML, and XHTML5
------------------------------------

At the moment HyML module contains ``xml``, ``html4``, ``html5``,
``xhtml``, and ``xhtml5`` macros (called as ``ML`` macros in short) to
generate the (M)arkup (L)anguage code. ``xml`` is a generic generator
which allows using any tag names and attributes. ``html4`` and ``xhtml``
macros allows to use only html4 specified tag names. Same applies to
``html5`` and ``xhtml5``. Complete chart of the allowed elements are
listed at the end of the document.

Tags can be created with or without attributes, as well as with or
without content. For example:

.. code:: python

    (println
      (xml (node))
      (xml (node :attribute "")) ; force to use empty attribute
      (xml (node :attribute "value"))
      (xml (node :attribute "value" "")) ; force to use empty content
      (xml (node :attribute "value" "Content")))


.. parsed-literal::

    <node/>
    <node attribute=""/>
    <node attribute="value"/>
    <node attribute="value"></node>
    <node attribute="value">Content</node>
    

However in ``html4`` and ``html5`` there are certain tags that cannot
have endings so they will be rendered in correct form by the parser.
"Forbidden" labeled tags are listed at the end of the document. One of
them is for example the meta tag:

.. code:: python

    (html4 (meta :name "keywords" :content "HTML,CSS,XML,JavaScript"))




.. parsed-literal::

    <meta name=keywords content=HTML,CSS,XML,JavaScript>



To see and compare the difference in xhtml, let macro print the same:

.. code:: python

    (xhtml (meta :name "keywords" :content "HTML,CSS,XML,JavaScript"))




.. parsed-literal::

    <meta name="keywords" content="HTML,CSS,XML,JavaScript"/>



Shorthand macro
~~~~~~~~~~~~~~~

``#㎖`` (Square Ml) can be used as a shorthand `reader
macro <http://docs.hylang.org/en/latest/language/readermacros.html>`__
for generating xml/html/xhtml code:

.. code:: python

    #㎖(html
        (head (title "Page title"))
        (body (div "Page content" :class "container")))




.. parsed-literal::

    <html><head><title>Page title</title></head><body><div class="container">Page content</div></body></html>



``#㎖`` actually utilizes ``xml`` macro so same result can be achieved
with the next, maybe more convenient and recommended notation:

.. code:: python

    (xml
      (html
        (head (title "Page title"))
        (body (div "Page content" :class "container"))))




.. parsed-literal::

    <html><head><title>Page title</title></head><body><div class="container">Page content</div></body></html>



It is not possible to define other ``ML`` macro to be used with the
``#㎖`` shorthand reader macro. You could however define your own
shorthands following next quidelines:

(defreader {unicode-char} [code] (parse-{parser} code))

``{unicode-char}`` can be any `unicode
char <https://unicode-table.com/en/>`__ you want. ``{parser}`` must be
one of the following available parsers: xml, xhtml, xhtml5, html4, or
html5.

With ``#㎖`` shorthand you have to provide a single root node for
generating code. Directry using ``ML`` macros makes it possible to
generate multiple instances of code, and might be more informative
notation style anyway:

.. code:: python

    (xml (p "Sentence 1") (p "Sentence 2") (p "Sentence 3"))




.. parsed-literal::

    <p>Sentence 1</p><p>Sentence 2</p><p>Sentence 3</p>



Let us then render the code, not just printing it. This can be done via
``html5>`` macro imported earlier from helpers:

.. code:: python

    (html4> "Content is " (b king) !)




.. raw:: html

    Content is <b>king</b>!



Renderers are available for all ``ML`` macros: ``xml>``, ``xhtml>``,
``xhtml5>``, ``html4>``, and ``html5>``.

Validation and minimizing
-------------------------

If validation of the html tag names is a concern, then one should use
``html4``, ``html5``, ``xhtml``, and ``xhtml5`` macro family. In the
example below if we try to use ``time`` element in ``html4``, which is
specifically available in ``html5`` only, we will get an ``HyTMLError``
exception:

.. code:: python

    ;(try
    ; (html4 (time))
    ; (catch [e [HyTMLError]]))
    ;hytml.macros.HyTMLError: Tag 'time' not meeting html4 specs

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

.. code:: python

    ; valid html4 document
    (html4 (title) (table (tr (td "Cell 1") (td "Cell 2") (td "Cell 3"))))




.. parsed-literal::

    <title/><table><tr><td>Cell 1<td>Cell 2<td>Cell 3</table>



.. code:: python

    ; in xhtml tags and attributes will be output in complete format
    (xhtml (title) (table (tr (td "Cell 1") (td "Cell 2") (td "Cell 3"))))




.. parsed-literal::

    <title/><table><tr><td>Cell 1</td><td>Cell 2</td><td>Cell 3</td></tr></table>



.. raw:: html

   <blockquote>

Note that above xhtml code is still not a valid xhtml document even tags
and attributes are perfectly output. ``ML`` macros do no validate
structure of the document just tag names. For validation one should use
official `validator <https://validator.w3.org/>`__ service and follow
the html `specifications <https://w3c.github.io/html/>`__ to create a
valid document. ``ML`` macros can be used to guide on that process but
more importantly it is meant to automatize the generation of the xml
code while adding programming capabilities on it.

.. raw:: html

   </blockquote>

.. raw:: html

   <blockquote>

``xml`` on the other hand doesn't give a dime of the used tag names.
They can be anything, even processed names. Same applies to keywords,
values, and contents. You should use more strict ``xhtml``, ``xhtml5``,
``html4``, and ``html5`` macros to make sure that tag names are
corresponding to HTML4 or HTML5 specifications.

.. raw:: html

   </blockquote>

.. code:: python

    ; see how boolean attribute minimizing works
    (html4 (input :disabled "disabled"))




.. parsed-literal::

    <input disabled>



Unquoting code
--------------

In all ``ML`` macros you can pass any code in it. See for example:

.. code:: python

    (xml (p "Sum: " (b (apply sum [[1 2 3 4]]))))




.. parsed-literal::

    <p>Sum: <b><apply>sum<[1, 2, 3, 4]/></apply></b></p>



But you see, the result was not possibly what you expected. ``ML``
macros will interpret the first item of the *expression* as a name of
the tag. Thus *apply* becomes a tag name. Until the next *expression*
everything else is interpreted either as a content or a keyword.

However using ``~`` (unquote) symbol, ``ML`` macro behaviour can be
stopped for a moment:

.. code:: python

    (xml (p "Sum: " (b ~(apply sum [[1 2 3 4]])) !))




.. parsed-literal::

    <p>Sum: <b>10</b>!</p>



So the following expression after ``~`` will be evaluated and then
result is returned back to the original parser. And the rest of the code
will be interpreted via macro. In this case it was just an exclamation
mark.

.. raw:: html

   <blockquote>

Note that it is not mandatory to wrap strings with ``""`` if given input
doesn't contain any spaces. You could also single quote simple
non-spaced letter sequences. So ``!`` is same as ``"!"`` in this case.

.. raw:: html

   </blockquote>

Quoting and executing normal Hy code inside html gives almost unlimited
possibility to use HyML as a templating engine. Of cource there is also
a risk to evaluate code that breaks the code execution. Plus
uncontrolled template engine code may be a security consern.

Unquote splice
--------------

In addition to unquote, one can handle lists and iterators with ``~@``
(unquote-splice) symbol. This is particularly useful when a list of html
elements needs to be passed to the parent element. Take for example this
table head generation snippet:

.. code:: python

    (xhtml 
     (table (thead
       (tr ~@(list-comp
             `(th :class (if (even? ~i) "even" "odd") ~label " " ~i)
             [[i label] (enumerate (* ["col"] 3))])))))




.. parsed-literal::

    <table><thead><tr><th class="even">col 0</th><th class="odd">col 1</th><th class="even">col 2</th></tr></thead></table>



`List
comprehensions <https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions>`__
notation might seem a little bit strange for some people. It takes a
processing part (expression) as the first argument, and the actual list
to be processed as the second argument. On a nested code this will move
lists to be processed in first hand to the end of the notation. For
example:

.. code:: python

    (xml> 
      ~@(list-comp `(ul (b "List")
          ~@(list-comp `(li item " " ~li)
              [li uls]))
        [uls [[1 2] [1 2]]]))




.. raw:: html

    <ul><b>List</b><li>item 1</li><li>item 2</li></ul><ul><b>List</b><li>item 1</li><li>item 2</li></ul>



But there is another slighly modified macro to use in similar manner:

``list-comp*``
--------------

Let's do again above example but this time with a dedicated
``list-comp*`` macro. Now the lists to be processed is passed as the
first argument to the ``list-comp*`` macro and the expression for
processing list items is the second argument. Yet the second argument
itself contains a new list processing loop until final list item is to
be processed. This is perhaps easier to follow for some people:

.. code:: python

    (xhtml
      ~@(list-comp* [uls [[1 2] [1 2]]]
        `(ul (b "List")
          ~@(list-comp* [li uls]
            `(li item " " ~li)))))




.. parsed-literal::

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

.. code:: python

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




.. raw:: html

    <table id=data><caption>Data table<colgroup><col style=background-color:red><col style="background-color: green"><col style="background-color: blue"><thead><tr><th>Column 1</th><th>Column 2</th><th>Column 3</th></thead><tbody id=tbody1><tr><td>1.0<td>1.1<td>1.2</tr><tr><td>2.0<td>2.1<td>2.2</tr></tbody><tbody id=tbody2><tr><td>1.0<td>1.1<td>1.2</tr><tr><td>2.0<td>2.1<td>2.2</tr><tfoot><tr><td colspan=3>Footer</tfoot></table>



Address book table from CSV file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We should of course be able to use external source for the html. Let's
try with a short csv file:

.. code:: python

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




.. raw:: html

    <table class="data"><caption>Contacts</caption><thead><th>Title</th><th>Name</th><th>Phone</th></thead><tbody><td>Mr.</td><td>John</td><td>07868785831</td></tbody><tbody><td>Miss</td><td>Linda</td><td>0141-2244-5566</td></tbody><tbody><td>Master</td><td>Jack</td><td>0142-1212-1234</td></tbody><tbody><td>Mr.</td><td>Bush</td><td>911-911-911</td></tbody></table>



Templates
---------

It is possible to load code from an external file too. This feature has
not been deeply implemented yet, but you get the feeling by the next
example. Firt I'm just going to show external template file content:

.. code:: python

    (with [f (open "template.hy")] (print (f.read)))


.. parsed-literal::

    (html :lang ~lang
      (head (title ~title))
      (body
      	(p ~body)))
    

Then I use ``include`` macro to read and process the content:

.. code:: python

    (defvar lang "en"
            title "Page title"
            body "Content")
    
    (xhtml ~@(include "template.hy"))




.. parsed-literal::

    <html lang="en"><head><title>Page title</title></head><body><p>Content</p></body></html>



All globally defined variables are available on ``ML`` macros likewise:

.. code:: python

    (xhtml ~lang ", " ~title ", " ~body)




.. parsed-literal::

    en, Page title, Content



HTML4 / 5 specifications
------------------------

``xml`` does not care about the markup specifications other than general
tag and attribute notation. It is totally dummy about the naming
conventions of the tags or their relation to each other or global
structure of the markup document. It is all on the responsibility of the
user to make it correct.

``html4`` and ``html5`` macros will render tags as specified below.
These macros will minimize code when possible. Using undefined tag will
raise an error. Attributes are not validated however. One should use
official `validator <http://validator.w3.org/>`__ for a proper
validation.

Below is the last example of using ``ML`` macros. It will print the
first 5 rows of the HTML4/5 specifications.

Columns are:

-  Tag name
-  Tag title
-  Forbidden (if there should be no content or end tag)
-  Omit (forbidden plus omit short tag like ``<col>``)
-  HTML4 (is html4 compatible?)
-  HTML5 (is html5 compatible?)

.. code:: python

    (xhtml>
      (table.data
        (caption "HTML Element Specifications")
        (thead
          (tr
            ~@(list-comp* [col ["Tag name" "Tag title" "Forbidden" "Omit" "HTML4" "HTML5"]]
              `(th ~col))))
        (tbody 
         ~@(list-comp* [[id row] (take 5 (.items (do (import (hyml.macros (specs))) specs)))]
           (do
            `(tr
              (td ~(.upper (get row :name)))
              (td ~(get row :name))
              (td ~(get row :forbidden))
              (td ~(get row :omit))
              (td ~(get row :html4) :class (if ~(get row :html4) "html4" ""))
              (td :class (if ~(get row :html5) "html5" ""))))))))




.. raw:: html

    <table class="data"><caption>HTML Element Specifications</caption><thead><tr><th>Tag name</th><th>Tag title</th><th>Forbidden</th><th>Omit</th><th>HTML4</th><th>HTML5</th></tr></thead><tbody><tr><td>A</td><td>a</td><td>False</td><td>False</td><td class="html4">✓</td><td class="html5"/>✓</tr><tr><td>ABBR</td><td>abbr</td><td>False</td><td>False</td><td class="html4">✓</td><td class="html5"/>✓</tr><tr><td>ACRONYM</td><td>acronym</td><td>False</td><td>False</td><td class="html4">✓</td><td class=""/></tr><tr><td>ADDRESS</td><td>address</td><td>False</td><td>False</td><td class="html4">✓</td><td class="html5"/>✓</tr><tr><td>APPLET</td><td>applet</td><td>False</td><td>False</td><td class="html4">✓</td><td class=""/></tr></tbody></table>



.. code:: python

    ; lets import pandas dataframe for easy table view
    (import [pandas])
    ; set max rows to 200 to prevent pruning displayed rows
    (pandas.set_option "display.max_rows" 200)
    ; disable jupyter notebook autoscroll on the next cell

.. code:: python

    %javascript IPython.OutputArea.prototype._should_scroll = function(lines) {return false}

.. code:: python

    ; show all specs
    (pandas.DataFrame.transpose (pandas.DataFrame specs))

.. raw:: html

    <div>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th></th>
          <th>:forbidden</th>
          <th>:html4</th>
          <th>:html5</th>
          <th>:name</th>
          <th>:omit</th>
          <th>:title</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th>:a</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>a</td>
          <td>False</td>
          <td>Anchor</td>
        </tr>
        <tr>
          <th>:abbr</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>abbr</td>
          <td>False</td>
          <td>Abbreviation</td>
        </tr>
        <tr>
          <th>:acronym</th>
          <td>False</td>
          <td>True</td>
          <td>False</td>
          <td>acronym</td>
          <td>False</td>
          <td>Acronym</td>
        </tr>
        <tr>
          <th>:address</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>address</td>
          <td>False</td>
          <td>Address</td>
        </tr>
        <tr>
          <th>:applet</th>
          <td>False</td>
          <td>True</td>
          <td>False</td>
          <td>applet</td>
          <td>False</td>
          <td>Java applet</td>
        </tr>
        <tr>
          <th>:area</th>
          <td>True</td>
          <td>True</td>
          <td>True</td>
          <td>area</td>
          <td>True</td>
          <td>Image map region</td>
        </tr>
        <tr>
          <th>:article</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>article</td>
          <td>False</td>
          <td>Defines an article</td>
        </tr>
        <tr>
          <th>:aside</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>aside</td>
          <td>False</td>
          <td>Defines content aside from the page content</td>
        </tr>
        <tr>
          <th>:audio</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>audio</td>
          <td>False</td>
          <td>Defines sound content</td>
        </tr>
        <tr>
          <th>:b</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>b</td>
          <td>False</td>
          <td>Bold text</td>
        </tr>
        <tr>
          <th>:base</th>
          <td>True</td>
          <td>True</td>
          <td>True</td>
          <td>base</td>
          <td>True</td>
          <td>Document base URI</td>
        </tr>
        <tr>
          <th>:basefont</th>
          <td>True</td>
          <td>True</td>
          <td>False</td>
          <td>basefont</td>
          <td>False</td>
          <td>Base font change</td>
        </tr>
        <tr>
          <th>:bdi</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>bdi</td>
          <td>False</td>
          <td>Isolates a part of text that might be formatte...</td>
        </tr>
        <tr>
          <th>:bdo</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>bdo</td>
          <td>False</td>
          <td>BiDi override</td>
        </tr>
        <tr>
          <th>:big</th>
          <td>False</td>
          <td>True</td>
          <td>False</td>
          <td>big</td>
          <td>False</td>
          <td>Large text</td>
        </tr>
        <tr>
          <th>:blockquote</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>blockquote</td>
          <td>False</td>
          <td>Block quotation</td>
        </tr>
        <tr>
          <th>:body</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>body</td>
          <td>False</td>
          <td>Document body</td>
        </tr>
        <tr>
          <th>:br</th>
          <td>True</td>
          <td>True</td>
          <td>True</td>
          <td>br</td>
          <td>True</td>
          <td>Line break</td>
        </tr>
        <tr>
          <th>:button</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>button</td>
          <td>False</td>
          <td>Button</td>
        </tr>
        <tr>
          <th>:canvas</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>canvas</td>
          <td>False</td>
          <td>Used to draw graphics, on the fly, via scripti...</td>
        </tr>
        <tr>
          <th>:caption</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>caption</td>
          <td>False</td>
          <td>Table caption</td>
        </tr>
        <tr>
          <th>:center</th>
          <td>False</td>
          <td>True</td>
          <td>False</td>
          <td>center</td>
          <td>False</td>
          <td>Centered block</td>
        </tr>
        <tr>
          <th>:cite</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>cite</td>
          <td>False</td>
          <td>Citation</td>
        </tr>
        <tr>
          <th>:code</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>code</td>
          <td>False</td>
          <td>Computer code</td>
        </tr>
        <tr>
          <th>:col</th>
          <td>True</td>
          <td>True</td>
          <td>True</td>
          <td>col</td>
          <td>True</td>
          <td>Table column</td>
        </tr>
        <tr>
          <th>:colgroup</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>colgroup</td>
          <td>False</td>
          <td>Table column group</td>
        </tr>
        <tr>
          <th>:datalist</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>datalist</td>
          <td>False</td>
          <td>Specifies a list of pre-defined options for in...</td>
        </tr>
        <tr>
          <th>:dd</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>dd</td>
          <td>False</td>
          <td>Definition description</td>
        </tr>
        <tr>
          <th>:del</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>del</td>
          <td>False</td>
          <td>Deleted text</td>
        </tr>
        <tr>
          <th>:details</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>details</td>
          <td>False</td>
          <td>Defines additional details that the user can v...</td>
        </tr>
        <tr>
          <th>:dfn</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>dfn</td>
          <td>False</td>
          <td>Defined term</td>
        </tr>
        <tr>
          <th>:dialog</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>dialog</td>
          <td>False</td>
          <td>Defines a dialog box or window</td>
        </tr>
        <tr>
          <th>:dir</th>
          <td>False</td>
          <td>True</td>
          <td>False</td>
          <td>dir</td>
          <td>False</td>
          <td>Directory list</td>
        </tr>
        <tr>
          <th>:div</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>div</td>
          <td>False</td>
          <td>Generic block-level container</td>
        </tr>
        <tr>
          <th>:dl</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>dl</td>
          <td>False</td>
          <td>Definition list</td>
        </tr>
        <tr>
          <th>:dt</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>dt</td>
          <td>False</td>
          <td>Definition term</td>
        </tr>
        <tr>
          <th>:em</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>em</td>
          <td>False</td>
          <td>Emphasis</td>
        </tr>
        <tr>
          <th>:embed</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>embed</td>
          <td>False</td>
          <td>Defines a container for an external (non-HTML)...</td>
        </tr>
        <tr>
          <th>:fieldset</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>fieldset</td>
          <td>False</td>
          <td>Form control group</td>
        </tr>
        <tr>
          <th>:figcaption</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>figcaption</td>
          <td>False</td>
          <td>Defines a caption for a &lt;figure&gt; element</td>
        </tr>
        <tr>
          <th>:figure</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>figure</td>
          <td>False</td>
          <td>Specifies self-contained content</td>
        </tr>
        <tr>
          <th>:font</th>
          <td>False</td>
          <td>True</td>
          <td>False</td>
          <td>font</td>
          <td>False</td>
          <td>Font change</td>
        </tr>
        <tr>
          <th>:footer</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>footer</td>
          <td>False</td>
          <td>Defines a footer for a document or section</td>
        </tr>
        <tr>
          <th>:form</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>form</td>
          <td>False</td>
          <td>Interactive form</td>
        </tr>
        <tr>
          <th>:frame</th>
          <td>True</td>
          <td>True</td>
          <td>False</td>
          <td>frame</td>
          <td>False</td>
          <td>Frame</td>
        </tr>
        <tr>
          <th>:frameset</th>
          <td>False</td>
          <td>True</td>
          <td>False</td>
          <td>frameset</td>
          <td>False</td>
          <td>Frameset</td>
        </tr>
        <tr>
          <th>:h1</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>h1</td>
          <td>False</td>
          <td>Level-one heading</td>
        </tr>
        <tr>
          <th>:h2</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>h2</td>
          <td>False</td>
          <td>Level-two heading</td>
        </tr>
        <tr>
          <th>:h3</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>h3</td>
          <td>False</td>
          <td>Level-three heading</td>
        </tr>
        <tr>
          <th>:h4</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>h4</td>
          <td>False</td>
          <td>Level-four heading</td>
        </tr>
        <tr>
          <th>:h5</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>h5</td>
          <td>False</td>
          <td>Level-five heading</td>
        </tr>
        <tr>
          <th>:h6</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>h6</td>
          <td>False</td>
          <td>Level-six heading</td>
        </tr>
        <tr>
          <th>:head</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>head</td>
          <td>False</td>
          <td>Document head</td>
        </tr>
        <tr>
          <th>:header</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>header</td>
          <td>False</td>
          <td>Defines a header for a document or section</td>
        </tr>
        <tr>
          <th>:hr</th>
          <td>True</td>
          <td>True</td>
          <td>True</td>
          <td>hr</td>
          <td>True</td>
          <td>Horizontal rule</td>
        </tr>
        <tr>
          <th>:html</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>html</td>
          <td>False</td>
          <td>HTML document</td>
        </tr>
        <tr>
          <th>:i</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>i</td>
          <td>False</td>
          <td>Italic text</td>
        </tr>
        <tr>
          <th>:iframe</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>iframe</td>
          <td>False</td>
          <td>Inline frame</td>
        </tr>
        <tr>
          <th>:img</th>
          <td>True</td>
          <td>True</td>
          <td>True</td>
          <td>img</td>
          <td>True</td>
          <td>Inline image</td>
        </tr>
        <tr>
          <th>:input</th>
          <td>True</td>
          <td>True</td>
          <td>True</td>
          <td>input</td>
          <td>True</td>
          <td>Form input</td>
        </tr>
        <tr>
          <th>:ins</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>ins</td>
          <td>False</td>
          <td>Inserted text</td>
        </tr>
        <tr>
          <th>:isindex</th>
          <td>True</td>
          <td>True</td>
          <td>True</td>
          <td>isindex</td>
          <td>False</td>
          <td>Input prompt</td>
        </tr>
        <tr>
          <th>:kbd</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>kbd</td>
          <td>False</td>
          <td>Text to be input</td>
        </tr>
        <tr>
          <th>:keygen</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>keygen</td>
          <td>True</td>
          <td>Defines a key-pair generator field (for forms)</td>
        </tr>
        <tr>
          <th>:label</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>label</td>
          <td>False</td>
          <td>Form field label</td>
        </tr>
        <tr>
          <th>:legend</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>legend</td>
          <td>False</td>
          <td>Fieldset caption</td>
        </tr>
        <tr>
          <th>:li</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>li</td>
          <td>False</td>
          <td>List item</td>
        </tr>
        <tr>
          <th>:link</th>
          <td>True</td>
          <td>True</td>
          <td>True</td>
          <td>link</td>
          <td>True</td>
          <td>Document relationship</td>
        </tr>
        <tr>
          <th>:main</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>main</td>
          <td>False</td>
          <td>Specifies the main content of a document</td>
        </tr>
        <tr>
          <th>:map</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>map</td>
          <td>False</td>
          <td>Image map</td>
        </tr>
        <tr>
          <th>:mark</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>mark</td>
          <td>False</td>
          <td>Defines marked/highlighted text</td>
        </tr>
        <tr>
          <th>:menu</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>menu</td>
          <td>False</td>
          <td>Menu list</td>
        </tr>
        <tr>
          <th>:menuitem</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>menuitem</td>
          <td>False</td>
          <td>Defines a command/menu item that the user can ...</td>
        </tr>
        <tr>
          <th>:meta</th>
          <td>True</td>
          <td>True</td>
          <td>True</td>
          <td>meta</td>
          <td>True</td>
          <td>Metadata</td>
        </tr>
        <tr>
          <th>:meter</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>meter</td>
          <td>False</td>
          <td>Defines a scalar measurement within a known ra...</td>
        </tr>
        <tr>
          <th>:nav</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>nav</td>
          <td>False</td>
          <td>Defines navigation links</td>
        </tr>
        <tr>
          <th>:noframes</th>
          <td>False</td>
          <td>True</td>
          <td>False</td>
          <td>noframes</td>
          <td>False</td>
          <td>Frames alternate content</td>
        </tr>
        <tr>
          <th>:noscript</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>noscript</td>
          <td>False</td>
          <td>Alternate script content</td>
        </tr>
        <tr>
          <th>:object</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>object</td>
          <td>False</td>
          <td>Object</td>
        </tr>
        <tr>
          <th>:ol</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>ol</td>
          <td>False</td>
          <td>Ordered list</td>
        </tr>
        <tr>
          <th>:optgroup</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>optgroup</td>
          <td>False</td>
          <td>Option group</td>
        </tr>
        <tr>
          <th>:option</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>option</td>
          <td>False</td>
          <td>Menu option</td>
        </tr>
        <tr>
          <th>:output</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>output</td>
          <td>False</td>
          <td>Defines the result of a calculation</td>
        </tr>
        <tr>
          <th>:p</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>p</td>
          <td>False</td>
          <td>Paragraph</td>
        </tr>
        <tr>
          <th>:param</th>
          <td>True</td>
          <td>True</td>
          <td>True</td>
          <td>param</td>
          <td>True</td>
          <td>Object parameter</td>
        </tr>
        <tr>
          <th>:picture</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>picture</td>
          <td>False</td>
          <td>Defines a container for multiple image resources</td>
        </tr>
        <tr>
          <th>:pre</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>pre</td>
          <td>False</td>
          <td>Preformatted text</td>
        </tr>
        <tr>
          <th>:progress</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>progress</td>
          <td>False</td>
          <td>Represents the progress of a task</td>
        </tr>
        <tr>
          <th>:q</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>q</td>
          <td>False</td>
          <td>Short quotation</td>
        </tr>
        <tr>
          <th>:rp</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>rp</td>
          <td>False</td>
          <td>Defines what to show in browsers that do not s...</td>
        </tr>
        <tr>
          <th>:rt</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>rt</td>
          <td>False</td>
          <td>Defines an explanation/pronunciation of charac...</td>
        </tr>
        <tr>
          <th>:ruby</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>ruby</td>
          <td>False</td>
          <td>Defines a ruby annotation (for East Asian typo...</td>
        </tr>
        <tr>
          <th>:s</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>s</td>
          <td>False</td>
          <td>Strike-through text</td>
        </tr>
        <tr>
          <th>:samp</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>samp</td>
          <td>False</td>
          <td>Sample output</td>
        </tr>
        <tr>
          <th>:script</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>script</td>
          <td>False</td>
          <td>Client-side script</td>
        </tr>
        <tr>
          <th>:section</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>section</td>
          <td>False</td>
          <td>Defines a section in a document</td>
        </tr>
        <tr>
          <th>:select</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>select</td>
          <td>False</td>
          <td>Option selector</td>
        </tr>
        <tr>
          <th>:small</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>small</td>
          <td>False</td>
          <td>Small text</td>
        </tr>
        <tr>
          <th>:source</th>
          <td>True</td>
          <td>False</td>
          <td>True</td>
          <td>source</td>
          <td>True</td>
          <td>Defines multiple media resources for media ele...</td>
        </tr>
        <tr>
          <th>:span</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>span</td>
          <td>False</td>
          <td>Generic inline container</td>
        </tr>
        <tr>
          <th>:strike</th>
          <td>False</td>
          <td>True</td>
          <td>False</td>
          <td>strike</td>
          <td>False</td>
          <td>Strike-through text</td>
        </tr>
        <tr>
          <th>:strong</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>strong</td>
          <td>False</td>
          <td>Strong emphasis</td>
        </tr>
        <tr>
          <th>:style</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>style</td>
          <td>False</td>
          <td>Embedded style sheet</td>
        </tr>
        <tr>
          <th>:sub</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>sub</td>
          <td>False</td>
          <td>Subscript</td>
        </tr>
        <tr>
          <th>:summary</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>summary</td>
          <td>False</td>
          <td>Defines a visible heading for a &lt;details&gt; element</td>
        </tr>
        <tr>
          <th>:sup</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>sup</td>
          <td>False</td>
          <td>Superscript</td>
        </tr>
        <tr>
          <th>:table</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>table</td>
          <td>False</td>
          <td>Table</td>
        </tr>
        <tr>
          <th>:tbody</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>tbody</td>
          <td>False</td>
          <td>Table body</td>
        </tr>
        <tr>
          <th>:td</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>td</td>
          <td>False</td>
          <td>Table data cell</td>
        </tr>
        <tr>
          <th>:textarea</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>textarea</td>
          <td>False</td>
          <td>Multi-line text input</td>
        </tr>
        <tr>
          <th>:tfoot</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>tfoot</td>
          <td>False</td>
          <td>Table foot</td>
        </tr>
        <tr>
          <th>:th</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>th</td>
          <td>False</td>
          <td>Table header cell</td>
        </tr>
        <tr>
          <th>:thead</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>thead</td>
          <td>False</td>
          <td>Table head</td>
        </tr>
        <tr>
          <th>:time</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>time</td>
          <td>False</td>
          <td>Defines a date/time</td>
        </tr>
        <tr>
          <th>:title</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>title</td>
          <td>False</td>
          <td>Document title</td>
        </tr>
        <tr>
          <th>:tr</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>tr</td>
          <td>False</td>
          <td>Table row</td>
        </tr>
        <tr>
          <th>:track</th>
          <td>True</td>
          <td>False</td>
          <td>True</td>
          <td>track</td>
          <td>True</td>
          <td>Defines text tracks for media elements (&lt;video...</td>
        </tr>
        <tr>
          <th>:tt</th>
          <td>False</td>
          <td>True</td>
          <td>False</td>
          <td>tt</td>
          <td>False</td>
          <td>Teletype text</td>
        </tr>
        <tr>
          <th>:u</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>u</td>
          <td>False</td>
          <td>Underlined text</td>
        </tr>
        <tr>
          <th>:ul</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>ul</td>
          <td>False</td>
          <td>Unordered list</td>
        </tr>
        <tr>
          <th>:var</th>
          <td>False</td>
          <td>True</td>
          <td>True</td>
          <td>var</td>
          <td>False</td>
          <td>Variable</td>
        </tr>
        <tr>
          <th>:video</th>
          <td>False</td>
          <td>False</td>
          <td>True</td>
          <td>video</td>
          <td>False</td>
          <td>Defines a video or movie</td>
        </tr>
        <tr>
          <th>:wbr</th>
          <td>True</td>
          <td>False</td>
          <td>True</td>
          <td>wbr</td>
          <td>True</td>
          <td>Defines a possible line-break</td>
        </tr>
      </tbody>
    </table>
    </div>


The `MIT <http://choosealicense.com/licenses/mit/>`__ License
-------------------------------------------------------------

Copyright (c) 2017 Marko Manninen
