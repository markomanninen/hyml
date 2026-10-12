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

;-------------------------------------------------------------
; Registry of variables and functions available to unquoted
; code (~ and ~@) inside ML macros and templates
;-------------------------------------------------------------
; markup is rendered at macro-expansion time, so values are
; evaluated and stored at compile time as well. they are compiled in the
; calling module, so functions can use the macros it has required (ml, ...)
(import hyml.core [variables-and-functions HyMLError namespace])

; for example: (defvar x 1 y 2 z 3)
; later values may refer to earlier ones: (defvar a 1 b (+ a 1))
(defmacro defvar [_hy_compiler #* args]
  (when (% (len args) 2)
    (raise (HyMLError "defvar needs an even number of arguments")))
  (for [i (range 0 (len args) 2)]
    (setv (get variables-and-functions (hy.mangle (get args i)))
          (hy.eval (get args (+ i 1)) (namespace) :module _hy_compiler.module)))
  None)

; for example: (deffun wholename (fn [x y] (+ y ", " x)))
(defmacro deffun [_hy_compiler name func]
  (setv (get variables-and-functions (hy.mangle name))
        (hy.eval func (namespace) :module _hy_compiler.module))
  None)
