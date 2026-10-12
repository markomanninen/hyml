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

(import xml.dom.minidom)
(import hyml.core [HyMLError])

;----------------------------------------
; print multiple statements on new lines
;----------------------------------------

(defmacro println [#* args]
  `(do ~@(gfor arg args `(print ~arg))))

;----------------------------------------------
; render html for the Jupyter Notebook document
; this is not mandatory for HyML other macros
; this is just for the html render in NB
;----------------------------------------------
; IPython is imported only when the expanded code runs, and the ML
; macros are called through hy.R so they need not be required by the user

(defmacro ml> [#* code]
  `(hy.I.IPython/display.HTML (hy.R.hyml/minimal.ml ~@code)))

(defmacro xml> [#* code]
  `(hy.I.IPython/display.HTML (hy.R.hyml/macros.xml ~@code)))

(defmacro xhtml> [#* code]
  `(hy.I.IPython/display.HTML (hy.R.hyml/macros.xhtml ~@code)))

(defmacro xhtml5> [#* code]
  `(hy.I.IPython/display.HTML (hy.R.hyml/macros.xhtml5 ~@code)))

(defmacro html4> [#* code]
  `(hy.I.IPython/display.HTML (hy.R.hyml/macros.html4 ~@code)))

(defmacro html5> [#* code]
  `(hy.I.IPython/display.HTML (hy.R.hyml/macros.html5 ~@code)))

;----------------------------------------------------
; Indent xml code
; Works only with well defined root node xml content!
;----------------------------------------------------

(defn indent [xmldoc]
  (try
    (setv pretty (.toprettyxml (xml.dom.minidom.parseString xmldoc)))
    (except [e Exception]
      (raise (HyMLError (+ "indent needs well-formed xml with a single root node: "
                           (str e))))))
  ; minidom always adds its own xml declaration. drop it and restore
  ; the original one if the document had it
  (setv pretty (.join "\n" (cut (.splitlines pretty) 1 None)))
  (if (.startswith xmldoc "<?xml")
      (+ (cut xmldoc 0 (+ (.index xmldoc "?>") 2)) "\n" pretty)
      pretty))

;-----------------------------------------------------------------------
; List comprehension
; Use ordinary list and expression (list-comp expr args) arguments order
; vice versa: (list-comp* args expr). This serves as a kind of for each
; loop where list items and variables are introdused first, and then
; expression to handle each of items.
;-----------------------------------------------------------------------

; Hy 0.13 style list-comp kept for existing templates:
; (list-comp expr [x xs y ys] condition) -> (lfor x xs y ys :if condition expr)
(defmacro list-comp [expr bindings [condition None]]
  (if (is condition None)
      `(lfor ~@bindings ~expr)
      `(lfor ~@bindings :if ~condition ~expr)))

(defmacro list-comp* [bindings expr [condition None]]
  (if (is condition None)
      `(lfor ~@bindings ~expr)
      `(lfor ~@bindings :if ~condition ~expr)))
