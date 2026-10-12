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

;----------------------------------------------
; Helpers shared by the MiNiMaL and ML parsers
;----------------------------------------------
; ML macros render markup at macro-expansion time, so everything here
; must exist at compile time too
(eval-and-compile

  (defclass HyMLError [Exception])

  ; global registry for variables and functions set by defvar and deffun
  (setv variables-and-functions {})

  (defn keyword? [x] (isinstance x hy.models.Keyword))

  ; tag expressions and spliced lists. strings are not collections here
  (defn coll? [x] (and (isinstance x #(list tuple)) (not (isinstance x str))))

  ; name of the symbol heading an expression: (unquote x) -> "unquote"
  (defn head-name [code]
    (when (and (isinstance code hy.models.Expression)
               code
               (isinstance (get code 0) hy.models.Symbol))
      (str (get code 0))))

  ; plain text of an atom. str of a numeric model gives its repr,
  ; and keywords should lose their colon
  (defn ->str [x]
    (cond (is x None) ""
          (keyword? x) x.name
          (isinstance x hy.models.Integer) (str (int x))
          (isinstance x hy.models.Float) (str (float x))
          (isinstance x hy.models.Complex) (str (complex x))
          True (str x)))

  ; Hy reads h1.main.header as (. h1 main header) and .main as (. None main).
  ; join them back to the shorthand string the (x)html parsers understand
  (defn dotted-tag [code]
    (.join "." (gfor part (cut code 1 None)
                 (if (= (str part) "None") "" (->str part)))))

  ; fresh namespace for evaluating unquoted code. the registry comes first
  ; and later dictionaries override earlier ones. keys are mangled so that
  ; {"first-name" ...} is found by ~first-name. hy must be a global, or
  ; functions defined in the namespace can't run quasiquoted code later
  (defn namespace [#* dicts]
    (setv ns (dict :hy hy #** variables-and-functions))
    (for [d dicts]
      (when d
        (for [[k v] (.items d)]
          (setv (get ns (hy.mangle (->str k))) v))))
    ns)

  ; evaluate code with macros looked up from the given module
  (defn eval-in [code module #* dicts]
    (hy.eval code (namespace #* dicts) :module module))

  ; tag name from the head of an expression. symbols and strings are names
  ; as such. ~(code) is evaluated, 'tag and `tag are unquoted
  (defn catch-tag [code evaluate]
    (setv head (head-name code))
    (cond (isinstance code hy.models.Symbol) (str code)
          (= head "unquote") (->str (evaluate (get code 1)))
          (in head #("quote" "quasiquote")) (->str (hy.eval code))
          (= head ".") (dotted-tag code)
          True (->str code)))

  ; result of unquoted code: keywords and expressions stay as code to be
  ; parsed further, everything else becomes text
  (defn unquoted [value]
    (if (or (keyword? value) (isinstance value hy.models.Expression))
        value
        (->str value)))

  ; evaluate ~ and ~@ items of a tag body. spliced lists are flattened in
  ; place, recursively, because include returns a splice itself
  (defn expand [items evaluate]
    (setv result [])
    (for [item items]
      (setv head (head-name item))
      (cond (= head "unquote-splice")
            (.extend result (expand (evaluate (get item 1)) evaluate))
            (= head "unquote")
            (.append result (unquoted (evaluate (get item 1))))
            True
            (.append result item)))
    result)

  ; quote an attribute value. & and < are left alone so that already
  ; escaped values and template placeholders keep working
  (defn escape-attribute [value]
    (.replace (str value) "\"" "&quot;")))
