
HyML tests
============

Test main features
------------------

Assert tests for all main features of HyML library. There should be no 
output after running these tests. If there is, then *Houston, we have 
a problem!*

.. code-block:: hylang

    ;;;;;;;;;
    ; basic ;
    ;;;;;;;;;
    
    ; empty things
    (assert (= (ml) ""))
    (assert (= (ml"") ""))
    (assert (= (ml "") ""))
    (assert (= (ml ("")) "</>"))
    ; tag names
    (assert (= (ml (tag)) "<tag/>"))
    (assert (= (ml (TAG)) "<TAG/>"))
    (assert (= (ml (~(.upper "tag"))) "<TAG/>"))
    (assert (= (ml (tag "")) "<tag></tag>"))
    ; content cases
    (assert (= (ml (tag "content")) "<tag>content</tag>"))
    (assert (= (ml (tag "CONTENT")) "<tag>CONTENT</tag>"))
    (assert (= (ml (tag ~(.upper "content"))) "<tag>CONTENT</tag>"))
    ; attribute names and values
    (assert (= (ml (tag :attr "val")) "<tag attr=\"val\"/>"))
    (assert (= (ml (tag ~(keyword "attr") "val")) "<tag attr=\"val\"/>"))
    (assert (= (ml (tag :attr "val" "")) "<tag attr=\"val\"></tag>"))
    (assert (= (ml (tag :attr "val" "content")) "<tag attr=\"val\">content</tag>"))
    (assert (= (ml (tag :ATTR "val")) "<tag ATTR=\"val\"/>"))
    (assert (= (ml (tag ~(keyword (.upper "attr")) "val")) "<tag ATTR=\"val\"/>"))
    (assert (= (ml (tag :attr "VAL")) "<tag attr=\"VAL\"/>"))
    (assert (= (ml (tag :attr ~(.upper "val"))) "<tag attr=\"VAL\"/>"))
    ; nested tags
    (assert (= (ml (tag (sub))) "<tag><sub/></tag>"))
    ; unquote splice
    (assert (= (ml (tag ~@(list-comp `(sub ~(str item)) [item [1 2 3]])))
               "<tag><sub>1</sub><sub>2</sub><sub>3</sub></tag>"))
    ; variables
    (defvar x "variable")
    (assert (= (ml (tag ~x)) "<tag>variable</tag>"))
    ; functions
    (deffun f (fn [x] x))
    (assert (= (ml (tag ~(f "function"))) "<tag>function</tag>"))
    ; templates
    (with [f (open "test/templates/test.hy" "w")] 
      (f.write "(tag)"))
    (assert (= (ml ~@(include "test/templates/test.hy")) "<tag/>"))
    ; set up custom template directory
    (import hyml.template)
    (def hyml.template.template-dir "test/templates/")
    ; render template function
    (import [hyml.template [*]])
    (with [f (open "test/templates/test2.hy" "w")] 
      (f.write "(tag ~tag)"))
    (assert (= (render-template "test2.hy" {"tag" "content"}) "<tag>content</tag>"))
    ; extend template
    (require [hyml.template [*]])
    (with [f (open "test/templates/test3.1.hy" "w")] 
      (f.write "(tags :attr ~val ~tag)"))
    (with [f (open "test/templates/test3.2.hy" "w")] 
      (f.write "~(extend-template \"test3.1.hy\" {\"tag\" `(tag)})"))
    (assert (= (render-template "test3.2.hy" {"val" "val"}) "<tags attr=\"val\"><tag/></tags>"))
    ; macro -macro
    (with [f (open "test/templates/test4.hy" "w")] 
      (f.write "~(macro custom [content] `(tag ~content))~(custom ~content)"))
    (assert (= (render-template "test4.hy" {"content" "content"}) "<tag>content</tag>"))
    ; revert path
    (def hyml.template.template-dir "templates/")
    ; template macro
    (assert (= (template {"val" "val"} `(tag :attr ~val)) (template `(tag :attr ~val) {"val" "val"})))
    
    ;;;;;;;;;;;
    ; special ;
    ;;;;;;;;;;;
    
    ; tag names
    (assert (= (ml (J)) "<1j/>"))
    (assert (= (ml (~"J")) "<J/>"))
    (assert (= [(ml ('tag)) (ml (`tag)) (ml (tag)) (ml ("tag"))] (* ["<tag/>"] 4)))
    ; attribute values
    (assert (= [(ml (tag :attr 'val)) (ml (tag :attr `val)) (ml (tag :attr val)) (ml (tag :attr "val"))]
               (* ["<tag attr=\"val\"/>"] 4)))
    ; content
    (assert (= [(ml (tag 'val)) (ml (tag `val)) (ml (tag val)) (ml (tag "val"))]
               (* ["<tag>val</tag>"] 4)))
    ; keyword processing
    (assert (= [(ml (tag ':attr)) (ml (tag `:attr))] ["<tag>attr</tag>" "<tag>attr</tag>"]))
    ;(assert (= (ml (tag :"attr")) "<tag =\"attr\"/>"))
    ; boolean attributes
    (assert (= [(ml (tag :attr "attr")) (ml (tag :attr)) (ml (tag ~(keyword "attr")))]
               ["<tag attr=\"attr\"/>" "<tag attr=\"attr\"/>" "<tag attr=\"attr\"/>"]))
    (assert (= (ml (tag :attr1 :attr2)) "<tag attr1=\"attr1\" attr2=\"attr2\"/>"))
    (assert (= (ml (tag Content :attr1 :attr2)) "<tag attr1=\"attr1\" attr2=\"attr2\">Content</tag>"))
    (assert (= (ml (tag :attr1 :attr2 Content)) "<tag attr1=\"attr1\" attr2=\"Content\"/>"))
    ; no space between attribute name and value as a string literal
    (assert (= (ml (tag :attr"val")) "<tag attr=\"val\"/>"))
    ; no space between tag, keywords, keyword value, and content string literals
    (assert (= (ml (tag"content":attr"val")) "<tag attr=\"val\">content</tag>"))
    
    ;;;;;;;;;
    ; weird ;
    ;;;;;;;;;

    ; quote should not be unquoted or surpressed
    (assert (= (ml (quote :quote "quote" "quote")) "<quote quote=\"quote\">quote</quote>"))
    ; tag name, keyword name, value and content can be same
    (assert (= (ml (tag :tag "tag" "tag")) "<tag tag=\"tag\">tag</tag>"))
    ; multiple same attribute names stays in the markup in the reserved order
    (assert (= (ml (tag :attr "attr1" :attr "attr2")) "<tag attr=\"attr1\" attr=\"attr2\"/>"))
    ; parse-mnlm with variable and function dictionary
    (assert (= (parse-mnml '(tag :attr ~var ~(func)) 
                           {"var" "val" "func" (fn[]"Content")}) "<tag attr=\"val\">Content</tag>"))
