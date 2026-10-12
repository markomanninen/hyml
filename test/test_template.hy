;; Tests for render-template, extend-template and template. Expected
;; values come from doc/tests.rst and "HyML - Minimal.ipynb".

(require hyml.template *)
(import hyml.template *)
(import hyml.template :as T)
(import pytest)

(defn [pytest.fixture] test-dir [monkeypatch]
  (monkeypatch.setattr T "template_dir" "test/templates/"))

(defn test-render-template [test-dir]
  (assert (= (render-template "test.hy") "<tag/>"))
  (assert (= (render-template "test2.hy" {"tag" "content"}) "<tag>content</tag>")))

(defn test-extend-template [test-dir]
  (assert (= (render-template "test3.2.hy" {"val" "val"}) "<tags attr=\"val\"><tag/></tags>")))

(defn test-macro-in-template [test-dir]
  (assert (= (render-template "test4.hy" {"content" "content"}) "<tag>content</tag>")))

(defvar precedence-check "registry")

(defn test-explicit-variables-win [test-dir]
  ; the defvar registry used to override variables passed to render-template
  (assert (= (render-template "test5.hy") "<tag>registry</tag>"))
  (assert (= (render-template "test5.hy" {"precedence-check" "explicit"}) "<tag>explicit</tag>"))
  ; later dictionaries override earlier ones
  (assert (= (render-template "test5.hy" {"precedence-check" "first"} {"precedence-check" "second"})
             "<tag>second</tag>")))

(defn test-default-template-dir []
  (assert (= T.template-dir "templates/"))
  (assert (= (render-template "render.hyml" {"var" "Variable 1" "func" (fn [] "Function 1")})
             "<root><var>Variable 1</var><func>Function 1</func></root>"))
  (assert (= (render-template "extend.hyml" {"title" "Page title"})
             "<html><head><title>Page title</title></head><body><p>Page content</p></body></html>"))
  (assert (= (render-template "macro.hyml" {"class" "main"}) "<p class=\"main\"/>")))

(setv greeting "hello")

(defn test-template-macro []
  (assert (= (template {"val" "val"} `(tag :attr ~val)) "<tag attr=\"val\"/>"))
  (assert (= (template `(tag :attr ~val) {"val" "val"}) "<tag attr=\"val\"/>"))
  ; caller's globals are visible
  (assert (= (template `(p ~greeting)) "<p>hello</p>"))
  (assert (is (template {"val" "val"}) None))
  (assert (is (template "") None)))

(setv variables "mine")

(defn test-template-macro-keeps-caller-variables []
  ; template used to assign a global named variables in the caller's module
  (template `(p ~greeting))
  (assert (= variables "mine")))

(defn test-escape-in-template []
  (assert (= (template `(p ~(escape user)) {"user" "<b>"}) "<p>&lt;b&gt;</p>")))
