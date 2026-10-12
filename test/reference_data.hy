;; Frozen copy of hyml/data.hy before the speed work (HyML 1.2.1). The
;; differential test renders random markup with this and with the current
;; implementation and requires identical results. Don't edit.

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

(import re html fnmatch functools)
(import urllib.parse [urlsplit])
(import hyml.core [HyMLError ->str keyword? head-name dotted-tag])
(import hyml.macros [dialects render spec void?])
(import reference-sexp [read :as read-sexp ReadError])

; the library's error class, so that both implementations compare the same way
(import hyml.data [HyMLDataError])

; heads that mean code in HyML. they are never tags in data mode
(setv code-heads (frozenset ["unquote" "unquote-splice" "quote" "quasiquote"]))
(setv reserved-names (| code-heads #{"."}))

; elements that can run scripts, load other documents or change how the
; page is interpreted. meta is allowed, its http-equiv attribute is not.
; tags and attributes listed explicitly in allowed_tags and
; allowed_attributes are allowed even when they are blocked here
(setv blocked-tags (frozenset ["script" "style" "iframe" "frame" "frameset" "object"
                               "embed" "applet" "base" "link" "noscript" "param"]))

; besides on* event handlers
(setv blocked-attributes (frozenset ["style" "srcdoc" "http-equiv" "ping"]))

(setv url-attributes (frozenset ["href" "src" "action" "formaction" "cite" "poster" "data"
                                 "background" "longdesc" "codebase" "manifest" "icon"
                                 "xlink:href"]))

(setv safe-schemes (frozenset ["http" "https" "mailto" "tel"]))

; URLs that browsers load without a click. a prompt injected agent can leak
; data in them (GitLab Duo, EchoLeak, CamoLeak), so in safe mode they must
; be relative or point to allowed_url_hosts
(setv resource-attributes (frozenset ["src" "srcset" "poster" "background" "data" "codebase"
                                      "manifest" "icon" "xlink:href"]))

; forms that post to another host are a phishing pattern, so their targets
; need allowed_url_hosts too
(setv form-attributes (frozenset ["action" "formaction"]))

(setv html-tag-name (re.compile r"[A-Za-z][A-Za-z0-9-]*"))
(setv xml-tag-name (re.compile r"[A-Za-z_][\w.-]*(?::[A-Za-z_][\w.-]*)?"))
(setv attribute-name (re.compile r"[A-Za-z_:][\w.:-]*"))
(setv max-problems 20)

; models are immutable, so the same tag symbol and attribute keyword can be
; shared. building them is costly, because Hy validates every name
(setv symbol (functools.cache hy.models.Symbol)
      keyword (functools.cache hy.models.Keyword))

(defn type-name [x]
  (. (type x) __name__))

(defclass Checker []
  "Turns markup data into HyML models with only tags, attributes and
  escaped text, collecting problems on the way."

  (defn __init__ [self dialect allowed-tags allowed-attributes allowed-url-hosts
                  allow-external-resources safe max-depth max-nodes]
    (when (not-in dialect dialects)
      (raise (ValueError (+ "dialect must be one of: " (.join ", " dialects)))))
    (setv self.dialect (get dialects dialect)
          self.specs (get self.dialect "specs")
          self.allowed-tags (when (is-not allowed-tags None)
                              (frozenset (gfor tag allowed-tags (.lower tag))))
          self.allowed-attributes (when (is-not allowed-attributes None) (list allowed-attributes))
          self.allowed-url-hosts (when (is-not allowed-url-hosts None)
                                   (frozenset (gfor host allowed-url-hosts (.lower host))))
          self.allow-external-resources allow-external-resources
          self.safe safe
          self.max-depth max-depth
          self.max-nodes max-nodes
          self.nodes 0
          self.problems []))

  (defn problem [self path message]
    (when (< (len self.problems) max-problems)
      (.append self.problems (if path (+ (.join " > " path) ": " message) message))))

  (defn text [self value]
    [(hy.models.String (html.escape value :quote False))])

  ;; HyML s-expression models

  (defn from-model [self node path depth]
    (cond
      (isinstance node hy.models.Expression) (self.model-element node path depth)
      (isinstance node #(hy.models.String hy.models.Symbol)) (self.text (str node))
      (isinstance node #(hy.models.Integer hy.models.Float)) (self.text (->str node))
      (keyword? node)
      (do (self.problem path (% "attribute :%s is outside an element" #(node.name))) [])
      True
      (do (self.problem path (% "%s is not markup. Use text or (tag ...)" #((type-name node)))) [])))

  (defn model-element [self node path depth]
    (setv head (when node (get node 0))
          name (cond (isinstance head #(hy.models.Symbol hy.models.String)) (str head)
                     (= (head-name head) ".") (dotted-tag head)
                     True None))
    (cond
      (not node)
      (do (self.problem path "empty element ()") [])
      (or (in (head-name node) code-heads) (in (head-name head) code-heads))
      (do (self.problem path "~, ~@, ' and ` are code, which is not allowed in markup data") [])
      (is name None)
      (do (self.problem path (% "the tag name must be a symbol or a string, not %s" #((type-name head)))) [])
      True
      (do
        (setv attributes [] children [] items (list (cut node 1 None)) i 0)
        (while (< i (len items))
          (setv item (get items i))
          (if (keyword? item)
              (do
                (setv next-item (when (< (+ i 1) (len items)) (get items (+ i 1))))
                (if (isinstance next-item #(hy.models.String hy.models.Symbol hy.models.Integer hy.models.Float))
                    (do (.append attributes #(item.name (->str next-item))) (+= i 2))
                    ; a keyword without a value is a boolean attribute
                    (do (.append attributes #(item.name True)) (+= i 1))))
              (do (.append children item) (+= i 1))))
        (self.element name attributes children self.from-model path depth))))

  ;; JSON Hiccup data

  (defn from-data [self node path depth]
    (cond
      (isinstance node bool)
      (do (self.problem path (% "%s is not markup. Use a string" #(node))) [])
      (isinstance node str) (self.text node)
      (isinstance node #(int float)) (self.text (str node))
      (is node None) []
      (and (isinstance node #(list tuple)) node (isinstance (get node 0) str))
      (self.data-element node path depth)
      ; a list of nodes is a fragment
      (isinstance node #(list tuple))
      (lfor [i child] (enumerate node)
            model (self.from-data child (+ path [(str (+ i 1))]) depth)
            model)
      True
      (do (self.problem path (% "%s is not markup. Use a string or [tag, {attributes}, ...children]"
                                #((type-name node))))
          [])))

  (defn data-element [self node path depth]
    (setv rest (list (cut node 1 None))
          attributes [])
    (when (and rest (isinstance (get rest 0) dict))
      (for [[name value] (.items (.pop rest 0))]
        (cond
          (or (is value None) (is value False)) None
          (is value True) (.append attributes #((str name) True))
          (and (isinstance value #(str int float)) (not (isinstance value bool)))
          (.append attributes #((str name) (str value)))
          ; ["a", "b"] for class lists
          (and (isinstance value #(list tuple)) (all (gfor v value (isinstance v str))))
          (.append attributes #((str name) (.join " " value)))
          True
          (self.problem (+ path [(get node 0)])
                        (% "attribute %s has a %s value. Use a string, a number, true or a list of strings"
                           #(name (type-name value)))))))
    (self.element (get node 0) attributes rest self.from-data path depth))

  ;; checks shared by both formats

  (defn element [self name attributes children convert path depth]
    ; a number at the end of the path is the position of this element
    (setv path (if (and path (.isdigit (get path -1)))
                   (+ (cut path -1) [(% "%s[%s]" #(name (get path -1)))])
                   (+ path [name]))
          html-like (is-not self.specs None))
    (+= self.nodes 1)
    (cond
      (= self.nodes (+ self.max-nodes 1))
      (do (self.problem path (% "more than max_nodes=%d elements" #(self.max-nodes))) (return []))
      (> self.nodes self.max-nodes) (return [])
      (> depth self.max-depth)
      (do (self.problem path (% "nested deeper than max_depth=%d" #(self.max-depth))) (return [])))
    ; div#main.note shorthand in the (x)html dialects
    (setv [tag ids classes] (if html-like (split-shorthand name) #(name [] [])))
    (when ids (setv attributes (merge attributes "id" ids)))
    (when classes (setv attributes (merge attributes "class" classes)))
    (setv ok (self.check-tag tag path))
    (setv attribute-models
          (lfor [attribute value] attributes
                :if (self.check-attribute tag attribute value path)
                model [(keyword attribute)
                       (hy.models.String (if (is value True)
                                             attribute
                                             (html.escape value :quote True)))]
                model))
    (setv child-models
          (lfor [i child] (enumerate children)
                model (convert child (+ path [(str (+ i 1))]) (+ depth 1))
                model))
    (when (and ok html-like (void? tag self.specs) child-models)
      (self.problem path (% "<%s> is a void element and can't have content" #(tag))))
    (if ok
        [(hy.models.Expression [(symbol tag) #* attribute-models #* child-models])]
        []))

  (defn check-tag [self tag path]
    (setv lower (.lower tag)
          pattern (if self.specs html-tag-name xml-tag-name))
    (cond
      (or (in lower reserved-names) (not (.fullmatch pattern tag)))
      (do (self.problem path (% "%r is not a valid tag name" #(tag))) False)
      (and self.specs (is (spec tag self.specs) None))
      (do (self.problem path (% "<%s> is not an %s element" #(tag (get self.dialect "name")))) False)
      (and self.safe (in lower blocked-tags)
           (or (is self.allowed-tags None) (not-in lower self.allowed-tags)))
      (do (self.problem path (% "<%s> is not allowed in safe mode, because it can run scripts or load content"
                                #(tag)))
          False)
      (and (is-not self.allowed-tags None) (not-in lower self.allowed-tags))
      (do (self.problem path (% "<%s> is not in the allowed tags: %s"
                                #(tag (.join ", " (sorted self.allowed-tags)))))
          False)
      True True))

  (defn check-attribute [self tag attribute value path]
    (setv lower (.lower attribute))
    (cond
      (not (.fullmatch attribute-name attribute))
      (do (self.problem path (% "%r is not a valid attribute name" #(attribute))) False)
      (and self.safe (or (.startswith lower "on") (in lower blocked-attributes))
           (or (is self.allowed-attributes None) (not-in lower self.allowed-attributes)))
      (do (self.problem path (% "attribute %s is not allowed in safe mode" #(attribute))) False)
      (and (is-not self.allowed-attributes None)
           (not (any (gfor pattern self.allowed-attributes (fnmatch.fnmatchcase lower pattern)))))
      (do (self.problem path (% "attribute %s is not in the allowed attributes: %s"
                                #(attribute (.join ", " self.allowed-attributes))))
          False)
      (and (isinstance value str) (or (in lower url-attributes) (= lower "srcset")))
      (all (lfor url (if (= lower "srcset")
                         (gfor candidate (.split value ",") :if (.strip candidate)
                               (get (.split (.strip candidate)) 0))
                         [value])
                 (self.check-url tag attribute url path)))
      True True))

  (defn check-url [self tag attribute url path]
    ; browsers ignore whitespace and control characters inside the scheme
    (setv cleaned (re.sub r"[\x00-\x20]+" "" (html.unescape url))
          scheme (re.match r"([A-Za-z][A-Za-z0-9+.-]*):" cleaned)
          external (or (.startswith cleaned "//")
                       (and scheme (in (.lower (.group scheme 1)) #("http" "https"))))
          host (.lower (or (. (urlsplit cleaned) hostname) "")))
    (cond
      (and self.safe scheme (not-in (.lower (.group scheme 1)) safe-schemes))
      (do (self.problem path (% "%s=%r uses the %s: scheme. Use http, https, mailto, tel or a relative URL"
                                #(attribute url (.lower (.group scheme 1)))))
          False)
      (and (is-not self.allowed-url-hosts None) external (not-in host self.allowed-url-hosts))
      (do (self.problem path (if self.allowed-url-hosts
                                 (% "%s=%r points to a host that is not allowed: %s"
                                    #(attribute url (.join ", " (sorted self.allowed-url-hosts))))
                                 (% "%s=%r points to another site, and no external sites are allowed. Use a relative URL"
                                    #(attribute url))))
          False)
      (and self.safe external (is self.allowed-url-hosts None) (not self.allow-external-resources)
           (or (in (.lower attribute) resource-attributes)
               (and (= (.lower tag) "link") (= (.lower attribute) "href"))))
      (do (self.problem path (% (+ "%s=%r loads an external resource without a click, which can leak data. "
                                   "Use a relative URL, or allow the host with allowed_url_hosts")
                                #(attribute url)))
          False)
      (and self.safe external (is self.allowed-url-hosts None) (in (.lower attribute) form-attributes))
      (do (self.problem path (% (+ "%s=%r sends form data to another host. "
                                   "Use a relative URL, or allow the host with allowed_url_hosts")
                                #(attribute url)))
          False)
      True True)))

(defn split-shorthand [name]
  (setv parts (re.split r"([.#])" name))
  #((or (get parts 0) "div")
    (lfor i (range 1 (len parts) 2) :if (and (= (get parts i) "#") (get parts (+ i 1))) (get parts (+ i 1)))
    (lfor i (range 1 (len parts) 2) :if (and (= (get parts i) ".") (get parts (+ i 1))) (get parts (+ i 1)))))

(defn merge [attributes name values]
  (setv value (.join " " values))
  (for [[i [key old]] (enumerate attributes)]
    (when (= key name)
      (return (+ (cut attributes i) [#(key (if (is old True) value (+ old " " value)))]
                 (cut attributes (+ i 1) None)))))
  (+ [#(name value)] attributes))

(defn check-data [source [dialect "html5"] * [allowed-tags None] [allowed-attributes None]
                  [allowed-url-hosts None] [allow-external-resources False] [safe True]
                  [max-depth 64] [max-nodes 10000]]
  "Check markup data. Returns #(models problems)."
  (setv checker (Checker dialect allowed-tags allowed-attributes allowed-url-hosts
                         allow-external-resources safe max-depth max-nodes))
  (cond
    ; s-expression text is read as plain lists, with HyML's own small reader
    (isinstance source str)
    (do (setv [nodes read-problems]
              (try (read-sexp source)
                   (except [e ReadError] (raise (HyMLDataError [(str e)])))))
        (.extend checker.problems read-problems)
        ; a single form needs no position in the problem paths
        (setv models (if (= (len nodes) 1)
                         (checker.from-data (get nodes 0) [] 1)
                         (checker.from-data nodes [] 1))))
    ; quoted Hy code, like '(p "x")
    (isinstance source hy.models.Object)
    (setv models (checker.from-model source [] 1))
    True
    (setv models (checker.from-data source [] 1)))
  #(models (cut checker.problems max-problems)))

(defn validate-data [source [dialect "html5"] #** options]
  "List the problems in markup data. An empty list means it renders."
  (try
    (get (check-data source dialect #** options) 1)
    (except [e HyMLDataError] e.problems)))

(defn render-data [source [dialect "html5"] #** options]
  "Render markup data without evaluating anything. Raises HyMLDataError
  listing every problem when the data is rejected."
  (setv [models problems] (check-data source dialect #** options))
  (when problems
    (raise (HyMLDataError problems)))
  (render dialect models :evaluation False))
