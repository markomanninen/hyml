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
  ; but it is optional only for main codebase
  (import IPython)
  (except (e Exception)))

; eval and compile variables, constants and functions for ml, defvar, deffun, and include macros
(eval-and-compile
  ; internal constants
  (def **keyword** "keyword") (def **unquote** "unquote")
  (def **splice** "unquote_splice") (def **unquote-splice** (, **unquote** **splice**))
  ; detach keywords and content from code expression
  (defn get-content-attributes [code]
    (setv content [] attributes [] kwd None)
    (for [item code]
         (do (if (and (= (first item) **unquote**)
                      (= (first (second item)) **keyword**))
                 (setv item (eval (second item))))
             (if-not (keyword? item)
               (if (none? kwd)
                   (.append content (parse-mnml item))
                   (.append attributes (, kwd (parse-mnml item)))))
             (if (keyword? item) (setv kwd item) (setv kwd None))))
    (, content attributes))
  ; recursively parse expression
  (defn parse-mnml [code] 
    (if (coll? code)
        (do (setv tag (catch-tag (first code)))
            (if (in tag **unquote-splice**)
                (if (= tag **unquote**)
                    (str (eval (second code) variables-and-functions))
                    (.join "" (map parse-mnml (eval (second code) variables-and-functions))))
                (do (setv (, content attributes) (get-content-attributes (drop 1 code)))
                    (+ (tag-start tag attributes (empty? content))
                       (if (empty? content) ""
                           (+ (.join "" (map str content)) (+ "</" tag ">")))))))
        (if (none? code) "" (str code))))
  ; detach tag from expression
  (defn catch-tag [code]
    (if (and (iterable? code) (= (first code) **unquote**))
        (eval (second code))
        (try (name (eval code))
             (except (e Exception) (str code)))))
  ; concat attributes
  (defn tag-attributes [attr]
    (if (empty? attr) ""
        (+ " " (.join " " (list-comp
          (% "%s=\"%s\"" (, (name kwd) (name value))) [[kwd value] attr])))))
  ; create start tag
  (defn tag-start [tag-name attr short]
    (+ "<" tag-name (tag-attributes attr) (if short "/>" ">"))))
; include functionality for template engine
(defmacro include [template]
  `(do (import [hy.importer [tokenize]])
       (with [f (open ~template)]
         (tokenize (+ "~@`(" (f.read) ")")))))
; main MiNiMaL macro to be used. passes code to parse-mnml
(defmacro ml [&rest code]
  (.join "" (map parse-mnml code)))
