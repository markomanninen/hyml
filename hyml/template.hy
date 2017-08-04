#!/usr/bin/python3
;; -*- coding: utf-8 -*-
;;
;; Copyright (c) 2017 Marko Manninen
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
; Template functionality
;
; Utilizing render-template and extend-template
;----------------------------------------------
(require (hyml.minimal (*)))
(import (hyml.minimal (*)))

; template dir setter. this could be retrieved OR set
; from other modules too
(def template-dir "templates/")

; return / chain extended list rather than extending in-place (.extend)
(defn extend [a b] (.extend a b) a)

; should take previus variables and pass them to the next template
; globals are automaticly added, locals should be added with dictinary
; or (locals) / (vars)
; (setv variable "click")
; (render-template "index.hyml" (locals))
(defn render-template [tmpl &rest args]
  ; prefix template with dir
  (setv tmpl (+ template-dir tmpl))
  ; we want to get a recursive access to render-template function and
  ; extend-template macro to enable "extend" / blocks functionality in templates
  ; and all custom variables and functions set with deffun / defvar
  (setv vars (merge-two-dicts (globals) variables-and-functions))
  ; pass variables from arguments
  (for [d args] (setv vars (merge-two-dicts d vars)))
  ; next part is very similar to parse-mnml unquote-splice part
  (.join "" (map
    (fn [item] (parse-mnml item vars))
      ; include will return unquote-splice (~@) so we need to get over them to
      ; real content with first and second
      (eval (second  (first (include tmpl))) vars))))

; to imitate jinja and mako
; ~(extend-template "layout.hyml" {"var1" "val1" "var2" "val2"})
(defmacro extend-template [tmpl &rest args]
  `(if-not (empty? ~args)
            (do ; every value of the args dictionaries are getting ready to be evaluated
                ; via parse-mnml. they may or may not contain HyML code, but if HyML code
                ; is passed, it must be quasiquoted!
                (setv args (list-comp (fn [arg] (parse-mnml arg)) (list ~args)))
                ; pass variables and functions dictionaries to render-template function
                (apply render-template (extend (extend [~tmpl] ~args) [(globals)])))
            (render-template ~tmpl (globals))))

; beside render-template and extend-template, template macro can be used
; to pass expression and variables directly to the parse-mnml
; functionality instead of using file to read the expression
; usage: (template `(p ~var) {"var" 1}) -> <p>1</p>
; - one must quasiquote (`) the expression.
; - expression must have a single root node
; - dictionary of variables is optional and can be provided
;   as the first or the second argument
; - one argument is mandatory
; - if the only argument is empty string or dictionary None will be returned
(defmacro template [p1 &optional p2]
  ; detect if the first or the second is the dictionary or the expression
  (setv variables {})
  (if (isinstance p1 hy.HyDict)
      (do (setv variables p1) (setv args p2))
      (do (setv args p1)
          (if (isinstance p2 hy.HyDict)
              (setv variables p2))))
  (if args
    ; merge dictionaries (local, global and variables-and-functions)
    `(do (setv variables (merge-two-dicts ~variables variables-and-functions))
         (setv variables (merge-two-dicts variables (globals)))
         ; quote before eval and parse evaluated expression
         (parse-mnml (eval (quote ~args) ~variables) ~variables))))
