#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import unicode_literals, division, absolute_import, print_function
import sys
import re


def run(bk):
    note_ref_id = 0
    note_text_id = 0
# all xhtml/html files - moves found notes to end of file, insert a link
# in the text and link to css in the files with notes
    for (id, linear, href) in bk.spine_iter():
        html = bk.readfile(id)
        html_original = html

        pattern_ref = re.compile(r'(?<!<p>)\[\d+\]')
        pattern_text = re.compile(r'\<p\>\[\d+\](.+)\<\/p\>')
        note_ref = re.search(pattern_ref, html)
        note_text = re.search(pattern_text, html)

        if note_ref is not None:  # only once for each file with notes
            html = re.sub(
                r'\<\/head\>', r'<link href="../Styles/footnote.css" rel="stylesheet" type="text/css"/>\n</head>', html)
            html = re.sub(r'\<html.+\>\s*\<head\>',
                        r'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN" xmlns:epub="http://www.idpf.org/2007/ops">\n<head>', html)
            html = re.sub(
                r'\<\/body\>', r'<aside epub:type="footnote">\n<ol class="duokan-footnote-content">\n</ol>\n</aside>\n</body>', html)

            while note_ref is not None:
                note_ref_id = note_ref_id + 1
                html = re.sub(pattern_ref, r'<a class="duokan-footnote" epub:type="noteref" href="' + str(
                    id) + '#fn' + str(note_ref_id) + '" id="fnref' + str(note_ref_id) + '"><img alt="" src="../Images/note.png"/></a>', html, 1)
                print(id, href, '' + str(note_ref_id) + ':' + note_ref.group(0).strip('[]^'))
                note_ref = re.search(pattern_ref, html)

            while note_text is not None:
                note_text_id = note_text_id + 1
                html = re.sub(pattern_text, r'', html, 1)
                html = re.sub(r'\<\/ol\>', r'\n<li class="duokan-footnote-item" id="fn' + str(note_text_id) + '">\n<p class="fn"><a href="' +
                              str(id) + '#fnref' + str(note_text_id) + '">◎</a>' + note_text.group(1).strip('[]^') + '​​​​​​​​</p></li>\n</ol>', html, 1)
                print(id, href, '' + str(note_text_id) + ':' + note_text.group(1))
                note_text = re.search(pattern_text, html)
            else:
                print(id, href, "No notes found")

            if not html == html_original:
                bk.writefile(id, html)

    insert_note_css(bk)
    return 0


def insert_note_css(bk):
    cssdata = '''a.duokan-footnote {
  line-height: 1;
  text-decoration: none;
  height: auto;
  border: 0;
  color: #000000;
}

.duokan-footnote img {
  width: 0.8em;
  vertical-align: super;
}

aside {
  border-top: 2px solid #e1e1e1;
  margin-top: 1.5em;
}

ol.duokan-footnote-content {
  padding-left: 1em;
  -webkit-padding-start: 1em;
  list-style-type: none;
  /* list-style-position: outside; */
}

li.duokan-footnote-item {
  text-decoration: none;
}

p.fn {
  text-decoration: none;
  color: #000000;
  font-family: Garamond, Palatino, "kt", "楷体", serif;
  text-indent: 0;
  duokan-text-indent: 0em;
  text-align: left;
}

p.fn a {
  color: #000000;
  text-decoration: none;
  margin-left: -1em;
}
'''
    basename = "footnote.css"
    uid = "footnotecss"
    mime = "text/css"
    bk.addfile(uid, basename, cssdata, mime)
    return 0


def main():
    print("I reached main when I should not have\n")
    return -1


if __name__ == "__main__":
    sys.exit(main())
