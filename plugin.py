#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import unicode_literals, division, absolute_import, print_function
import sys
import re


def run(bk):
    lastid = 0
    fnid = 0
    fnid1 = 0
# all xhtml/html files - moves found notes to end of file, insert a link
# in the text and link to css in the files with notes
    for (id, href) in bk.text_iter():
        html = bk.readfile(id)
        html_original = html
        found = re.search(r'(?<!<p>)\[\d+\]', html)
        found1 = re.search(r'\<p\>\[\d+\](.+)\<\/p\>', html)
        local_fnid1 = 0
        if found is not None:  # only once for each file with notes
            html = re.sub(
                r'\<\/head\>', r'<link href="../Styles/footnote.css" rel="stylesheet" type="text/css"/>\n</head>', html)
            html = re.sub(r'\<html.+\>\s*\<head\>',
                        r'<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="zh-CN" xmlns:epub="http://www.idpf.org/2007/ops">\n<head>', html)
            html = re.sub(
                r'\<\/body\>', r'<aside epub:type="footnote">\n<ol class="duokan-footnote-content">\n</ol>\n</aside>\n</body>', html)
        while found is not None:
            fnid = fnid + 1
            html = re.sub(r'(?<!<p>)\[\d+\]', r'<a class="duokan-footnote" epub:type="noteref" href="' + str(
                id) + '#fn' + str(fnid) + '" id="fnref' + str(fnid) + '"><img alt="" src="../Images/note.png"/></a>', html, 1)
            print(id, href, '' + str(fnid) + ':' + found.group(0).strip('[]^'))
            found = re.search(r'(?<!<p>)\[\d+\]', html)
        while found1 is not None:
            fnid1 = fnid1 + 1
            local_fnid1 = local_fnid1 + 1
            html = re.sub(r'\<p\>\[\d+\](.+)\<\/p\>', r'', html, 1)
            html = re.sub(r'\<\/ol\>', r'\n<li class="duokan-footnote-item" id="fn' + str(fnid1) + '">\n<p class="fn"><a href="' +
                          str(id) + '#fnref' + str(fnid1) + '">[' + str(local_fnid1) + ']</a> ' + found1.group(1).strip('[]^') + '​​​​​​​​</p></li>\n</ol>', html, 1)
            print(id, href, '' + str(fnid1) + ':' + found1.group(1))
            found1 = re.search(r'\<p\>\[\d+\](.+)\<\/p\>', html)
        else:
            print(id, href, "No notes found")
        if not html == html_original:
            bk.writefile(id, html)
        lastid = id
# css
    if fnid > 0:
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
  padding-left: 2em;
  -webkit-padding-start: 2em;
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
  margin-left: -1.5em;
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
