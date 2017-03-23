#!/usr/bin/python3

;----------------------------------------
; print multiple statements on new lines
;----------------------------------------

(defmacro println [&rest args]
  `(do
    (setv args (list ~args))
    (for [line args]
      (print line))))

(defn create-symbol [&rest args]
  (hy.HySymbol (.join "" (map str args))))

;----------------------------------------------
; render html for the Jupyter Notebook document
; this is not mandatory for HyML other macros
; this is just for the html render in NB
;----------------------------------------------

(try 
  (do
    (import IPython)
    (if (in 'display (.__dir__ IPython))
        (do
          (defmacro xml> [&rest code]
            `(IPython.display.HTML (xml ~@code)))

          (defmacro xhtml> [&rest code]
            `(IPython.display.HTML (xhtml ~@code)))

          (defmacro xhtml5> [&rest code]
            `(IPython.display.HTML (xhtml5 ~@code)))

          (defmacro html4> [&rest code]
            `(IPython.display.HTML (html4 ~@code)))

          (defmacro html5> [&rest code]
            `(IPython.display.HTML (html5 ~@code))))))
  (except (e Exception) (print e)))

;-----------------
; Indent xml code
;-----------------
(import xml.dom.minidom)

(setv dom xml.dom.minidom)

(defn indent [xmldoc]
  (try
    (do
      (setv pretty-lines (-> xmldoc dom.parseString .toprettyxml .splitlines))
      (try
      	(do
      	  (setv pretty-lines (.join "\n" (drop 1 pretty-lines)))
	      (if (= (.index xmldoc "<?xml") 0)
	          (+ (.join "" (take (+ (.index xmldoc "?>") 2) xmldoc)) "\n" pretty-lines)
	      	  pretty-lines))
	    (except (e Exception) pretty-lines)))
     (except (e Exception) e)))
