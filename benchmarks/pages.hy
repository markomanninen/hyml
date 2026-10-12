;; The benchmark pages written with the HyML macros. The macros render at
;; compile time, so static-page returns a string that was built when this
;; module was compiled.

(require hyml.macros [html5])

(setv static-source "
(html :lang \"en\"
  (head (meta :charset \"utf-8\") (title \"HyML benchmark\"))
  (body
    (header (h1 \"HyML benchmark\")
      (nav (ul (li (a :href \"/\" \"Home\")) (li (a :href \"/docs\" \"Docs\"))
               (li (a :href \"/blog\" \"Blog\")) (li (a :href \"/about\" \"About\")))))
    (main
      (article
        (h2 \"Markup as data\")
        (p \"HyML writes HTML as s-expressions.\")
        (p \"Text is escaped: <b> & co.\")
        (ul (li \"one\") (li \"two\") (li \"three\") (li \"four\") (li \"five\"))
        (p (a :href \"https://example.com/?a=1&b=2\" \"A link\"))))
    (footer (p \"MIT licensed\"))))")

(defn static-page []
  (html5
    (html :lang "en"
      (head (meta :charset "utf-8") (title "HyML benchmark"))
      (body
        (header (h1 "HyML benchmark")
          (nav (ul (li (a :href "/" "Home")) (li (a :href "/docs" "Docs"))
                   (li (a :href "/blog" "Blog")) (li (a :href "/about" "About")))))
        (main
          (article
            (h2 "Markup as data")
            (p "HyML writes HTML as s-expressions.")
            (p "Text is escaped: &lt;b&gt; &amp; co.")
            (ul (li "one") (li "two") (li "three") (li "four") (li "five"))
            (p (a :href "https://example.com/?a=1&amp;b=2" "A link"))))
        (footer (p "MIT licensed"))))))

; runtime rendering with code: ~@ and ~ are evaluated on every call
(setv table-source "
(table (thead (tr (th \"Name\") (th \"Price\") (th \"Qty\")))
  (tbody ~@(lfor row rows
             `(tr (td (a :href ~(get row \"url\") ~(escape (get row \"name\"))))
                  (td ~(get row \"price\"))
                  (td ~(get row \"qty\"))))))")
