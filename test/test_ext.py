import io

from hyml.ext import babel_extract, extract_from_source

SOURCE = '''\
(require hyml.minimal :readers [i])
(_ "Hello")
(html5 (p (gettext "World") #i"Shorthand"))
(ngettext "apple" "apples" count)
(lazy_gettext "Lazy")
(print "not a message")
#㎖(p "markup")
'''


def test_extract_from_source():
    assert extract_from_source(SOURCE) == [
        (2, "_", "Hello", []),
        (3, "gettext", "World", []),
        (3, "_", "Shorthand", []),
        (4, "ngettext", ("apple", "apples", None), []),
        (5, "gettext", "Lazy", []),
    ]


def test_babel_extract_reads_bytes_and_extra_keywords():
    fileobj = io.BytesIO('(_ "Hei")\n(tr "Moi")\n'.encode("utf-8"))
    assert list(babel_extract(fileobj, {"tr": None}, [], {})) == [
        (1, "_", "Hei", []),
        (2, "tr", "Moi", []),
    ]
