#!/usr/bin/python3
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
; (require (hyml.minimal (*)))
; 
; Usage:
; (ml (tag :attr "value" (sub "Content"))) ->
; <tag attr="value"><sub>Content</sub></tag>
; 
; Author: Marko Manninen <elonmedia@gmail.com>
; Copyright: Marko Manninen (c) 2017
; Licence: MIT
;----------------------------------------------

; global registry for variables and functions
(require (hyml.variables (defvar deffun)))
(import (hyml.variables (variables-and-functions)))
; some helpers
(require (hyml.helpers (println ml> list-comp*)))
(import (hyml.helpers (indent)))

(try
  ; needed for Jupyter Notebook ml> render helper
  ; but it is optional only for the main codebase
  (import IPython)
  (except (e Exception)))

; eval and compile variables, constants and functions for ml, defvar, deffun, and include macros
(eval-and-compile
  ; internal constants
  (def **keyword** "keyword") (def **unquote** "unquote")
  (def **splice** "unquote_splice") (def **unquote-splice** (, **unquote** **splice**))
  (def **quote** "quote") (def **quasi** "quasiquote")
  (def **quasi-quote** (, **quote** **quasi**))
  ; given two dicts, merge them into a new dict as a shallow copy.
  (defn merge-two-dicts [x y]
    (if-not (or (empty? x) (empty y))
            ; tiny optimization, if there is values in both x and y
            (do (setv z (.copy x)) (.update z y) z)
            ; else one more check to return the one that has values
            ; or maybe all were empty then x should be fine
            (if (empty? x) y x)))
  ; detach keywords and content from code expression
  (defn get-content-attributes [code &optional [vars-and-funcs {}]]
    (setv content [] attributes [] kwd None)
    (for [item code]
         (do (if (iterable? item)
                 ; should we evaluate keyword
                 (if (= (first item) **unquote**)
                     (setv item (eval (second item)
                                      (merge-two-dicts variables-and-functions vars-and-funcs)))
                     ; single pre-quoted symbols will get accepted
                     ; this is practically to make attribute value and content part 
                     ; coherent with create-tag functionality. without this
                     ; quotation symbols would be interpreted as tag names!
                     (in (first item) **quasi-quote**) (setv item (name (eval item)))))
             ; should we add item to content / attributes list
             (if-not (keyword? item)
               (if (none? kwd)
                   ; keyword was not set, so item must be a content
                   (.append content (parse-mnml item vars-and-funcs))
                   ; otherwise it is attribute
                   (.append attributes (, kwd (parse-mnml item vars-and-funcs)))))
             ; handle possible boolean attributes
             (if (and (keyword? kwd) (keyword? item))
                 (.append attributes (, kwd (name kwd))))
             ; should we regard next item as a values of the keyword?
             (if (keyword? item) (setv kwd item) (setv kwd None))))
    ; attributes without values are boolean attributes that
    ; has same value than the name of the attribute
    (if (keyword? kwd)
        (.append attributes (, kwd (name kwd))))
    (, content attributes))
  ; recursively parse expression. take optional variables and functions
  ; dictionary for eval functionality. note that ml macro does NOT
  ; support this, only parse-mnml direct function call
  (defn parse-mnml [code &optional [vars-and-funcs {}]]
    (if (coll? code)
        (do (setv tag (catch-tag (first code)))
            ; special processing for unquote and unquote-splice 
            (if (in tag **unquote-splice**)
                (if (= tag **unquote**)
                    ; must pass variables-and-functions functions so that
                    ; custom variables and functions are found in the namespace
                    (str (eval (second code) (merge-two-dicts variables-and-functions vars-and-funcs)))
                    ; process the list of code
                    (.join "" (map
                      ; if there are variables and functions we would like to pass them to parse function
                      ; else just simple parse-mnml map
                      (if (empty? vars-and-funcs) parse-mnml (fn [item] (parse-mnml item vars-and-funcs))) 
                          (eval (second code) 
                                (merge-two-dicts variables-and-functions vars-and-funcs)))))
                ; normal tag creation
                (do (setv (, content attributes) (get-content-attributes (drop 1 code) vars-and-funcs))
                    ; start tag with attributes
                    ; if there is no content, then we can use short tags
                    (+ (tag-start tag attributes (empty? content))
                       ; if there is no content, we dodn't need end tag
                       (if (empty? content) ""
                           (+ (.join "" (map str content)) (+ "</" tag ">")))))))
        ; returned value is always a string
        (if (none? code) "" (str code))))
  ; detach tag from expression
  (defn catch-tag [code]
    ; see if we should evaluate unquoted tag name
    (if (and (iterable? code) (= (first code) **unquote**))
        (eval (second code))
        ; otherwise try to catch the evaluated name
        (try (name (eval code))
             ; or just return the string representation of the tag
             (except (e Exception) (str code)))))
  ; concat attributes
  (defn tag-attributes [attr]
    (if (empty? attr) ""
        (+ " " (.join " " (list-comp
          ; get the name of the keyword and value symbols
          (% "%s=\"%s\"" (, (name kwd) (name value))) [[kwd value] attr])))))
  ; create start tag
  (defn tag-start [tag-name attr short]
    (+ "<" tag-name (tag-attributes attr) (if short "/>" ">"))))
; include functionality for template engine
(defmacro include [template]
  `(do (import [hy.importer [tokenize]])
       (with [f (open ~template)]
         ; content of the file must be wrapped with expression parentheses ()
         ; quasiquoted (`) and finally unquote-spliced (~@) so that
         ; final evaluation is done in the main parse-mnml loop
         (tokenize (+ "~@`(" (f.read) ")")))))
; main MiNiMaL macro to be used. passes code to parse-mnml
(defmacro ml [&rest code]
  ; with map multiple expressions, not only nested ones, can be processed
  (.join "" (map parse-mnml code)))
