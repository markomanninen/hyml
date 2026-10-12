HyML tests
============

Test main features
------------------

Tests for all main features of HyML library are run with
`pytest <https://pytest.org/>`__. Clone the repository, install HyML with
the test extras, and run ``pytest`` in the repository root:

.. code-block:: bash

    $ git clone https://github.com/markomanninen/hyml.git
    $ cd hyml
    $ pip install -e ".[test]"
    $ pytest

If all tests pass, everything is fine. If not, then *Houston, we have
a problem!*

The tests are in the ``test`` directory:

- ``test/test_minimal.hy`` -- the MiNiMaL ``ml`` macro, ``defvar``,
  ``deffun``, ``include``, ``parse-mnml``, and the ``#i`` reader macro
- ``test/test_macros.hy`` -- the ``xml``, ``xhtml``, ``xhtml5``, ``html4``,
  and ``html5`` macros, the ``#㎖`` reader macro, validation, attribute
  minimizing, and optional end tags
- ``test/test_template.hy`` -- ``render-template``, ``extend-template``,
  and the ``template`` macro
- ``test/test_helpers.hy`` -- ``indent``, ``println``, ``list-comp``,
  ``list-comp*``, and the Jupyter Notebook renderers
- ``test/test_api.py`` -- the Python API ``hyml.render``
- ``test/test_ext.py`` -- the Babel message extractor

Test templates are in ``test/templates`` and the example templates of the
documentation in ``templates``. Pytest finds the Hy test modules with the
help of ``test/conftest.py``.

A few representative asserts from the test suite:

.. code-block:: hylang

    (require hyml.minimal *)
    (import hyml.minimal *)

    ; empty things
    (assert (= (ml) ""))
    (assert (= (ml ("")) "</>"))
    ; tag names are not evaluated
    (assert (= (ml (tag)) "<tag/>"))
    (assert (= (ml (J)) "<J/>"))
    (assert (= (ml (~(.upper "tag"))) "<TAG/>"))
    ; content, attribute names, and values
    (assert (= (ml (tag :attr "val" "content")) "<tag attr=\"val\">content</tag>"))
    (assert (= (ml (tag ~(hy.models.Keyword "attr") "val")) "<tag attr=\"val\"/>"))
    ; boolean attributes
    (assert (= (ml (tag Content :attr1 :attr2)) "<tag attr1=\"attr1\" attr2=\"attr2\">Content</tag>"))
    ; unquote splice
    (assert (= (ml (tag ~@(lfor item [1 2 3] `(sub ~(str item)))))
               "<tag><sub>1</sub><sub>2</sub><sub>3</sub></tag>"))
    ; variables and functions
    (defvar x "variable")
    (deffun f (fn [x] x))
    (assert (= (ml (tag ~x ~(f "function"))) "<tag>variablefunction</tag>"))
    ; parse-mnml with variable and function dictionary
    (assert (= (parse-mnml '(tag :attr ~var ~(func))
                           {"var" "val" "func" (fn [] "Content")})
               "<tag attr=\"val\">Content</tag>"))
    ; templates
    (import hyml.template [render-template])
    (import hyml.template)
    (setv hyml.template.template-dir "test/templates/")
    (assert (= (render-template "test2.hy" {"tag" "content"}) "<tag>content</tag>"))
    (setv hyml.template.template-dir "templates/")

    (require hyml.macros [xml html4 html5 xhtml])
    ; html minimizing and optional end tags
    (assert (= (html4 (meta :name "keywords" :content "HTML,CSS,XML,JavaScript"))
               "<meta name=keywords content=HTML,CSS,XML,JavaScript>"))
    (assert (= (html5 (input :type "checkbox" :checked :disabled))
               "<input type=checkbox checked disabled>"))
    (assert (= (html5 (ul (li "a") (li "b"))) "<ul><li>a<li>b</ul>"))
    (assert (= (html4 (title)) "<title></title>"))
    (assert (= (xhtml (title)) "<title/>"))
    ; shorthand notation
    (assert (= (xhtml (div#main.big.wide "x")) "<div id=\"main\" class=\"big wide\">x</div>"))
    ; special tags
    (assert (= (xml (!DOCTYPE note SYSTEM "Note.dtd")) "<!DOCTYPE note SYSTEM \"Note.dtd\">"))

Because ``.hy`` modules can't go through the assertion rewriting of
pytest, the tests are run with ``--assert=plain``, which is already set in
``pyproject.toml``. A failing assert shows the line, but not the compared
values.
