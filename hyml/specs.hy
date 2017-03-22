#!/usr/bin/python3

;--------------------------------------------------------------
; HTML4 / HTML5 spesifications
; forbidden and optional end tags
; plus boolean attributes for minimizing generated code length
;--------------------------------------------------------------

; https://www.w3schools.com/TAGs/default.asp
; http://www.w3.org/TR/html401/index/elements.html
; http://www.w3.org/TR/html5/syntax.html#optional-tags
; https://en.wikipedia.org/wiki/XHTML
; https://html.spec.whatwg.org/multipage/syntax.html#optional-tags
; https://www.w3schools.com/tags/tag_doctype.asp

;----------------------
; HTML4 spesifications
;----------------------

(setv specs4 {
  :a {:title "Anchor" :forbidden False :omit False}
  :abbr {:title "Abbreviation" :forbidden False :omit False}
  :acronym {:title "Acronym" :forbidden False :omit False}
  :address {:title "Address" :forbidden False :omit False}
  :applet {:title "Java applet" :forbidden False :omit False}
  :area {:title "Image map region" :forbidden True :omit True}
  :b {:title "Bold text" :forbidden False :omit False}
  :base {:title "Document base URI" :forbidden True :omit True}
  :basefont {:title "Base font change" :forbidden True :omit False}
  :bdo {:title "BiDi override" :forbidden False :omit False}
  :big {:title "Large text" :forbidden False :omit False}
  :blockquote {:title "Block quotation" :forbidden False :omit False}
  :body {:title "Document body" :forbidden False :omit False}
  :br {:title "Line break" :forbidden True :omit True}
  :button {:title "Button" :forbidden False :omit False}
  :caption {:title "Table caption" :forbidden False :omit False}
  :center {:title "Centered block" :forbidden False :omit False}
  :cite {:title "Citation" :forbidden False :omit False}
  :code {:title "Computer code" :forbidden False :omit False}
  :col {:title "Table column" :forbidden True :omit True}
  :colgroup {:title "Table column group" :forbidden False :omit False}
  :dd {:title "Definition description" :forbidden False :omit False}
  :del {:title "Deleted text" :forbidden False :omit False}
  :dfn {:title "Defined term" :forbidden False :omit False}
  :dir {:title "Directory list" :forbidden False :omit False}
  :div {:title "Generic block-level container" :forbidden False :omit False}
  :dl {:title "Definition list" :forbidden False :omit False}
  :dt {:title "Definition term" :forbidden False :omit False}
  :em {:title "Emphasis" :forbidden False :omit False}
  :fieldset {:title "Form control group" :forbidden False :omit False}
  :font {:title "Font change" :forbidden False :omit False}
  :form {:title "Interactive form" :forbidden False :omit False}
  :frame {:title "Frame" :forbidden True :omit False}
  :frameset {:title "Frameset" :forbidden False :omit False}
  :h1 {:title "Level-one heading" :forbidden False :omit False}
  :h2 {:title "Level-two heading" :forbidden False :omit False}
  :h3 {:title "Level-three heading" :forbidden False :omit False}
  :h4 {:title "Level-four heading" :forbidden False :omit False}
  :h5 {:title "Level-five heading" :forbidden False :omit False}
  :h6 {:title "Level-six heading" :forbidden False :omit False}
  :head {:title "Document head" :forbidden False :omit False}
  :hr {:title "Horizontal rule" :forbidden True :omit True}
  :html {:title "HTML document" :forbidden False :omit False}
  :i {:title "Italic text" :forbidden False :omit False}
  :iframe {:title "Inline frame" :forbidden False :omit False}
  :img {:title "Inline image" :forbidden True :omit True}
  :input {:title "Form input" :forbidden True :omit True}
  :ins {:title "Inserted text" :forbidden False :omit False}
  :isindex {:title "Input prompt" :forbidden True :omit False}
  :kbd {:title "Text to be input" :forbidden False :omit False}
  :label {:title "Form field label" :forbidden False :omit False}
  :legend {:title "Fieldset caption" :forbidden False :omit False}
  :li {:title "List item" :forbidden False :omit False}
  :link {:title "Document relationship" :forbidden True :omit True}
  :map {:title "Image map" :forbidden False :omit False}
  :menu {:title "Menu list" :forbidden False :omit False}
  :meta {:title "Metadata" :forbidden True :omit True}
  :noframes {:title "Frames alternate content" :forbidden False :omit False}
  :noscript {:title "Alternate script content" :forbidden False :omit False}
  :object {:title "Object" :forbidden False :omit False}
  :ol {:title "Ordered list" :forbidden False :omit False}
  :optgroup {:title "Option group" :forbidden False :omit False}
  :option {:title "Menu option" :forbidden False :omit False}
  :p {:title "Paragraph" :forbidden False :omit False}
  :param {:title "Object parameter" :forbidden True :omit True}
  :pre {:title "Preformatted text" :forbidden False :omit False}
  :q {:title "Short quotation" :forbidden False :omit False}
  :s {:title "Strike-through text" :forbidden False :omit False}
  :samp {:title "Sample output" :forbidden False :omit False}
  :script {:title "Client-side script" :forbidden False :omit False}
  :select {:title "Option selector" :forbidden False :omit False}
  :small {:title "Small text" :forbidden False :omit False}
  :span {:title "Generic inline container" :forbidden False :omit False}
  :strike {:title "Strike-through text" :forbidden False :omit False}
  :strong {:title "Strong emphasis" :forbidden False :omit False}
  :style {:title "Embedded style sheet" :forbidden False :omit False}
  :sub {:title "Subscript" :forbidden False :omit False}
  :sup {:title "Superscript" :forbidden False :omit False}
  :table {:title "Table" :forbidden False :omit False}
  :tbody {:title "Table body" :forbidden False :omit False}
  :td {:title "Table data cell" :forbidden False :omit False}
  :textarea {:title "Multi-line text input" :forbidden False :omit False}
  :tfoot {:title "Table foot" :forbidden False :omit False}
  :th {:title "Table header cell" :forbidden False :omit False}
  :thead {:title "Table head" :forbidden False :omit False}
  :title {:title "Document title" :forbidden False :omit False}
  :tr {:title "Table row" :forbidden False :omit False}
  :tt {:title "Teletype text" :forbidden False :omit False}
  :u {:title "Underlined text" :forbidden False :omit False}
  :ul {:title "Unordered list" :forbidden False :omit False}
  :var {:title "Variable" :forbidden False :omit False}})

; add key as a tag name
(for [[key set] (.items specs4)]
  (do
     (assoc set :html4 True)
     (assoc set :html5 True)
     (assoc set :name (name key))))

;----------------------
; HTML5 spesifications
;----------------------

(setv specs5 {
  :article {:title "Defines an article" :forbidden False :omit False}
  :aside {:title "Defines content aside from the page content" :forbidden False :omit False}
  :audio {:title "Defines sound content" :forbidden False :omit False}
  :bdi {:title "Isolates a part of text that might be formatted in a different direction from other text outside it" :forbidden False :omit False}
  :canvas {:title "Used to draw graphics, on the fly, via scripting (usually JavaScript)" :forbidden False :omit False}
  :datalist {:title "Specifies a list of pre-defined options for input controls" :forbidden False :omit False}
  :details {:title "Defines additional details that the user can view or hide" :forbidden False :omit False}
  :dialog {:title "Defines a dialog box or window" :forbidden False :omit False}
  :embed {:title "Defines a container for an external (non-HTML) application" :forbidden False :omit False}
  :figcaption {:title "Defines a caption for a <figure> element" :forbidden False :omit False}
  :figure {:title "Specifies self-contained content" :forbidden False :omit False}
  :footer {:title "Defines a footer for a document or section" :forbidden False :omit False}
  :header {:title "Defines a header for a document or section" :forbidden False :omit False}
  :keygen {:title "Defines a key-pair generator field (for forms)" :forbidden False :omit True}
  :main {:title "Specifies the main content of a document" :forbidden False :omit False}
  :mark {:title "Defines marked/highlighted text" :forbidden False :omit False}
  :menuitem {:title "Defines a command/menu item that the user can invoke from a popup menu" :forbidden False :omit False}
  :meter {:title "Defines a scalar measurement within a known range (a gauge)" :forbidden False :omit False}
  :nav {:title "Defines navigation links" :forbidden False :omit False}
  :output {:title "Defines the result of a calculation" :forbidden False :omit False}
  :picture {:title "Defines a container for multiple image resources" :forbidden False :omit False}
  :progress {:title "Represents the progress of a task" :forbidden False :omit False}
  :rp {:title "Defines what to show in browsers that do not support ruby " :forbidden False :omit False}
  :rt {:title "Defines an explanation/pronunciation of characters (for East Asian typography)" :forbidden False :omit False}
  :ruby {:title "Defines a ruby annotation (for East Asian typography)" :forbidden False :omit False}
  :section {:title "Defines a section in a document" :forbidden False :omit False}
  :source {:title "Defines multiple media resources for media elements (<video> and <audio>)" :forbidden True :omit True}
  :summary {:title "Defines a visible heading for a <details> element" :forbidden False :omit False}
  :time {:title "Defines a date/time" :forbidden False :omit False}
  :track {:title "Defines text tracks for media elements (<video> and <audio>)" :forbidden True :omit True}
  :video {:title "Defines a video or movie" :forbidden False :omit False}
  :wbr {:title "Defines a possible line-break" :forbidden True :omit True}})

; add key as a tag name
(for [[key set] (.items specs5)]
  (do
     (assoc set :html4 False)
     (assoc set :html5 True)
     (assoc set :name (name key))))

; next tags are not supported by html5 althought they are at html4
(setv specs5! (, 
  :tt :strike :noframes :frameset :frame :font :dir :center :big :basefont :applet :acronym))

; add html4 specs (except specs5!) to html5
(for [[key set] (.items specs4)]
  (if-not (in key specs5!)
          (assoc specs5 key set)
          ; change html5 flag to false if tag is in specs5! specs
          (assoc set :html5 False)))

; generate both html4 and html5 specs table
(setv specs {})

; first add html4 specs
(for [[key set] (.items specs4)]
  (assoc specs key set))

; then add html5 specs
(for [[key set] (.items specs5)]
  (if-not (in key specs)
          (assoc specs key set)))

; cast specs dict to ordered dict
(import [collections [OrderedDict]])
(setv specs (OrderedDict (sorted (.items specs))))

;--------------------
; Boolean attributes
;--------------------
; next boolean attributes can be minimized on html. 
; for example <input disabled="disabled"> will be just <input disabled>
; https://github.com/kangax/html-minifier/issues/63
(setv boolean-attributes (, 
  :allowfullscreen :async :autofocus :autoplay :checked :compact :controls :declare 
  :default :defaultchecked :defaultmuted :defaultselected :defer :disabled :draggable 
  :enabled :formnovalidate :hidden :indeterminate :inert :ismap :itemscope :loop :multiple 
  :muted :nohref :noresize :noshade :novalidate :nowrap :open :pauseonexit :readonly 
  :required :reversed :scoped :seamless :selected :sortable :spellcheck :translate 
  :truespeed :typemustmatch :visible))

;----------------------
; Optional end tags
; TODO: recheck rules!
;----------------------

(setv whitespaces (, u"\u0009" u"\u000A" u"\u000C" u"\u000D" u"\u0020")) ; ('\t', '\n', '\x0c', '\r', ' ')

(defn comment? [element]
  (or (= (.join "" (take 3 (name element))) "!--")
      (= (.join "" (take 4 (name element))) "<!--")))

(defn whitespace? [element]
  (and (not (none? element)) (in (name (first element)) whitespaces)))

; TODO: optional start tag rules and implementation in macros
; However, a start tag must never be omitted if it has any attributes.
(setv optional-start-tags {

; An html element's start tag may be omitted if the first thing inside the html element is not a comment.
  :html (fn [context] False)

; A head element's start tag may be omitted if the element is empty, or if the first thing inside the head element is an element.
  :head (fn [context] False)

; A body element's start tag may be omitted if the element is empty, or if the first thing inside the body element is not ASCII whitespace 
; or a comment, except if the first thing inside the body element is a meta, link, script, style, or template element.
  :body (fn [context] False)

; A colgroup element's start tag may be omitted if the first thing inside the colgroup element is a col element, and if the element is not 
; immediately preceded by another colgroup element whose end tag has been omitted. (It can't be omitted if the element is empty.)
  :colgroup (fn [context] False)

; A tbody element's start tag may be omitted if the first thing inside the tbody element is a tr element, and if the element is not immediately 
; preceded by a tbody, thead, or tfoot element whose end tag has been omitted. (It can't be omitted if the element is empty.)
  :tbody (fn [context] False)})

; TODO tests for all. Difference of :followed-by and :parent especially
(setv optional-end-tags {

; An html element's end tag may be omitted if the html element is not immediately followed by a comment.
:html (fn [context] (not (comment? (get context :followed-by))))

; A head element's end tag may be omitted if the head element is not immediately followed by ASCII whitespace or a comment.
:head (fn [context] (and (not (whitespace? (get context :followed-by)))
                         (not (comment? (get context :followed-by)))))

; A body element's end tag may be omitted if the body element is not immediately followed by a comment.
:body (fn [context] (not (comment? (get context :followed-by))))

; An li element's end tag may be omitted if the li element is immediately followed by another li element or if there is no more content in the parent element.
:li (fn [context] (or (in (get context :followed-by) (, :li))
                      (get context :is-last-child)))

; A dt element's end tag may be omitted if the dt element is immediately followed by another dt element or a dd element.
:dt (fn [context] (in (get context :followed-by) (, :dt :dd)))

; A dd element's end tag may be omitted if the dd element is immediately followed by another dd element or a dt element, 
; or if there is no more content in the parent element.
:dd (fn [context] (or (in (get context :followed-by) (, :dt :dd))
                      (get context :is-last-child)))

; A p element's end tag may be omitted if the p element is immediately followed by an address, article, aside, blockquote, details, div, dl, fieldset, 
; figcaption, figure, footer, form, h1, h2, h3, h4, h5, h6, header, hgroup, hr, main, menu, nav, ol, p, pre, section, table, or ul element, 
; or if there is no more content in the parent element and the parent element is an HTML element that is not an a, audio, del, ins, map, noscript, 
; or video element, or an autonomous custom element.
:p (fn [context]  (or (in (get context :followed-by) (, :address :article :aside :blockquote :details :div :dl :fieldset :figcaption
                                                        :figure :footer :form :h1 :h2 :h3 :h4 :h5 :h6 :header :hgroup :hr :main :menu
                                                        :nav :ol :p :pre :section :table :ul))
                      (and (get context :is-last-child)
                           (not (in (get context :parent) (, :a :audio :del :ins :map :noscript :video))))))

; An rt element's end tag may be omitted if the rt element is immediately followed by an rt or rp element, or if there is no more content in the parent element.
:rt (fn [context] (or (in (get context :followed-by) (, :rt tp))
                      (get context :is-last-child)))

; An rp element's end tag may be omitted if the rp element is immediately followed by an rt or rp element, or if there is no more content in the parent element.
:rp (fn [context] (or (in (get context :followed-by) (, :rt :rp))
                      (get context :is-last-child)))

; An optgroup element's end tag may be omitted if the optgroup element is immediately followed by another optgroup element, 
; or if there is no more content in the parent element.
:optgroup (fn [context] (or (in (get context :followed-by) (, :optgroup))
                            (get context :is-last-child)))

; An option element's end tag may be omitted if the option element is immediately followed by another option element, 
; or if it is immediately followed by an optgroup element, or if there is no more content in the parent element.
:option (fn [context] False)

; A colgroup element's end tag may be omitted if the colgroup element is not immediately followed by ASCII whitespace or a comment.
:colgroup (fn [context] (and (not (whitespace? (get context :followed-by)))
                             (not (comment? (get context :followed-by)))))

; A caption element's end tag may be omitted if the caption element is not immediately followed by ASCII whitespace or a comment.
:caption (fn [context] (and (not (whitespace? (get context :followed-by)))
                            (not (comment? (get context :followed-by)))))

; A thead element's end tag may be omitted if the thead element is immediately followed by a tbody or tfoot element.
:thead (fn [context] (in (get context :followed-by) (, :tbody :tfoot)))

; A tbody element's end tag may be omitted if the tbody element is immediately followed by a tbody or tfoot element, 
; or if there is no more content in the parent element.
:tbody (fn [context] (or (in (get context :followed-by) (, :tbody :tfoot))
                         (get context :is-last-child)))

; A tfoot element's end tag may be omitted if there is no more content in the parent element.
:tfoot (fn [context] (get context :is-last-child))

; A tr element's end tag may be omitted if the tr element is immediately followed by another tr element, or if there is no more content in the parent element.
:tr (fn [context] (or (in (get context :followed-by) (, :tr))
                      (get context :is-last-child)))

; A td element's end tag may be omitted if the td element is immediately followed by a td or th element, or if there is no more content in the parent element.
:td (fn [context] (or (in (get context :followed-by) (, :td :th))
                      (get context :is-last-child)))

; A th element's end tag may be omitted if the th element is immediately followed by a td or th element, or if there is no more content in the parent element.
:th (fn [context] (or (in (get context :followed-by) (, :td :th))
                      (get context :is-last-child)))})
