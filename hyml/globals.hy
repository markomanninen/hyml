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

(eval-and-compile
  ; without eval-and-compile setv variables doesn't work as a global variable for macros
  (setv variables {})
  (defclass HyMLError [Exception]))

; for example: (defvar x 1 y 2 z 3)
(defmacro defvar [&rest args]
  ; cast tuple to list to make removal of list items work
  (setv args (list args))
  ; only even number of arguments are accepted
  (if (even? (len args))
      (do
        (setv rtrn (second args))
        (while (pos? (len args))
             (do
               ; update dictionary key with a value
               (assoc variables (first args) (second args))
               ; remove first two arguments (key-value pair)
               (.remove args (get args 0))
               (.remove args (get args 0))))
        rtrn)
      (raise (HyMLError "defvar needs an even number of arguments"))))
