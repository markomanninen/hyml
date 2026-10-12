;; Tests for the xml, xhtml, xhtml5, html4 and html5 macros. Expected
;; values come from the executed notebook "HyML - XML & (X)HTML generator
;; for Hy.ipynb" and README.rst unless noted otherwise.

(require hyml.macros *)
(require hyml.macros :readers [㎖])
(import hyml.macros *)
(import pytest)

(defn read-forms [source]
  (list (hy.read-many source)))

(defn test-xml-basics []
  (assert (= [(xml (node))
              (xml (node :attribute ""))
              (xml (node :attribute "value"))
              (xml (node :attribute "value" ""))
              (xml (node :attribute "value" "Content"))]
             ["<node/>"
              "<node attribute=\"\"/>"
              "<node attribute=\"value\"/>"
              "<node attribute=\"value\"></node>"
              "<node attribute=\"value\">Content</node>"]))
  (assert (= (xml (html (head (title "Page title")) (body (div "Page content" :class "container"))))
             "<html><head><title>Page title</title></head><body><div class=\"container\">Page content</div></body></html>"))
  (assert (= (xml (p "Sentence 1") (p "Sentence 2") (p "Sentence 3"))
             "<p>Sentence 1</p><p>Sentence 2</p><p>Sentence 3</p>")))

(defn test-square-ml-reader-macro []
  (assert (= #㎖(html (head (title "Page title")) (body (div "Page content" :class "container")))
             "<html><head><title>Page title</title></head><body><div class=\"container\">Page content</div></body></html>")))

(defn test-xml-has-no-shorthand-or-validation []
  (assert (= (xml (h1.main) (time)) "<h1.main/><time/>")))

(defn test-special-tags []
  (assert (= (xml (?xml :version "1.0" :encoding "UTF-8")) "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"))
  (assert (= (xml (!DOCTYPE html)) "<!DOCTYPE html>"))
  ; DOCTYPE parts used to be joined without spaces or quotes
  (assert (= (xml (!DOCTYPE note SYSTEM "Note.dtd")) "<!DOCTYPE note SYSTEM \"Note.dtd\">"))
  (assert (= (html5 (!DOCTYPE html)) "<!DOCTYPE html>"))
  (assert (= (xml (!-- "comment")) "<!--comment-->")))

(defn test-html-minimizing []
  (assert (= (html4 (meta :name "keywords" :content "HTML,CSS,XML,JavaScript"))
             "<meta name=keywords content=HTML,CSS,XML,JavaScript>"))
  (assert (= (xhtml (meta :name "keywords" :content "HTML,CSS,XML,JavaScript"))
             "<meta name=\"keywords\" content=\"HTML,CSS,XML,JavaScript\"/>"))
  (assert (= (html4 (input :disabled "disabled")) "<input disabled>"))
  (assert (= (html4 (table (tr (td "Cell 1") (td "Cell 2") (td "Cell 3"))))
             "<table><tr><td>Cell 1<td>Cell 2<td>Cell 3</table>"))
  (assert (= (xhtml (title) (table (tr (td "Cell 1") (td "Cell 2") (td "Cell 3"))))
             "<title/><table><tr><td>Cell 1</td><td>Cell 2</td><td>Cell 3</td></tr></table>")))

(defn test-html-has-no-self-closing-elements []
  ; was <title/>, which browsers read as an unclosed start tag
  (assert (= (html4 (title)) "<title></title>"))
  (assert (= (html5 (div) (br) (img :src "a.png")) "<div></div><br><img src=a.png>")))

(defn test-boolean-attributes []
  ; valueless boolean attributes were dropped in the ML macros
  (assert (= (html4 (input :disabled)) "<input disabled>"))
  (assert (= (html5 (input :type "checkbox" :checked :disabled))
             "<input type=checkbox checked disabled>"))
  (assert (= (xhtml (input :disabled)) "<input disabled=\"disabled\"/>")))

(defn test-unquoted-attribute-values-are-safe []
  ; minimized values were left unquoted unless they contained a space
  (assert (= (html5 (input :value "")) "<input value=\"\">"))
  (assert (= (html5 (input :value "it's")) "<input value=\"it's\">"))
  (assert (= (html5 (a :href "?a=1&b=2" "x")) "<a href=\"?a=1&b=2\">x</a>"))
  (assert (= (html5 (input :value "a\tb")) "<input value=\"a\tb\">"))
  (assert (= (xhtml (p :title "say \"hi\"" "x")) "<p title=\"say &quot;hi&quot;\">x</p>")))

(defn test-shorthand []
  (assert (= (xhtml5 (.main-container (h1.main.header "x") (ul#main "List")))
             "<div class=\"main-container\"><h1 class=\"main header\">x</h1><ul id=\"main\">List</ul></div>"))
  (assert (= (xhtml (div#main.big.wide "x")) "<div id=\"main\" class=\"big wide\">x</div>"))
  (assert (= (xhtml (p.a :class "b" "x")) "<p class=\"b a\">x</p>"))
  (assert (= (html5 (.x)) "<div class=x></div>")))

(defn test-validation []
  (with [e (pytest.raises HyMLError)]
    (render "html4" (read-forms "(time)")))
  (assert (= (str e.value) "Tag name 'time' not meeting html4 specifications."))
  (assert (= (html5 (time "now")) "<time>now</time>"))
  (with [e (pytest.raises HyMLError)]
    (render "html5" (read-forms "(br \"content\")")))
  (assert (in "void element" (str e.value))))

(defn test-html5-elements []
  (assert (= (html5 (template (p "x"))) "<template><p>x</template>"))
  (assert (= (html5 (embed :src "a.swf")) "<embed src=a.swf>"))
  (assert (= (xhtml5 (embed :src "a.swf")) "<embed src=\"a.swf\"/>")))

(defn test-optional-end-tags []
  (assert (= (html5 (ul (li "a") (li "b"))) "<ul><li>a<li>b</ul>"))
  (assert (= (html5 (dl (dt "t") (dd "d") (dt "u") (dd "e"))) "<dl><dt>t<dd>d<dt>u<dd>e</dl>"))
  (assert (= (html5 (div (p "x") (p "y"))) "<div><p>x<p>y</div>"))
  (assert (= (html5 (div (p "x") (.box "y"))) "<div><p>x<div class=box>y</div></div>"))
  ; p inside a is not closed implicitly
  (assert (= (html5 (a (p "x"))) "<a><p>x</p></a>"))
  ; text after p used to be compared by its first letter: "pear" -> p
  (assert (= (html5 (div (p "x") "pear")) "<div><p>x</p>pear</div>"))
  (assert (= (html5 (ruby "漢" (rp "(") (rt "kan") (rp ")"))) "<ruby>漢<rp>(<rt>kan<rp>)</ruby>"))
  (assert (= (html5 (select (option "a") (option "b"))) "<select><option>a<option>b</select>"))
  (assert (= (html5 (table (caption "c") "<!-- x -->")) "<table><caption>c</caption><!-- x --></table>"))
  (assert (= (html5 (html (head (title "t")) (body (p "x"))))
             "<html><head><title>t</title><body><p>x")))

(defn test-unquote []
  (assert (= (xml (p "Sum: " (b ~(sum [1 2 3 4])) !)) "<p>Sum: <b>10</b>!</p>"))
  (assert (= (xml ~(+ "a" "b")) "ab"))
  ; unquoted code can return markup or attributes
  (assert (= (xml (p ~'(b "x"))) "<p><b>x</b></p>"))
  (assert (= (xml (p ~(hy.models.Keyword "id") "x")) "<p id=\"x\"/>")))

(defn test-unquote-splice []
  (assert (= (xhtml
               (table (thead
                 (tr ~@(lfor [i label] (enumerate (* ["col"] 3))
                         `(th :class (if (% ~i 2) "odd" "even") ~label " " ~i))))))
             (+ "<table><thead><tr><th class=\"even\">col 0</th><th class=\"odd\">col 1</th>"
                "<th class=\"even\">col 2</th></tr></thead></table>")))
  (assert (= (xhtml
               ~@(list-comp* [uls [[1 2] [1 2]]]
                   `(ul (b "List")
                      ~@(list-comp* [li uls]
                          `(li item " " ~li)))))
             (* "<ul><b>List</b><li>item 1</li><li>item 2</li></ul>" 2)))
  (assert (= (xml
               ~@(list-comp `(ul (b "List")
                               ~@(list-comp `(li item " " ~li) [li uls]))
                            [uls [[1 2] [1 2]]]))
             (* "<ul><b>List</b><li>item 1</li><li>item 2</li></ul>" 2))))

(defn test-all-in-one []
  (assert (= (xhtml5
               "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
               "<!DOCTYPE html>"
               (html :lang "en" :xmlns "http://www.w3.org/1999/xhtml"
                 (head (title "Page title"))
                 (body
                   "<!-- body starts here -->"
                   (.main-container
                     (h1.main.header ~(.capitalize "page header"))
                     (ul#main "List"
                       ~@(list-comp* [[idx num] (enumerate (range 3))]
                           `(li :class ~(if (% idx 2) "odd" "even") ~num)))))))
             (+ "<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE html>"
                "<html lang=\"en\" xmlns=\"http://www.w3.org/1999/xhtml\">"
                "<head><title>Page title</title></head>"
                "<body><!-- body starts here --><div class=\"main-container\">"
                "<h1 class=\"main header\">Page header</h1>"
                "<ul id=\"main\">List<li class=\"even\">0</li><li class=\"odd\">1</li><li class=\"even\">2</li></ul>"
                "</div></body></html>"))))

(defn test-data-table []
  ; spliced rows are now siblings of each other, so more end tags are omitted
  (assert (= (html4
               (table#data
                 (caption "Data table")
                 (colgroup
                   (col :style "background-color:red")
                   (col :style "background-color: green"))
                 (thead
                   (tr ~@(list-comp* [col ["Column 1" "Column 2"]] `(th ~col))))
                 (tbody#tbody1
                   ~@(list-comp* [row (range 1 3)]
                       `(tr ~@(list-comp* [cell (range 2)] `(td ~row "." ~cell)))))
                 (tfoot (tr (td :colspan "2" "Footer")))))
             (+ "<table id=data><caption>Data table<colgroup>"
                "<col style=background-color:red><col style=\"background-color: green\">"
                "<thead><tr><th>Column 1<th>Column 2"
                "<tbody id=tbody1><tr><td>1.0<td>1.1<tr><td>2.0<td>2.1"
                "<tfoot><tr><td colspan=2>Footer</table>"))))

(defn test-csv-table []
  (assert (= (xhtml
               (table.data
                 (caption "Contacts")
                 ~@(list-comp*
                     [[idx row] (enumerate (.split (.read (open "data.csv" "r")) "\n"))]
                     (if idx
                         `(tbody ~@(list-comp* [item (.split row ",")] `(td ~item)))
                         `(thead ~@(list-comp* [item (.split row ",")] `(th ~item)))))))
             (+ "<table class=\"data\"><caption>Contacts</caption>"
                "<thead><th>Title</th><th>Name</th><th>Phone</th></thead>"
                "<tbody><td>Mr.</td><td>John</td><td>07868785831</td></tbody>"
                "<tbody><td>Miss</td><td>Linda</td><td>0141-2244-5566</td></tbody>"
                "<tbody><td>Master</td><td>Jack</td><td>0142-1212-1234</td></tbody>"
                "<tbody><td>Mr.</td><td>Bush</td><td>911-911-911</td></tbody></table>"))))

(defvar lang "en"
        title "Page title"
        body "Content")

(defn test-include-and-variables []
  (assert (= (xhtml ~@(include "templates/template.hy"))
             "<html lang=\"en\"><head><title>Page title</title></head><body><p>Content</p></body></html>"))
  (assert (= (xhtml ~lang ", " ~title ", " ~body) "en, Page title, Content")))

(defn test-attribute-expressions-and-unquote []
  (assert (= (xml (td :class (if True "yes" "no"))) "<td class=\"yes\"/>"))
  (assert (= (xml (td :lang ~lang)) "<td lang=\"en\"/>")))

(defn test-render-with-variables []
  (assert (= (render "html5" (read-forms "(p ~greeting)") {"greeting" "hi"}) "<p>hi</p>"))
  (assert (= (parse-html5 (hy.read "(p \"x\")")) "<p>x</p>")))

(defn test-specs-table []
  (assert (= (lfor [key row] (cut (list (.items specs)) 3) (get row :name))
             ["a" "abbr" "acronym"]))
  (assert (get specs :br :forbidden))
  (assert (not (get specs :acronym :html5))))
