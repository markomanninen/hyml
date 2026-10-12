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
; HyML MiNiMaL
;
; Minimal Markup Language generator in Hy
;
; Source:
; https://github.com/markomanninen/hyml/
;
; Install:
; $ pip install hyml
;
; Import macros:
; (require hyml.minimal *)
;
; Usage:
; (ml (tag :attr "value" (sub "Content"))) ->
; <tag attr="value"><sub>Content</sub></tag>
;
; Author: Marko Manninen <elonmedia@gmail.com>
; Copyright: Marko Manninen (c) 2017-2026
; Licence: MIT
;----------------------------------------------

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
