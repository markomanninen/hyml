;; -*- coding: utf-8 -*-
;;
;; Copyright (c) 2026 Marko Manninen
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


;-------------------------------------------------------------------------
; Safe data mode: render markup that comes from users or LLM agents
;-------------------------------------------------------------------------
; The ML macros evaluate ~ and ~@ code, so they must never see untrusted
; input. Data mode accepts markup as data only:
;
; - HyML s-expression text: "(p :class \"note\" \"Hello\")"
; - JSON Hiccup arrays: ["p", {"class": "note"}, "Hello"]
;
; Nothing is evaluated. Tag and attribute names are checked, text and
; attribute values are escaped, and in safe mode (the default) elements and
; attributes that can run scripts or load content, URLs with other than
; http, https, mailto and tel schemes, and external URLs that load without a
; click (images, media) are rejected. All problems are
; collected into one HyMLDataError, with the path to each, so that an agent
; can correct its markup in one go.
;
; (render-data "(ul (li \"one\") (li \"two\"))")  -> "<ul><li>one<li>two</ul>"

; the implementation is in hyml/datamode.py
(import hyml.datamode [HyMLDataError check-data validate-data render-data])
