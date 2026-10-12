(require hyml.helpers *)
(import hyml.helpers [indent HyMLError])
(import sys types pytest)

(defn test-indent []
  (assert (= (indent "<a><b>x</b></a>") "<a>\n\t<b>x</b>\n</a>"))
  (assert (= (indent "<?xml version=\"1.0\" encoding=\"UTF-8\"?><a><b/></a>")
             "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<a>\n\t<b/>\n</a>")))

(defn test-indent-needs-single-root []
  ; used to return the exception object as the result
  (with [(pytest.raises HyMLError)]
    (indent "<a/><b/>")))

(defn test-println [capsys]
  (println "a" (+ "b" "c"))
  (assert (= (. (capsys.readouterr) out) "a\nbc\n")))

(defn test-list-comp []
  (assert (= (list-comp (* x 2) [x (range 3)]) [0 2 4]))
  (assert (= (list-comp (* x 2) [x (range 4)] (% x 2)) [2 6]))
  (assert (= (list-comp* [[i c] (enumerate "ab")] (+ c (str i))) ["a0" "b1"])))

(defn test-notebook-renderers [monkeypatch]
  ; IPython is imported only when the expanded code runs
  (setv ipython (types.ModuleType "IPython")
        display (types.ModuleType "IPython.display")
        display.HTML (fn [markup] #("HTML" markup))
        ipython.display display)
  (monkeypatch.setitem sys.modules "IPython" ipython)
  (monkeypatch.setitem sys.modules "IPython.display" display)
  (assert (= (ml> (p "x")) #("HTML" "<p>x</p>")))
  (assert (= (xml> (p "x")) #("HTML" "<p>x</p>")))
  (assert (= (html5> (p "x")) #("HTML" "<p>x</p>"))))
