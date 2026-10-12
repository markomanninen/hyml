;; -*- coding: utf-8 -*-
;;
;; Copyright (c) 2017-2026 Marko Manninen
;;
;; Permission is hereby granted, free of charge, to any person obtaining a copy
;; of this software and associated documentation files (the "Software"), to deal
;; in the Software without restriction, including without limitation the rights
;; to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
;; copies of the Software, and to permit persons to whom the Software is
;; furnished to do so, subject to the following conditions:
;;
;; The above copyright notice and this permission notice shall be included in
;; all copies or substantial portions of the Software.
;;
;; THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
;; IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
;; FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
;; AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
;; LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
;; OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
;; THE SOFTWARE.

;------------------------------------------------
; HyML - XML / (X)HTML generator for Hy language
;------------------------------------------------
; ALMOST ALL IN ONE EXAMPLE
; specify parser macro (ML macros): xml, xhtml, xhtml5, html4, or html5
;(xhtml5
;  ; text content. xml declaration could also be (?xml :version "1.0" :encoding "UTF-8")
;  "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
;  ; text content. doctype could also be (!DOCTYPE "html")
;  "<!DOCTYPE html>"
;  ; define tag name as the first parameter
;  ; define attributes by keywords
;  (html :lang "en" :xmlns "http://www.w3.org/1999/xhtml"
;    ; define nested tags and content by similar manner
;    (head
;      ; everything else except the first parameter and keywords are
;      ; regarded as inner html content
;      (title "Page title"))
;    (body
;      ; text content. comments could also be (!-- "comments")
;      "<!-- body starts here -->"
;      ; short notation for div element and class attribute <div class=""/>
;      ; note: main-container will be main_container!
;      (.main-container
;         ; short notation for class attribute <h1 class=""/>
;         ; with multiple dot notation classes are concatenated with space
;         ; so .main.header becomes: class="main header"
;         ; unquote macro with ~ to execute normal hy code
;         ; after unquted expression rest of the code is parsed by ML macros
;         (h1.main.header ~(.capitalize "page header"))
;         ; short notation for id attribute <ul id=""/>
;         ; you should not use joined #main#sub similar to class notation althought it is not prohibited
;         ; this is because id="main sub" is not a good id according to html attribute specifications
;         (ul#main "List"
;           ; unquote splice processes lists and concatenates results
;           ; list-comp* is a slightly modified vesion of list-comp
;           ; in list-comp* list argument is the first and expression
;           ; the second argument. in list-comp those arguments are in reverse order
;           ~@(list-comp* [i [1 2 3]] `(li ~i)))))))
;----------------------------------------------------
(require hyml.variables [defvar deffun])
(require hyml.helpers [println list-comp list-comp*])
(require hyml.minimal [include])
(import hyml.core [HyMLError variables-and-functions])
(import hyml.specs [specs4 specs5 specs boolean-attributes optional-end-tags
                    optional-start-tags])

; markup is rendered at macro-expansion time
(eval-and-compile
  (import re contextvars)
  (import hyml.core [HyMLError keyword? coll? head-name ->str eval-in
                     escape-attribute expand]
          hyml.core :as core)
  (import hyml.specs [specs4 specs5 boolean-attributes optional-end-tags
                      optional-start-tags])

  ; parser settings. html dialects minimize attributes and end tags,
  ; the -min ones start tags too. xml does not validate tag names
  (setv dialects {
    "xml"       {"name" "xml"    "specs" None   "html" False "omit-start" False}
    "xhtml"     {"name" "xhtml4" "specs" specs4 "html" False "omit-start" False}
    "xhtml5"    {"name" "xhtml5" "specs" specs5 "html" False "omit-start" False}
    "html4"     {"name" "html4"  "specs" specs4 "html" True  "omit-start" False}
    "html5"     {"name" "html5"  "specs" specs5 "html" True  "omit-start" False}
    "html4-min" {"name" "html4"  "specs" specs4 "html" True  "omit-start" True}
    "html5-min" {"name" "html5"  "specs" specs5 "html" True  "omit-start" True}})

  (setv boolean-attribute-names (sfor kwd boolean-attributes kwd.name))

  ; variables of the ongoing render call. a context variable keeps
  ; nested and concurrent render calls apart
  (setv render-variables (contextvars.ContextVar "render-variables" :default None))
  ; False while rendering untrusted data (hyml.data), so that no input can
  ; ever reach code evaluation
  (setv evaluation-allowed (contextvars.ContextVar "evaluation-allowed" :default True))

  ; unquoted code sees the macros of this module (list-comp*, include, ...)
  (defn evaluate [code]
    (when (not (.get evaluation-allowed))
      (raise (HyMLError "code evaluation is disabled while rendering markup data")))
    (eval-in code "hyml.macros" (.get render-variables)))

  (defn catch-tag [code]
    (core.catch-tag code evaluate))

  ; spec tables and tag rules by plain tag name. building a Keyword for
  ; every lookup was the most expensive part of rendering
  (defn by-name [table]
    (dfor [key value] (.items table) key.name value))
  (setv spec-index {(id specs4) (by-name specs4) (id specs5) (by-name specs5)}
        end-rules (by-name optional-end-tags)
        start-rules (by-name optional-start-tags))

  (defn spec [tag specs]
    (setv index (.get spec-index (id specs)))
    (if (is index None)
        (.get specs (hy.models.Keyword (.lower tag)))
        (.get index (.lower tag))))

  ; void elements (br, img, ...) have no content and no end tag. :keyword
  ; literals build a Keyword on every call, so the sets are made once
  (defn void-names [table]
    (sfor [name s] (.items (by-name table)) :if (or (get s :forbidden) (get s :omit)) name))
  (setv void-index {(id specs4) (void-names specs4) (id specs5) (void-names specs5)})

  (defn void? [tag specs]
    (setv names (.get void-index (id specs)))
    (if (is names None)
        (do (setv s (spec tag specs))
            (bool (and s (or (get s :forbidden) (get s :omit)))))
        (in (.lower tag) names)))

  ; separate keyword attributes from the content. a keyword without a value
  ; (followed by another keyword or nothing) is a boolean attribute
  ; (get-content-attributes '(1 :k "x" 2 :l "y" 3))
  ; -> #([1 2 3] [["k" "x"] ["l" "y"]])
  (defn get-content-attributes [code]
    (setv content [] attributes [] kwd None)
    (for [item (expand code evaluate)]
      (if (keyword? item)
          (do
            (when (is-not kwd None)
              (.append attributes [kwd.name kwd.name]))
            (setv kwd item))
          (do
            (if (is kwd None)
                (.append content item)
                (.append attributes [kwd.name (attribute-value item)]))
            (setv kwd None))))
    (when (is-not kwd None)
      (.append attributes [kwd.name kwd.name]))
    #(content attributes))

  ; attribute values are evaluated, so that calculated expressions can be
  ; used for them. naive example: (if (% ~i 2) "odd" "even")
  (defn attribute-value [item]
    (->str (if (isinstance item hy.models.Expression) (evaluate item) item)))

  ; .content -> <div class="content"></div>
  ; #content -> <div id="content"></div>
  ; section.content -> <section class="content"></section>
  ; section#content.main -> <section id="content" class="main"></section>
  (defn shorthand [tag attributes]
    (if (not (re.search r"[.#]" tag))
        #(tag attributes)
        (do
          (setv parts (re.split r"([.#])" tag)
                ids (lfor i (range 1 (len parts) 2) :if (and (= (get parts i) "#") (get parts (+ i 1))) (get parts (+ i 1)))
                classes (lfor i (range 1 (len parts) 2) :if (and (= (get parts i) ".") (get parts (+ i 1))) (get parts (+ i 1))))
          #((or (get parts 0) "div")
            (merge-attribute (merge-attribute attributes "id" ids) "class" classes)))))

  ; add values to an existing attribute or append a new attribute
  (defn merge-attribute [attributes name values]
    (if (not values)
        attributes
        (do
          (setv value (.join " " values)
                attributes (list attributes))
          (for [[i [key old]] (enumerate attributes)]
            (when (= key name)
              (setv (get attributes i) [key (if (or (= old value) (not value)) old (+ old " " value))])
              (return attributes)))
          (+ attributes [[name value]]))))

  ; in html4 and html5, but not in xhtml, attributes can be minimized.
  ; <textarea readonly="readonly"></textarea> could simply be:
  ; <textarea readonly></textarea>, and values without spaces or
  ; quotes need no quotation marks
  (defn concat-attributes [attributes [minify False]]
    (.join "" (gfor [key value] attributes
                (cond (and minify (in key boolean-attribute-names) (= key value))
                      (+ " " key)
                      (and minify (re.fullmatch r"[^\s\"'=<>`]+" value))
                      (% " %s=%s" #(key value))
                      True
                      (% " %s=\"%s\"" #(key (escape-attribute value)))))))

  ; what follows an element: a tag name or a kind of text
  (defn sibling-kind [item tag]
    (cond (is-not tag None) (if (= tag "!--")
                                "#comment"
                                (.lower (or (get (re.split r"[.#]" tag) 0) "div")))
          (.startswith (setx text (->str item)) "<!--") "#comment"
          (and text (.isspace (get text 0))) "#whitespace"
          True "#text"))

  ; html tags may be omitted under the rules in specs
  (defn optional? [tag context [rules end-rules]]
    (setv rule (.get rules (.lower tag)))
    (bool (and rule context (rule context))))

  ; tag names of the element nodes, None for text
  (defn node-tags [items]
    (lfor item items (when (coll? item) (catch-tag (if item (get item 0) None)))))

  ; render a list of sibling nodes. siblings are known so that
  ; optional tags can be omitted
  (defn render-nodes [dialect items [parent None] [tags None]]
    (setv tags (if (is tags None) (node-tags items) tags)
          last-index (- (len items) 1)
          after-omitted None
          parts [])
    (for [[i [item tag]] (enumerate (zip items tags))]
      (if (is tag None)
          (setv after-omitted None
                part (->str item))
          (setv context {"followed-by" (when (< i last-index)
                                         (sibling-kind (get items (+ i 1)) (get tags (+ i 1))))
                         "is-last-child" (and (is-not parent None) (= i last-index))
                         "parent" (when parent (.lower parent))
                         "after-omitted" after-omitted}
                part (render-node dialect tag (cut item 1 None) context)
                kind (sibling-kind item tag)
                after-omitted (when (and (get dialect "html") (optional? kind context)) kind)))
      (.append parts part))
    (.join "" parts))

  ; DOCTYPE parts: names as such, other strings in quotation marks
  (defn doctype-part [item]
    (setv text (->str item))
    (if (and (isinstance item str) (not (isinstance item hy.models.Symbol))
             (not (re.fullmatch r"[\w-]+" text)))
        (+ "\"" text "\"")
        text))

  (defn render-node [dialect tag code context]
    (setv [content attributes] (get-content-attributes code))
    (cond
      ; comment tag <!-- -->
      ; can be written as a plain text also: (body "<!-- comments... -->")
      (= tag "!--")
      (+ "<!--" (render-nodes dialect content) "-->")
      ; xml document start tag
      (= tag "?xml")
      (+ "<?xml" (concat-attributes attributes) "?>")
      ; doctype code block is special because tag content is placed inside start tag
      ; (!DOCTYPE html) => <!DOCTYPE html>
      ; (!DOCTYPE note SYSTEM "Note.dtd") => <!DOCTYPE note SYSTEM "Note.dtd">
      (= (.upper tag) "!DOCTYPE")
      (+ "<!DOCTYPE " (.join " " (map doctype-part content)) ">")
      True
      (render-element dialect tag content attributes context)))

  (defn render-element [dialect tag content attributes context]
    (setv specs (get dialect "specs") html (get dialect "html"))
    (when specs
      (setv [tag attributes] (shorthand tag attributes))
      (when (is (spec tag specs) None)
        (raise (HyMLError (% "Tag name '%s' not meeting %s specifications."
                             #(tag (get dialect "name")))))))
    (setv void (and specs (void? tag specs)))
    (when (and void content)
      (raise (HyMLError (% "Tag '%s' is a void element and cannot have content." #(tag)))))
    (setv start (+ "<" tag (concat-attributes attributes html))
          tags (node-tags content)
          body (render-nodes dialect content tag tags))
    (cond
      ; <br> in html, <br/> in xhtml
      void (+ start (if html ">" "/>"))
      ; html has no self closing tags. end tag can be optional though,
      ; and in the -min dialects start tag without attributes too
      html (+ (if (and (get dialect "omit-start")
                       (not attributes)
                       (optional? tag
                                  (| context {"first-child" (when content
                                                              (sibling-kind (get content 0) (get tags 0)))})
                                  start-rules))
                  ""
                  (+ start ">"))
              body
              (if (optional? tag context) "" (+ "</" tag ">")))
      ; xml and xhtml use short tags for empty elements
      (not content) (+ start "/>")
      True (+ start ">" body "</" tag ">")))

  ; render forms with the named dialect: xml, xhtml, xhtml5, html4, or html5.
  ; variables are available to unquoted code beside the defvar registry.
  ; with evaluation False any attempt to evaluate code raises HyMLError
  (defn render [dialect code [variables None] * [evaluation True]]
    (setv token (.set render-variables variables)
          guard (.set evaluation-allowed evaluation))
    (try
      (render-nodes (get dialects dialect) (expand code evaluate))
      (finally
        (.reset evaluation-allowed guard)
        (.reset render-variables token))))

  ; single form parsers for custom shorthands:
  ; (defreader ✓ (parse-html5 (.parse-one-form &reader)))
  (defn parse-xml [code] (render "xml" [code]))
  (defn parse-xhtml [code] (render "xhtml" [code]))
  (defn parse-xhtml5 [code] (render "xhtml5" [code]))
  (defn parse-html4 [code] (render "html4" [code]))
  (defn parse-html5 [code] (render "html5" [code])))

; unicode Square Ml U+3396 is a shorthand for parsing tags. note that
; xml and similar macros will accept multiple expressions, not just
; an expression with a single root node
; enable with (require hyml.macros :readers [㎖])
(defreader ㎖
  (parse-xml (.parse-one-form &reader)))

; default xml parser
(defmacro xml [#* code] (render "xml" code))
; xhtml (1.0) is almost same as html4 and html5 but tags must be correctly closed
; for example <b> must be <b/> in xhtml. xhtml takes care of the html4 tag names
(defmacro xhtml [#* code] (render "xhtml" code))
; same as xhtml, but xhtml5 takes care of the html5 tag names
(defmacro xhtml5 [#* code] (render "xhtml5" code))
; strict set of html tag generator for html4
(defmacro html4 [#* code] (render "html4" code))
; strict set of html tag generator for html5
(defmacro html5 [#* code] (render "html5" code))
; html4 and html5 that omit optional start tags too: html, head, body,
; colgroup, and tbody when the rules allow it
(defmacro html4-min [#* code] (render "html4-min" code))
(defmacro html5-min [#* code] (render "html5-min" code))
