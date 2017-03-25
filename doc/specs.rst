
HyML - HTML4 / HTML5 specifications 
===================================

``xml`` does not care about the markup specifications other than general
tag and attribute notation. It is totally dummy about the naming
conventions of the tags or their relation to each other or global
structure of the markup document. It is all on the responsibility of the
user to make it correct.

``html4`` and ``html5`` macros will render tags as specified below.
These macros will minimize code when possible. Using undefined tag will
raise an error. Attributes are not validated however. One should use
official `validator <http://validator.w3.org/>`__ for a proper
validation.

This is also the last example of using ``ML`` macros.

Columns in the table are:

-  Tag name
-  Tag code when using empty content
-  Has optional end tag?
-  Has forbidden content and end tag?
-  Can omit short tag (``<col>``)?
-  Is tag in HTML4 specifications?
-  Is tag in HTML5 specifications?

.. code-block:: hylang

    (xhtml>
      (table.data
        (caption "HTML Element Specifications")
        (thead
          (tr
            ~@(list-comp* [col ["Tag name" "Code" "Optional" "Forbidden" "Omit" "HTML4" "HTML5"]]
              `(th ~col))))
        (tbody 
         ~@(list-comp* [[id row] (.items (do (import (hyml.macros (specs))) specs))]
           (do
            `(tr
              (td ~(.upper (get row :name)))
              (td ~(do (import html) 
                       (import (hyml.macros (parse-html4 parse-html5))) 
                       (html.escape (if (get row :html4) (parse-html4 `(~(get row :name) ""))
                                        (parse-html5 `(~(get row :name) ""))))))
              (td ~(do (import (hyml.macros (optional?)))
                       (if (optional? (get row :name)) "✓" "")))
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
      -  &lt;a&gt;&lt;/a&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  ABBR
      -  &lt;abbr&gt;&lt;/abbr&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  ACRONYM
      -  &lt;acronym&gt;&lt;/acronym&gt;
      -  
      -  
      -  
      -  ✓
      -  

   *  -  ADDRESS
      -  &lt;address&gt;&lt;/address&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  APPLET
      -  &lt;applet&gt;&lt;/applet&gt;
      -  
      -  
      -  
      -  ✓
      -  

   *  -  AREA
      -  &lt;area&gt;
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  ARTICLE
      -  &lt;article&gt;&lt;/article&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  ASIDE
      -  &lt;aside&gt;&lt;/aside&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  AUDIO
      -  &lt;audio&gt;&lt;/audio&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  B
      -  &lt;b&gt;&lt;/b&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  BASE
      -  &lt;base&gt;
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  BASEFONT
      -  &lt;basefont&gt;
      -  
      -  ✓
      -  
      -  ✓
      -  

   *  -  BDI
      -  &lt;bdi&gt;&lt;/bdi&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  BDO
      -  &lt;bdo&gt;&lt;/bdo&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  BIG
      -  &lt;big&gt;&lt;/big&gt;
      -  
      -  
      -  
      -  ✓
      -  

   *  -  BLOCKQUOTE
      -  &lt;blockquote&gt;&lt;/blockquote&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  BODY
      -  &lt;body&gt;
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  BR
      -  &lt;br&gt;
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  BUTTON
      -  &lt;button&gt;&lt;/button&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  CANVAS
      -  &lt;canvas&gt;&lt;/canvas&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  CAPTION
      -  &lt;caption&gt;
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  CENTER
      -  &lt;center&gt;&lt;/center&gt;
      -  
      -  
      -  
      -  ✓
      -  

   *  -  CITE
      -  &lt;cite&gt;&lt;/cite&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  CODE
      -  &lt;code&gt;&lt;/code&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  COL
      -  &lt;col&gt;
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  COLGROUP
      -  &lt;colgroup&gt;
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  DATALIST
      -  &lt;datalist&gt;&lt;/datalist&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  DD
      -  &lt;dd&gt;&lt;/dd&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  DEL
      -  &lt;del&gt;&lt;/del&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  DETAILS
      -  &lt;details&gt;&lt;/details&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  DFN
      -  &lt;dfn&gt;&lt;/dfn&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  DIALOG
      -  &lt;dialog&gt;&lt;/dialog&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  DIR
      -  &lt;dir&gt;&lt;/dir&gt;
      -  
      -  
      -  
      -  ✓
      -  

   *  -  DIV
      -  &lt;div&gt;&lt;/div&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  DL
      -  &lt;dl&gt;&lt;/dl&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  DT
      -  &lt;dt&gt;&lt;/dt&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  EM
      -  &lt;em&gt;&lt;/em&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  EMBED
      -  &lt;embed&gt;&lt;/embed&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  FIELDSET
      -  &lt;fieldset&gt;&lt;/fieldset&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  FIGCAPTION
      -  &lt;figcaption&gt;&lt;/figcaption&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  FIGURE
      -  &lt;figure&gt;&lt;/figure&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  FONT
      -  &lt;font&gt;&lt;/font&gt;
      -  
      -  
      -  
      -  ✓
      -  

   *  -  FOOTER
      -  &lt;footer&gt;&lt;/footer&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  FORM
      -  &lt;form&gt;&lt;/form&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  FRAME
      -  &lt;frame&gt;
      -  
      -  ✓
      -  
      -  ✓
      -  

   *  -  FRAMESET
      -  &lt;frameset&gt;&lt;/frameset&gt;
      -  
      -  
      -  
      -  ✓
      -  

   *  -  H1
      -  &lt;h1&gt;&lt;/h1&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  H2
      -  &lt;h2&gt;&lt;/h2&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  H3
      -  &lt;h3&gt;&lt;/h3&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  H4
      -  &lt;h4&gt;&lt;/h4&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  H5
      -  &lt;h5&gt;&lt;/h5&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  H6
      -  &lt;h6&gt;&lt;/h6&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  HEAD
      -  &lt;head&gt;
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  HEADER
      -  &lt;header&gt;&lt;/header&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  HR
      -  &lt;hr&gt;
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  HTML
      -  &lt;html&gt;
      -  ✓
      -  
      -  
      -  ✓
      -  ✓

   *  -  I
      -  &lt;i&gt;&lt;/i&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  IFRAME
      -  &lt;iframe&gt;&lt;/iframe&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  IMG
      -  &lt;img&gt;
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  INPUT
      -  &lt;input&gt;
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  INS
      -  &lt;ins&gt;&lt;/ins&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  ISINDEX
      -  &lt;isindex&gt;
      -  
      -  ✓
      -  
      -  ✓
      -  ✓

   *  -  KBD
      -  &lt;kbd&gt;&lt;/kbd&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  KEYGEN
      -  &lt;keygen&gt;&lt;/keygen&gt;
      -  
      -  
      -  ✓
      -  
      -  ✓

   *  -  LABEL
      -  &lt;label&gt;&lt;/label&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  LEGEND
      -  &lt;legend&gt;&lt;/legend&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  LI
      -  &lt;li&gt;&lt;/li&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  LINK
      -  &lt;link&gt;
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  MAIN
      -  &lt;main&gt;&lt;/main&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  MAP
      -  &lt;map&gt;&lt;/map&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  MARK
      -  &lt;mark&gt;&lt;/mark&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  MENU
      -  &lt;menu&gt;&lt;/menu&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  MENUITEM
      -  &lt;menuitem&gt;&lt;/menuitem&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  META
      -  &lt;meta&gt;
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  METER
      -  &lt;meter&gt;&lt;/meter&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  NAV
      -  &lt;nav&gt;&lt;/nav&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  NOFRAMES
      -  &lt;noframes&gt;&lt;/noframes&gt;
      -  
      -  
      -  
      -  ✓
      -  

   *  -  NOSCRIPT
      -  &lt;noscript&gt;&lt;/noscript&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  OBJECT
      -  &lt;object&gt;&lt;/object&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  OL
      -  &lt;ol&gt;&lt;/ol&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  OPTGROUP
      -  &lt;optgroup&gt;&lt;/optgroup&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  OPTION
      -  &lt;option&gt;&lt;/option&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  OUTPUT
      -  &lt;output&gt;&lt;/output&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  P
      -  &lt;p&gt;&lt;/p&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  PARAM
      -  &lt;param&gt;
      -  
      -  ✓
      -  ✓
      -  ✓
      -  ✓

   *  -  PICTURE
      -  &lt;picture&gt;&lt;/picture&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  PRE
      -  &lt;pre&gt;&lt;/pre&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  PROGRESS
      -  &lt;progress&gt;&lt;/progress&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  Q
      -  &lt;q&gt;&lt;/q&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  RP
      -  &lt;rp&gt;&lt;/rp&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  RT
      -  &lt;rt&gt;&lt;/rt&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  RUBY
      -  &lt;ruby&gt;&lt;/ruby&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  S
      -  &lt;s&gt;&lt;/s&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SAMP
      -  &lt;samp&gt;&lt;/samp&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SCRIPT
      -  &lt;script&gt;&lt;/script&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SECTION
      -  &lt;section&gt;&lt;/section&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  SELECT
      -  &lt;select&gt;&lt;/select&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SMALL
      -  &lt;small&gt;&lt;/small&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SOURCE
      -  &lt;source&gt;
      -  
      -  ✓
      -  ✓
      -  
      -  ✓

   *  -  SPAN
      -  &lt;span&gt;&lt;/span&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  STRIKE
      -  &lt;strike&gt;&lt;/strike&gt;
      -  
      -  
      -  
      -  ✓
      -  

   *  -  STRONG
      -  &lt;strong&gt;&lt;/strong&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  STYLE
      -  &lt;style&gt;&lt;/style&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SUB
      -  &lt;sub&gt;&lt;/sub&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  SUMMARY
      -  &lt;summary&gt;&lt;/summary&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  SUP
      -  &lt;sup&gt;&lt;/sup&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TABLE
      -  &lt;table&gt;&lt;/table&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TBODY
      -  &lt;tbody&gt;&lt;/tbody&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TD
      -  &lt;td&gt;&lt;/td&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TEXTAREA
      -  &lt;textarea&gt;&lt;/textarea&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TFOOT
      -  &lt;tfoot&gt;&lt;/tfoot&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TH
      -  &lt;th&gt;&lt;/th&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  THEAD
      -  &lt;thead&gt;&lt;/thead&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TIME
      -  &lt;time&gt;&lt;/time&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  TITLE
      -  &lt;title&gt;&lt;/title&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TR
      -  &lt;tr&gt;&lt;/tr&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  TRACK
      -  &lt;track&gt;
      -  
      -  ✓
      -  ✓
      -  
      -  ✓

   *  -  TT
      -  &lt;tt&gt;&lt;/tt&gt;
      -  
      -  
      -  
      -  ✓
      -  

   *  -  U
      -  &lt;u&gt;&lt;/u&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  UL
      -  &lt;ul&gt;&lt;/ul&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  VAR
      -  &lt;var&gt;&lt;/var&gt;
      -  
      -  
      -  
      -  ✓
      -  ✓

   *  -  VIDEO
      -  &lt;video&gt;&lt;/video&gt;
      -  
      -  
      -  
      -  
      -  ✓

   *  -  WBR
      -  &lt;wbr&gt;
      -  
      -  ✓
      -  ✓
      -  
      -  ✓


