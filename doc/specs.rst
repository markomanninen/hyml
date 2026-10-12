
HyML - HTML4 / HTML5 specifications 
===================================

``xml`` does not care about the markup specifications other than general
tag and attribute notation. It is totally dummy about the naming
conventions of the tags or their relation to each other or global
structure of the markup document. It is all on the responsibility of the
user to make it correct.

``html4`` and ``html5`` as well as ``xhtml`` and ``xhtml5`` macros will render
tags as specified below. These macros will minimize code when possible. Using 
undefined tag will raise an error. Attributes are not validated however. One 
should use official `validator <http://validator.w3.org/>`__ for a proper
validation.

This is also the last example of using ``ML`` macros. xhtml> will delegate
xhtml content to IPython.display method so that content is rendered on
Jupyter Notebook cell rather than just output as a raw xml string.
``xhtml>`` is required from ``hyml.helpers``, and the ``xhtml`` macro
gives the same markup as a string outside of Jupyter Notebook.

Columns in the table are:

-  Tag name
-  Tag code when using empty content
-  Has the optional end tag? (in ``html4`` and ``html5``, depending on the
   next sibling and the parent element)
-  Has a forbidden content and the end tag?
-  Can omit the short tag? For example: ``<col>``
-  Is the tag in HTML4 specifications?
-  Is the tag in HTML5 specifications?

.. code-block:: hylang

    (require hyml.macros *)
    (require hyml.helpers [xhtml>])

    (xhtml>
      (table.data
        (caption "HTML Element Specifications")
        (thead
          (tr
            ~@(list-comp* [col ["Tag name" "Code" "Optional" "Forbidden" "Omit" "HTML4" "HTML5"]]
              `(th ~col))))
        (tbody
          ~@(do (import html
                        hyml.macros [specs parse-html4 parse-html5]
                        hyml.specs [optional-end-tags])
            (list-comp* [[id row] (.items specs)]
             `(tr
               (td ~(.upper (get row :name)))
               (td ~(html.escape
                     (if (get row :html4)
                         (parse-html4 `(~(get row :name)))
                         (parse-html5 `(~(get row :name))))))
               (td ~(if (in id optional-end-tags) "✓" ""))
               (td ~(if (get row :forbidden) "✓" ""))
               (td ~(if (get row :omit) "✓" ""))
               (td ~(if (get row :html4) "✓" ""))
               (td ~(if (get row :html5) "✓" ""))))))))

.. list-table::
   :header-rows: 1

   *  -  Tag name
      -  Code
      -  Optional
      -  Forbidden
      -  Omit
      -  HTML4
      -  HTML5

   *  -  A
      -  <a></a>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  ABBR
      -  <abbr></abbr>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  ACRONYM
      -  <acronym></acronym>
      -  
      -  
      -  
      -  ✓
      -  

   *  -  ADDRESS
      -  <address></address>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  APPLET
      -  <applet></applet>
      -  
      -  
      -  
      -  ✓
      -  

   *  -  AREA
      -  <area>
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  ARTICLE
      -  <article></article>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  ASIDE
      -  <aside></aside>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  AUDIO
      -  <audio></audio>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  B
      -  <b></b>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  BASE
      -  <base>
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  BASEFONT
      -  <basefont>
      -  
      -  ✓
      -  
      -  ✓
      -  

   *  -  BDI
      -  <bdi></bdi>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  BDO
      -  <bdo></bdo>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  BIG
      -  <big></big>
      -  
      -  
      -  
      -  ✓
      -  

   *  -  BLOCKQUOTE
      -  <blockquote></blockquote>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  BODY
      -  <body>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  BR
      -  <br>
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  BUTTON
      -  <button></button>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  CANVAS
      -  <canvas></canvas>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  CAPTION
      -  <caption>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  CENTER
      -  <center></center>
      -  
      -  
      -  
      -  ✓
      -  

   *  -  CITE
      -  <cite></cite>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  CODE
      -  <code></code>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  COL
      -  <col>
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  COLGROUP
      -  <colgroup>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  DATA
      -  <data></data>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  DATALIST
      -  <datalist></datalist>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  DD
      -  <dd></dd>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  DEL
      -  <del></del>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  DETAILS
      -  <details></details>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  DFN
      -  <dfn></dfn>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  DIALOG
      -  <dialog></dialog>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  DIR
      -  <dir></dir>
      -  
      -  
      -  
      -  ✓
      -  

   *  -  DIV
      -  <div></div>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  DL
      -  <dl></dl>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  DT
      -  <dt></dt>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  EM
      -  <em></em>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  EMBED
      -  <embed>
      -  
      -  ✓
      -  ✓
      -  
      -  ✓

   *  -  FIELDSET
      -  <fieldset></fieldset>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  FIGCAPTION
      -  <figcaption></figcaption>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  FIGURE
      -  <figure></figure>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  FONT
      -  <font></font>
      -  
      -  
      -  
      -  ✓
      -  

   *  -  FOOTER
      -  <footer></footer>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  FORM
      -  <form></form>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  FRAME
      -  <frame>
      -  
      -  ✓
      -  
      -  ✓
      -  

   *  -  FRAMESET
      -  <frameset></frameset>
      -  
      -  
      -  
      -  ✓
      -  

   *  -  H1
      -  <h1></h1>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  H2
      -  <h2></h2>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  H3
      -  <h3></h3>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  H4
      -  <h4></h4>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  H5
      -  <h5></h5>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  H6
      -  <h6></h6>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  HEAD
      -  <head>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  HEADER
      -  <header></header>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  HGROUP
      -  <hgroup></hgroup>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  HR
      -  <hr>
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  HTML
      -  <html>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  I
      -  <i></i>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  IFRAME
      -  <iframe></iframe>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  IMG
      -  <img>
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  INPUT
      -  <input>
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  INS
      -  <ins></ins>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  ISINDEX
      -  <isindex>
      -  
      -  ✓
      -  
      -  ✓
      -  ✓

   *  -  KBD
      -  <kbd></kbd>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  KEYGEN
      -  <keygen>
      -  
      -  ✓
      -  ✓
      -  
      -  ✓

   *  -  LABEL
      -  <label></label>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  LEGEND
      -  <legend></legend>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  LI
      -  <li></li>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  LINK
      -  <link>
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  MAIN
      -  <main></main>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  MAP
      -  <map></map>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  MARK
      -  <mark></mark>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  MENU
      -  <menu></menu>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  MENUITEM
      -  <menuitem></menuitem>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  META
      -  <meta>
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  METER
      -  <meter></meter>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  NAV
      -  <nav></nav>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  NOFRAMES
      -  <noframes></noframes>
      -  
      -  
      -  
      -  ✓
      -  

   *  -  NOSCRIPT
      -  <noscript></noscript>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  OBJECT
      -  <object></object>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  OL
      -  <ol></ol>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  OPTGROUP
      -  <optgroup></optgroup>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  OPTION
      -  <option></option>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  OUTPUT
      -  <output></output>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  P
      -  <p></p>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  PARAM
      -  <param>
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  PICTURE
      -  <picture></picture>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  PRE
      -  <pre></pre>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  PROGRESS
      -  <progress></progress>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  Q
      -  <q></q>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  RP
      -  <rp></rp>
      -  ✓
      -  
      -  
      -  
      -  ✓

   *  -  RT
      -  <rt></rt>
      -  ✓
      -  
      -  
      -  
      -  ✓

   *  -  RUBY
      -  <ruby></ruby>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  S
      -  <s></s>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SAMP
      -  <samp></samp>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SCRIPT
      -  <script></script>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SEARCH
      -  <search></search>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  SECTION
      -  <section></section>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  SELECT
      -  <select></select>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SLOT
      -  <slot></slot>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  SMALL
      -  <small></small>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SOURCE
      -  <source>
      -  
      -  ✓
      -  ✓
      -  
      -  ✓

   *  -  SPAN
      -  <span></span>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  STRIKE
      -  <strike></strike>
      -  
      -  
      -  
      -  ✓
      -  

   *  -  STRONG
      -  <strong></strong>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  STYLE
      -  <style></style>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SUB
      -  <sub></sub>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SUMMARY
      -  <summary></summary>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  SUP
      -  <sup></sup>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TABLE
      -  <table></table>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TBODY
      -  <tbody></tbody>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  TD
      -  <td></td>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  TEMPLATE
      -  <template></template>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  TEXTAREA
      -  <textarea></textarea>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TFOOT
      -  <tfoot></tfoot>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  TH
      -  <th></th>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  THEAD
      -  <thead></thead>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  TIME
      -  <time></time>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  TITLE
      -  <title></title>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TR
      -  <tr></tr>
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  TRACK
      -  <track>
      -  
      -  ✓
      -  ✓
      -  
      -  ✓

   *  -  TT
      -  <tt></tt>
      -  
      -  
      -  
      -  ✓
      -  

   *  -  U
      -  <u></u>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  UL
      -  <ul></ul>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  VAR
      -  <var></var>
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  VIDEO
      -  <video></video>
      -  
      -  
      -  
      -  
      -  ✓

   *  -  WBR
      -  <wbr>
      -  
      -  ✓
      -  ✓
      -  
      -  ✓
