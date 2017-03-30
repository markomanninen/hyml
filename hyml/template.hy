#!/usr/bin/python3
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
  (setv vars (globals))
  ; pass variables from arguments
  (for [d args] (setv vars (merge-two-dicts d vars)))
  ; next part is very similar to parse-mnml unquote-splice part
  (.join "" (map
    (fn [item] (parse-mnml item vars))
      ; include will return unquote-splice (~@) so we need to get over them to
      ; real content with first and second
      (eval  (second  (first (include tmpl))) vars))))

; to imitate jinja and mako
; ~(extend-template "layout.hyml" {"var1" "val1" "var2" "val2"})
(defmacro extend-template [tmpl &rest args]
  `(if-not (empty? ~args)
            (do (setv args (list-comp (fn [arg] (parse-mnml arg)) (list ~args)))
                (apply render-template (extend (extend [~tmpl] ~args) [(globals)])))
            (render-template ~tmpl (globals))))
