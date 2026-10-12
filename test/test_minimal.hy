;; Tests for the MiNiMaL ml macro. Expected values come from the
;; executed notebook "HyML - Minimal.ipynb" and doc/tests.rst unless
;; noted otherwise.

(require hyml.minimal *)
(import hyml.minimal *)
(import pytest)

(defn test-empty []
  (assert (= (ml) ""))
  (assert (= (ml "") ""))
  (assert (= (ml ("")) "</>")))

(defn test-tag-names []
  (assert (= (ml (tag)) "<tag/>"))
  (assert (= (ml (TAG)) "<TAG/>"))
  (assert (= (ml (~(.upper "tag"))) "<TAG/>"))
  (assert (= (ml (~(+ "t" "a" "g"))) "<tag/>"))
  (assert (= (ml (tag "")) "<tag></tag>"))
  (assert (= [(ml ('tag)) (ml (`tag)) (ml (tag)) (ml ("tag"))] (* ["<tag/>"] 4)))
  (assert (= (ml (~"J")) "<J/>")))

(defn test-tag-names-are-not-evaluated []
  ; Hy 0.13 evaluated tag symbols first, so (J) became <1j/> and names of
  ; builtins depended on luck
  (assert (= (ml (J)) "<J/>"))
  (assert (= (ml (map (input) (object))) "<map><input/><object/></map>"))
  ; hyphens are no longer turned into underscores
  (assert (= (ml (my-tag)) "<my-tag/>"))
  (assert (= (ml (h1.title)) "<h1.title/>")))

(defn test-content []
  (assert (= (ml (tag "content")) "<tag>content</tag>"))
  (assert (= (ml (tag "CONTENT")) "<tag>CONTENT</tag>"))
  (assert (= (ml (tag ~(.upper "content"))) "<tag>CONTENT</tag>"))
  (assert (= [(ml (tag 'val)) (ml (tag `val)) (ml (tag val)) (ml (tag "val"))]
             (* ["<tag>val</tag>"] 4)))
  (assert (= (ml (tag 1 2.5)) "<tag>12.5</tag>"))
  (assert (= (ml (tag ~(+ "Generator inside: " (ml (sub "content")))))
             "<tag>Generator inside: <sub>content</sub></tag>")))

(defn test-attributes []
  (assert (= (ml (tag :attr "val")) "<tag attr=\"val\"/>"))
  (assert (= (ml (tag ~(hy.models.Keyword "attr") "val")) "<tag attr=\"val\"/>"))
  (assert (= (ml (tag ~(hy.models.Keyword (.join "" ["a" "t" "t" "r"])) "value"))
             "<tag attr=\"value\"/>"))
  (assert (= (ml (tag :attr "val" "")) "<tag attr=\"val\"></tag>"))
  (assert (= (ml (tag :attr "val" "content")) "<tag attr=\"val\">content</tag>"))
  (assert (= (ml (tag :ATTR "val")) "<tag ATTR=\"val\"/>"))
  (assert (= (ml (tag ~(hy.models.Keyword (.upper "attr")) "val")) "<tag ATTR=\"val\"/>"))
  (assert (= (ml (tag :attr "VAL")) "<tag attr=\"VAL\"/>"))
  (assert (= (ml (tag :attr ~(.upper "val"))) "<tag attr=\"VAL\"/>"))
  (assert (= (ml (tag :attr ~(+ "v" "a" "l" "u" "e"))) "<tag attr=\"value\"/>"))
  (assert (= [(ml (tag :attr 'val)) (ml (tag :attr `val)) (ml (tag :attr val)) (ml (tag :attr "val"))]
             (* ["<tag attr=\"val\"/>"] 4)))
  (assert (= (ml (tag :http-equiv "x")) "<tag http-equiv=\"x\"/>"))
  ; no space between attribute name and value as a string literal
  (assert (= (ml (tag :attr"val")) "<tag attr=\"val\"/>"))
  (assert (= (ml (tag :"attr")) "<tag =\"attr\"/>")))

(defn test-attribute-values-are-escaped []
  (assert (= (ml (tag :title "say \"hi\"")) "<tag title=\"say &quot;hi&quot;\"/>")))

(defn test-keyword-content []
  (assert (= [(ml (tag ':attr)) (ml (tag `:attr))] ["<tag>attr</tag>" "<tag>attr</tag>"])))

(defn test-boolean-attributes []
  (assert (= [(ml (tag :disabled)) (ml (tag ~(hy.models.Keyword "disabled"))) (ml (tag :disabled "disabled"))]
             (* ["<tag disabled=\"disabled\"/>"] 3)))
  (assert (= (ml (tag "Content" :disabled :enabled))
             "<tag disabled=\"disabled\" enabled=\"enabled\">Content</tag>"))
  (assert (= (ml (tag :attr1 :attr2)) "<tag attr1=\"attr1\" attr2=\"attr2\"/>"))
  (assert (= (ml (tag Content :attr1 :attr2)) "<tag attr1=\"attr1\" attr2=\"attr2\">Content</tag>"))
  (assert (= (ml (tag :attr1 :attr2 Content)) "<tag attr1=\"attr1\" attr2=\"Content\"/>"))
  (assert (= (ml (tag :attr :attr "attr2")) "<tag attr=\"attr\" attr=\"attr2\"/>")))

(defn test-weird []
  ; quote should not be unquoted or surpressed
  (assert (= (ml (quote :quote "quote" "quote")) "<quote quote=\"quote\">quote</quote>"))
  ; tag name, keyword name, value and content can be same
  (assert (= (ml (tag :tag "tag" "tag")) "<tag tag=\"tag\">tag</tag>"))
  ; multiple same attribute names stays in the markup in the reserved order
  (assert (= (ml (tag :attr "attr1" :attr "attr2")) "<tag attr=\"attr1\" attr=\"attr2\"/>")))

(defn test-nesting-and-multiple-roots []
  (assert (= (ml (tag (sub))) "<tag><sub/></tag>"))
  (assert (= (ml (p "a") (p "b")) "<p>a</p><p>b</p>")))

(defn test-unquote-splice []
  (assert (= (ml (tag ~@(lfor item [1 2 3] `(sub ~(str item)))))
             "<tag><sub>1</sub><sub>2</sub><sub>3</sub></tag>"))
  ; Hy 0.13 style list-comp and list-comp* are still available
  (assert (= (ml (tag ~@(list-comp `(sub ~(str item)) [item (range 5)])))
             "<tag><sub>0</sub><sub>1</sub><sub>2</sub><sub>3</sub><sub>4</sub></tag>"))
  (assert (= (ml (tag ~@(list-comp* [item [1 2]] `(sub ~item))))
             "<tag><sub>1</sub><sub>2</sub></tag>"))
  (assert (= (ml (ul ~@(list-comp* [i (range 4)] `(li ~i) (% i 2))))
             "<ul><li>1</li><li>3</li></ul>")))

(defvar x "variable")
(deffun f (fn [x] x))
(defvar firstname "Dennis"
        lastname "McDonald")
(deffun wholename (fn [x y] (+ y ", " x)))
(defvar first-name "Ada")
(defvar n 1 m (+ n 1))
; functions see the macros required by the module defining them. ml
; renders when the function is compiled, so call-time values go into
; returned quasiquoted markup instead
(deffun footer (fn [] (ml (footer "static"))))
(deffun card (fn [name] `(div :class "card" ~name)))

(defn test-variables-and-functions []
  (assert (= (ml (tag ~x)) "<tag>variable</tag>"))
  (assert (= (ml (tag ~(f "function"))) "<tag>function</tag>"))
  (assert (= (ml (tag ~(wholename firstname lastname))) "<tag>McDonald, Dennis</tag>"))
  ; names with hyphens and values that refer to earlier ones
  (assert (= (ml ~first-name) "Ada"))
  (assert (= (ml ~m) "2"))
  (assert (= (ml (body ~(card "x") ~(footer)))
             "<body><div class=\"card\">x</div><footer>static</footer></body>")))

(defn test-defvar-needs-pairs []
  (with [e (pytest.raises Exception)]
    (hy.eval '(do (require hyml.variables [defvar]) (defvar lonely))))
  (assert (in "even number of arguments" (str e.value))))

(defvar to "Tove"
        from "Jani"
        heading "Reminder"
        body "Don't forget me this weekend!")

(defn test-include []
  (assert (= (ml ~@(include "test/templates/test.hy")) "<tag/>"))
  (assert (= (ml ~@(include "templates/note.hy"))
             (+ "<note src=\"https://www.w3schools.com/xml/note.xml\">"
                "<to>Tove</to><from>Jani</from><heading>Reminder</heading>"
                "<body>Don't forget me this weekend!</body></note>")))
  (assert (= (indent (ml ~@(include "templates/note.hy")))
             (.join "\n" ["<note src=\"https://www.w3schools.com/xml/note.xml\">"
                          "\t<to>Tove</to>"
                          "\t<from>Jani</from>"
                          "\t<heading>Reminder</heading>"
                          "\t<body>Don't forget me this weekend!</body>"
                          "</note>"]))))

(defn test-parse-mnml []
  (assert (= (parse-mnml '(tag)) "<tag/>"))
  (assert (= (parse-mnml '(tag :attr ~val) {"val" "val"}) "<tag attr=\"val\"/>"))
  (assert (= (parse-mnml '(tag :attr ~var ~(func))
                         {"var" "val" "func" (fn [] "Content")})
             "<tag attr=\"val\">Content</tag>")))

(defvar contacts [{:firstname "Eric" :lastname "Johnson" :telephone "+1-202-555-0170"}
                  {:firstname "Mary" :lastname "Johnson" :telephone "+1-202-555-0185"}])

(defn test-contacts []
  (assert (= (ml
               (contacts
                 ~@(do
                     (import hyml.minimal [parse-mnml])
                     (lfor contact contacts
                       `(contact
                          ~@(lfor [tag val] (.items contact)
                              (parse-mnml `(~tag ~val))))))))
             (+ "<contacts>"
                "<contact><firstname>Eric</firstname><lastname>Johnson</lastname>"
                "<telephone>+1-202-555-0170</telephone></contact>"
                "<contact><firstname>Mary</firstname><lastname>Johnson</lastname>"
                "<telephone>+1-202-555-0185</telephone></contact>"
                "</contacts>"))))

(defvar topic "How do you make XHTML 1.0 Transitional document with HyML?"
        tags ['html 'xhtml 'hyml]
        postedBy "Hege Refsnes"
        contactEmail "hege.refsnes@example.com")

(deffun valid (fn []
  `(p (a :href "http://validator.w3.org/check?uri=referer"
         (img :src "http://www.w3.org/Icons/valid-xhtml10"
              :alt "Valid XHTML 1.0 Transitional"
              :height "31" :width "88")))))

(defn test-xhtml-transitional-document []
  (assert (= (ml
               "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
               (html :xmlns "http://www.w3.org/1999/xhtml" :lang "en"
                 (head
                   (title "Conforming XHTML 1.0 Transitional Template")
                   (meta :http-equiv "Content-Type" :content "text/html; charset=utf-8"))
                 (body
                   (div :class "post"
                     (div :class "header" ~topic)
                     ~@(include "templates/body.hy")
                     (div :class "tags"
                       ~@(lfor tag tags `(span ~tag)))
                     (div :id "footer"
                       (p "Posted by: " ~postedBy)
                       (p "Email: "
                         (a :href ~(+ "mailto:" contactEmail) ~contactEmail) ".")))
                   ~(valid))))
             (+ "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
                "<html xmlns=\"http://www.w3.org/1999/xhtml\" lang=\"en\">"
                "<head><title>Conforming XHTML 1.0 Transitional Template</title>"
                "<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\"/></head>"
                "<body><div class=\"post\">"
                "<div class=\"header\">How do you make XHTML 1.0 Transitional document with HyML?</div>"
                "<div class=\"body\">I've been wondering if it is possible to create XHTML 1.0 Transitional \n"
                "      document by using a brand new HyML?</div>"
                "<div class=\"tags\"><span>html</span><span>xhtml</span><span>hyml</span></div>"
                "<div id=\"footer\"><p>Posted by: Hege Refsnes</p>"
                "<p>Email: <a href=\"mailto:hege.refsnes@example.com\">hege.refsnes@example.com</a>.</p>"
                "</div></div>"
                "<p><a href=\"http://validator.w3.org/check?uri=referer\">"
                "<img src=\"http://www.w3.org/Icons/valid-xhtml10\" alt=\"Valid XHTML 1.0 Transitional\" "
                "height=\"31\" width=\"88\"/></a></p>"
                "</body></html>"))))

(defn test-macro-macro []
  (macro custom [content] `(tag ~content))
  (assert (= (custom "x") '(tag "x"))))

(require hyml.minimal :readers [i])

(defn _ [message] (+ "translated: " message))

(defn test-gettext-reader-macro []
  (assert (= #i"Hello" "translated: Hello")))
