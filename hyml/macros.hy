#!/usr/bin/python3

;------------------------------------------------
; HyML - XML / (X)HTML generator for Hy language
;------------------------------------------------
; ALMOST ALL IN ONE EXAMPLE
; specify parser macro (ML macros): xml, xhtml, xhtml5, html4, or html5
;(xhtml5
;  ; text content. xml declaration could also be (?xml :version "1.0" :encoding "UTF-8")
;  "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
;  ; text content. doctype could also be (!DOCTYPE "html")
;  "<!DOCTYPE html>"
;  ; define tag name as the first parameter
;  ; define attributes by keywords
;  (html :lang "en" :xmlns "http://www.w3.org/1999/xhtml"
;    ; define nested tags and content by similar manner
;    (head
;      ; everything else except the first parameter and keywords are
;      ; regarded as inner html content
;      (title "Page title"))
;    (body
;      ; text content. comments could also be (!-- "comments")
;      "<!-- body starts here -->"
;      ; short notation for div element and class attribute <div class=""/>
;      ; note: main-container will be main_container!
;      (.main-container
;         ; short notation for class attribute <h1 class=""/>
;         ; with multiple dot notation classes are concatenated with space
;         ; so .main.header becomes: class="main header"
;         ; unquote macro with ~ to execute normal hy code
;         ; after unquted expression rest of the code is parsed by ML macros
;         (h1.main.header ~(.capitalize "page header"))
;         ; short notation for id attribute <ul id=""/>
;         ; you should not use joined #main#sub similar to class notation althought it is not prohibited
;         ; this is because id="main sub" is not a good id according to html attribute specifications
;         (ul#main "List"
;           ; unquote splice processes lists and concatenates results
;           ; list-comp* is a slightly modified vesion of list-comp
;           ; in list-comp* list argument is the first and expression
;           ; the second argument. in list-comp those arguments are in reverse order
;           ~@(list-comp* [i [1 2 3]] `(li ~i)))))))
;----------------------------------------------------
(require (hyml.globals (*)))
(import (hyml.globals (variables HyMLError)))
(import (hyml.specs (specs4 specs5 specs boolean-attributes
                     optional-start-tags optional-end-tags)))

(try
  ; needed for xml render helpers
  (import IPython)
  (except (e Exception)))

(eval-and-compile

  ;(defclass HyMLError [Exception])

  (defn append [lst val] (.append lst val) lst)
  (defn insert [lst idx val] (.insert lst idx val) lst)

  ; find keyword from code and return it plus possible value if available
  ; used to handle # and . special notation in (x)html
  (defn find-keyword [kwd code]
    (try
      ; set default value
      (setv key-value None
            key-index (.index code (keyword kwd)))
      (except (e Exception)
        ; .index raises exception if not found, set key to None in that case
        (setv key-index None)))
    ; if key is None then value is None too
    (if-not (none? key-index)
      (try
        ; try to find out value
        (setv key-value (get code (inc key-index)))
        (except (e Exception)
          ; get might raise list out of range error, which means
          ; there is a single key, but no value on the expression
          (setv key-value None))))
    ; return value as a list
    [key-index key-value])

  ; append keyword and value to the code expression
  ; used to handle # and . special notation in (x)html
  (defn append-keyword [kwd value code]
    (do
      ; find key index and possible value
      (setv (, idx key-value) (find-keyword kwd code))
      ; if keyword index was found
      (if-not (none? idx)
              (do
                ; if old value existed then remove it
                (if-not (none? key-value)
                        (.pop code (inc idx)))
                ; after removal insert new value on the place
                (.insert code (inc idx)
                  ; new value concatenated to the old value, if values are different
                  (if-not (none? key-value)
                          (if (or (= key-value value) (empty? value))
                              key-value
                              (% "%s %s" (, key-value value)))
                          ; else if there was no previous value
                          ; or it was same with a new one then add just the value
                          value)))
              ; else append new keyword and value to the code expression
              (do
                (append code (keyword kwd))
                (append code value)))
      ; return possibly modified code expression
      code))

  ; minify attributes, if they are single items without content
  ; (textarea :disabled) -> <textarea disabled="disabled"></textarea>
  (defmacro defgets [name minify if-code]
    `(defn ~name [code parent-tag]
      (setv content []
            attributes []
            key None)
      (for [[idx item] (enumerate code)]
           (do
             ~if-code
             (if (keyword? item)
                 (setv key item)
                 (setv key None))))
      (, content attributes)))

  ; parser-wise content and attribute getter
  (defmacro defget [name parser &optional [minify False]]
    `(defgets ~name ~minify
      (if-not (none? key)
              ; get attributes from argument set.
              ; every other item could be a key and value. for example
              ; "content" :key value "more content" :key2 value2
              ; would make attributes [(, key value) (, key2 value2)]
              (if-not (keyword? item)
                      (.append attributes (, (name key) item)))
              ; get attributes from argument set.
              ; every other item could be a key and value. for example
              ; "content" :key value "more content" :key2 value2
              ; in this case would make content:
              ; ["content" "more content"]
              (if-not (or (keyword? key) (keyword? item))
                      (.append content
                        (if (coll? item)
                            (~parser item code idx parent-tag)
                            item))))))

  ; (get-content-attributes '(1 :k "x" 2 :l "y" 3))
  ; -> ([1, 2, 3], [('k', 'x'), ('l', 'y')])
  ; passes parser for recursive content creation
  (defget get-content-attributes parse-xml)
  (defget get-content-attributes4 parse-html4 True)
  (defget get-content-attributes5 parse-html5 True)
  (defget get-content-attributesx parse-xhtml)
  (defget get-content-attributes5x parse-xhtml5)

  ; (setv (, code tag) (get-code-tag [code tag "." "class"]))
  ; (setv (, code tag) (get-code-tag [code tag "#" "id"]))
  (defn get-code-tag [code tag separator e]
    (do
      (setv params (.split tag separator))
      [(append-keyword e (.join " " (drop 1 params)) code)
       (hy.HySymbol (if (empty? (first params)) "div" (first params)))]))
  ; main parser loop
  ; get-content-attributes function calls back here so that recursive
  ; code generation becomes possible
  (defmacro defparse [name do-code get-content-attributes &optional [pre-code ""]]
    `(defn ~name [code &optional [parent None] [idx 0] [parent-tag None]] (if (coll? code)
      (do
        (setv tag (catch-tag (first code)))
        ; tag modifications in (x)html parsers for # and . special handlers
        ~pre-code
        ; content and attributes are not needed when unquote or unquote_splice are called
        (if-not (in tag (, "unquote" "unquote_splice"))
                (setv (, content attributes) (~get-content-attributes (list (drop 1 code)) tag)))
        ; note: hy transforms - to _
        (if ; comment tag <!-- -->
            ; can be written as a plain text also: (body "<!-- comments... -->")
            ; actual notation looks a little bit silly: (!-- "comments")
            ; so this case is likely to be removed as a redundant case
            (= tag "!__")
            (+ "<!--" (tag-content content) "-->")
            ; xml document start tag
            (= tag "?xml")
            (+ "<?xml" (concat-attributes attributes) "?>")
            ; doctype code block is special because tag content is placed inside start tag
            ; plus start tag is not in short form althought end tag is not rendered, which
            ; is a little bit similar to col tag.
            ; (!DOCTYPE html) => <!DOCTYPE html>
            ; (!DOCTYPE note SYSTEM \"Note.dtd\") => <!DOCTYPE note SYSTEM "Note.dtd">
            ; this could also be generated by plain text, so these two cases might be an overkill..
            (= tag "!DOCTYPE")
            (+ "<!DOCTYPE " (tag-content content) ">")
            ; unquoting code. this means that one can change from html* macro mode
            ; to the normal lisp evaluation mode:
            ; (html* ~(+ 1 1)) -> (html* (unquote (+ 1 1)))
            ; unquote part of the code is untouched, but second part of  the code is evaluated
            ; thus becoming: (str (eval (+ 1 1))) -> "2"
            (= tag "unquote") (str (eval (second code) variables))
            ; ~@ is used to concat lists. ~name function is called recursively
            ; to evaluate the content. works similarly with unquote but in this case
            ; list of recursively parsed strings are joined together. this case handles
            ; both ~@(list-comp) and ~@(list-comp*) functions or any other similar list
            ; creation function
            (= tag "unquote_splice")
            (.join "" (map ~name (eval (second code) variables)))
            ~do-code))
      ; return code as a string because html is practically just a stream of text
      (if-not (none? code) (str code) ""))))

  ; default xml parser
  (defparse parse-xml
    (+ (tag-start tag attributes (empty? content))
       (if-not (empty? content)
               (+ (tag-content content) (tag-end tag))
                "")) get-content-attributes)
  ; is permitted tag
  (defn tag? [tag specs] (in (keyword (.lower (str tag))) specs))
  ; tag specifications
  (defn tag-specs [tag specs] (get specs (keyword (.lower (str tag)))))
  ; omit end tag
  (defn omit? [tag specs] (get (tag-specs tag specs) :omit))
  ; forbidden end tag
  (defn forbidden? [tag specs] (get (tag-specs tag specs) :forbidden))
  ; optional end tag
  (defn optional? [tag &optional [idx 0] [parent None] [parent-tag None]]
    (if (in (keyword tag) optional-end-tags)
        ((get optional-end-tags (keyword tag)) {
              :followed-by (if (and (not (none? parent)) (< (inc idx) (len parent)))
                               (keyword (first (get parent (inc idx))))
                               None)
              :is-last-child (and (not (none? parent))
                                  (= (inc idx) (len parent)))
              :parent (if (none? parent-tag) None (keyword parent-tag))}) False))

  ; html and xhtml parsers
  (defmacro defparser [parser specs get-content-attributes e do-tag]
    `(defparse ~parser
      (if (tag? tag ~specs)
          ~do-tag
          (do (raise (HyMLError (% "Tag name '%s' not meeting %s specifications." (, tag ~e))))
              ""))
      ; get content and attributes function
      ~get-content-attributes
      ; tag modifications in (x)html parsers for # and . special handlers
      (do
        ; #id will be available via dispatch_reader_macro expression
        ; that needs to be specially processed
        (if (= (first tag) "dispatch_reader_macro")
            (setv tag (+ "#" (.join "" (drop 1 (first (take 1 code)))))))
        ; .content -> <div class="content"></div>
        ; #content -> <div id="content"></div>
        ; section.content -> <section class="content"></section>
        ; section#content -> <section id="content"></section>
        (if (in "." tag)
            (setv (, code tag) (get-code-tag code tag "." "class"))
            (in "#" tag)
            (setv (, code tag) (get-code-tag code tag "#" "id"))))))

  ; html parsers
  (defmacro defparsehtml [parser specs get-content-attributes e]
    `(defparser ~parser ~specs ~get-content-attributes ~e
      ; empty content will give a short tag
      (+ (tag-start tag attributes (empty? content) (omit? tag ~specs) True)
         (if (and (not (forbidden? tag ~specs)) (not (empty? content)))
             (+ (tag-content content)
                ; in html certain tags can be optional to save some bytes
                (if-not (optional? tag idx parent parent-tag) (tag-end tag) ""))
             ""))))

  ; xhtml parsers
  (defmacro defparsexhtml [parser specs get-content-attributes e]
    `(defparser ~parser ~specs ~get-content-attributes ~e
      ; empty content will give a short tag, omit not possible in xhtml
      ; attribute minimizing not possible either
      (+ (tag-start tag attributes (empty? content))
         (if (and (not (forbidden? tag ~specs)) (not (empty? content)))
             (+ (tag-content content) (tag-end tag))
             (not (empty? content))
             (tag-end tag)
             ""))))

  (defparsehtml parse-html4 specs4 get-content-attributes4 "html4")
  (defparsehtml parse-html5 specs5 get-content-attributes5 "html5")
  (defparsexhtml parse-xhtml specs4 get-content-attributesx "xhtml4")
  (defparsexhtml parse-xhtml5 specs5 get-content-attributes5x "xhtml5")

  ; create a tag from the first item of the expression
  ; first try to evaluate code, because there might be
  ; a calculated expression for the tag name, naive examples:
  ; "td" or (+ "t" "d") -> td
  ; but in case symbol td is used, it will raise a name errors
  ; which will cause that string representation of the symbol is
  ; returned on the except part
  (defn catch-tag [code]
    (try
      ; catch "'name' is not defined" errors
      (name (eval code))
      (except (e Exception) (eval 'code))))

  ; helpers for concat-attributes
  (defn name* [kwd]
    (str (eval 'kwd)))
  (defn as-attribute-keyword [kwd]
    (keyword (name* kwd)))
  (defn as-attribute-value [value]
    (str (if (= hy.HyExpression (type value)) (eval value variables) value)))

  ; transforms [(key value)] list to xml attribute list:
  ; key="value". both key and value part will be evaluated
  ; so that calculated expressions can be used for them
  ; NOTE: do to get-attributes behaviour key doesn't really support
  ; calculated expressions. but for value naive example is:
  ; (if (even? ~i) "even" "odd")
  ; in html4 and html5, but not in xhtml, attributes can be minimized
  ; if attribute is a boolean element. for example:
  ; <textarea readonly="readonly"></textarea> could simply be:
  ; <textarea readonly></textarea>
  (defn concat-attributes [attr &optional [minify False]]
    (if-not (empty? attr)
      (+ " " (.join " "
         (list-comp
           ; it is not possible to set key and value before
           ; if clause for undefined variable error, which I could not
           ; identify, why so. thus this part looks very messy code...
           (if (and minify
                    (in (as-attribute-keyword kwd) boolean-attributes)
                    (= (name* kwd) (as-attribute-value value)))
               (name* kwd)
               (% (if (and minify (not (in " " (as-attribute-value value))))
                      "%s=%s"
                      "%s=\"%s\"")
                  (, (name* kwd) (as-attribute-value value))))
           [[kwd value] attr])))
      ""))

  ; concat content list and cast all items to string
  (defn concat-content [content]
    (.join "" (map str content)))

  (defn tag-content [content]
    (if-not (none? content)
            (concat-content content)
             ""))

  ; create a start tag
  (defn tag-start [tag-name attr &optional [short False] [omit False] [minify False]]
    (+ "<" (str tag-name) (concat-attributes attr minify) (if (and short (not omit)) "/>" ">")))

  ; create end tag
  (defn tag-end [tag-name] (+ "</" (str tag-name) ">")))

; unicode Square Ml U+3396  is a shorthand for parsing tags. note that
; html* and similar macros will accept multiple expressions, not just
; an expression with a single root node
(defsharp ㎖ [code] (parse-xml code))

; parser creator
(defmacro defml [name parser]
  `(defmacro ~name [&rest code]
    (.join "" (map ~parser code))))

; default xml parser
(defml xml parse-xml)
; xhtml (1.0) is almost same as html4 and html5 but tags must be correctly closed
; for example <b> must be <b/> in xhtml. xhtml takes care of the html4 tag names
(defml xhtml parse-xhtml)
; same as xhtml, but xhtml5 takes care of the html5 tag names
(defml xhtml5 parse-xhtml5)
; strict set of html tag generator for html4
(defml html4 parse-html4)
; strict set of html tag generator for html5
(defml html5 parse-html5)

; use ordinary list and expression order (list-comp expr args)
; vice versa: (list-comp* args expr). this serves as a kind of for each
; loop where list items and variables are introdused first, and then
; expression to handle each of items
(defmacro list-comp* [args expr]
  `(list-comp ~expr ~args))

(defmacro include [template]
  `(do
    (import [hy.importer [tokenize]])
    (with [f (open ~template)]
      (tokenize (+ "~@`(" (f.read) ")")))))
