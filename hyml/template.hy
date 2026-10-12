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
; Template functionality
;
; Utilizing render-template and extend-template
;----------------------------------------------
(require hyml.minimal *)
(import hyml.minimal *)
(import hyml.core [namespace])

; template dir setter. this could be retrieved OR set
; from other modules too: (setv hyml.template.template-dir "views/")
(setv template-dir "templates/")

; read a template file and evaluate it as a quasiquoted list of forms,
; so that ~ and ~@ inside the template are resolved from vars
(defn read-template [path vars]
  (with [f (open path :encoding "utf-8")]
    (setv forms (list (hy.read-many (.read f) :filename path))))
  (hy.eval (hy.models.Expression [(hy.models.Symbol "quasiquote")
                                  (hy.models.Expression forms)])
           vars
           :module "hyml.template"))

; globals are automaticly added, locals should be added with dictionary
; or (locals) / (vars). later dictionaries override earlier ones:
; (setv variable "click")
; (render-template "index.hyml" (locals))
(defn render-template [tmpl #* args]
  ; we want to get a recursive access to render-template function and
  ; extend-template macro to enable "extend" / blocks functionality in templates
  ; and all custom variables and functions set with deffun / defvar
  (setv vars (namespace (globals) #* args))
  (.join "" (gfor item (read-template (+ template-dir tmpl) vars)
              (parse-mnml item vars))))

; to imitate jinja and mako
; ~(extend-template "layout.hyml" {"var1" "val1" "var2" "val2"})
; the namespace of the calling template is passed on, and the given
; dictionaries override it. values may be quasiquoted HyML code
(defmacro extend-template [tmpl #* args]
  `(render-template ~tmpl (globals) ~@args))

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
(defmacro template [p1 [p2 None]]
  ; detect if the first or the second is the dictionary or the expression
  (setv [expr variables] (if (isinstance p1 hy.models.Dict) [p2 p1] [p1 p2]))
  (when (and expr (not (isinstance expr hy.models.Dict)))
    ; caller's globals, then the given variables
    `(hy.I.hyml/template.render-expression (quote ~expr) (globals) ~(or variables {}))))

(defn render-expression [expr #* dicts]
  (setv vars (namespace #* dicts))
  (parse-mnml (hy.eval expr vars :module "hyml.template") vars))
