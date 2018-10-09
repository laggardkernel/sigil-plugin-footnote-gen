#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2019, laggardkernel and the sigil-plugin-footnote-gen contributors
# SPDX-License-Identifier: MIT

from __future__ import unicode_literals, division, absolute_import, print_function
import os
import sys
import re
import chardet
import tkinter as tk
from tkinter import Tk, BOTH, StringVar, PhotoImage, IntVar
from tkinter.ttk import Frame, Button, Label, Entry, Checkbutton

try:
    from sigil_bs4 import BeautifulSoup, Comment
except:
    from bs4 import BeautifulSoup, Comment


isosx = sys.platform.startswith('darwin')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOM_DIR = os.path.join(BASE_DIR, 'custom')


class Dialog(Frame):
    global Cancel
    Cancel = True

    def __init__(self, parent, bk):
        # display the dialog box
        Frame.__init__(self, parent)
        self.parent = parent
        self.bk = bk
        self.initUI()

    def savevalues(self):
        global Cancel
        Cancel = False
        prefs = self.bk.getPrefs()
        prefs['kindle'] = self.kindle.get()
        prefs['ibooks'] = self.ibooks.get()
        prefs['anchorid'] = self.anchorid.get()
        prefs['fndefid'] = self.fndefid.get()
        prefs['backlink'] = self.backlink.get()
        if self.separate.get() == 1:
            prefs['notesource'] = self.notesource.get()
        else:
            prefs['notesource'] = ''
        self.bk.savePrefs(prefs)
        self.master.quit()
        self.master.destroy()

    def initUI(self):
        # define dialog box properties
        self.parent.title("Duokan Footnote Linker")
        self.pack(fill=BOTH, expand=1)

        # get preferences
        prefs = self.bk.getPrefs()

        # info
        infoLabel = Label(self, text="Additional compatibility: ")
        infoLabel.place(x=25, y=10)

        # compatibility check
        self.kindle = IntVar()
        # if 'kindle' in prefs:
        #     self.kindle.set(prefs['kindle'])
        # else:
        #     self.kindle.set(1)
        self.kindle.set(1)
        kindleCheck = Checkbutton(self, text="Kindle", variable=self.kindle)
        kindleCheck.place(x=40, y=30)

        self.ibooks = IntVar()
        # if 'ibooks' in prefs:
        #     self.ibooks.set(prefs['ibooks'])
        # else:
        #     self.ibooks.set(1)
        self.ibooks.set(1)
        ibooksCheck = Checkbutton(self, text="iBooks(macOS only)", variable=self.ibooks)
        ibooksCheck.place(x=150, y=30)

        # disable compatibility check temporarily
        # kindleCheck.config(state=tk.DISABLED)
        # ibooksCheck.config(state=tk.DISABLED)

        # footnote id prefix
        anchorIDLabel = Label(self, text="Anchor ID prefix: ")
        anchorIDLabel.place(x=25, y=60)
        self.anchorid = StringVar(None)
        if 'anchorid' in prefs:
            self.anchorid.set(prefs['anchorid'])
        else:
            self.anchorid.set('fnanchor-')
        anchorIDEntry = Entry(self, textvariable=self.anchorid)
        anchorIDEntry.place(x=150, y=60, width=85)

        # footnote definition id
        fndefIDLabel = Label(self, text="Definition ID prefix: ")
        fndefIDLabel.place(x=25, y=85)
        self.fndefid = StringVar(None)
        if 'fndefid' in prefs:
            self.fndefid.set(prefs['fndefid'])
        else:
            self.fndefid.set('fndef-')
        fndefIDEntry = Entry(self, textvariable=self.fndefid)
        fndefIDEntry.place(x=150, y=85, width=85)

        # backlink class
        backlinkLabel = Label(self, text="Backlink class: ")
        backlinkLabel.place(x=25, y=110)
        self.backlink = StringVar(None)
        if 'backlink' in prefs:
            self.backlink.set(prefs['backlink'])
        else:
            self.backlink.set('fnsymbol')
        backlinkEntry = Entry(self, textvariable=self.backlink)
        backlinkEntry.place(x=150, y=110, width=85)

        # Notes source location
        self.separate = IntVar()
        separateSourceCheck = Checkbutton(
            self, text="Footnote file: ", variable=self.separate
        )
        separateSourceCheck.place(x=5, y=135)

        self.notesource = StringVar()
        opf_guide_items = {}
        for ref_type, title, href in self.bk.getguide():
            opf_guide_items[ref_type] = href
        # look for notes guide item
        if 'notes' in opf_guide_items:
            print('Separate note source found from OPF guide according to semantics.')
            self.notesource.set(opf_guide_items['notes'])
            self.separate.set(1)
        noteSourceEntry = Entry(self, textvariable=self.notesource)
        noteSourceEntry.place(x=150, y=135, width=150)

        # OK and Cancel buttons
        cancelButton = Button(self, text="Cancel", command=self.quit)
        cancelButton.place(x=25, y=165)
        okButton = Button(self, text="OK", command=self.savevalues)
        okButton.place(x=150, y=165)


def run(bk):
    # set Tk parameters for dialog box
    root = Tk()
    root.geometry("320x200+400+400")
    app = Dialog(root, bk)
    if not isosx:
        icon_img = PhotoImage(
            file=os.path.join(bk._w.plugin_dir, bk._w.plugin_name, 'sigil.png')
        )
        root.tk.call('wm', 'iconphoto', root._w, icon_img)
    root.mainloop()

    if Cancel == True:
        print(
            'Plugin terminated by user.\nPlease click OK to close the Plugin Runner window.'
        )
        return -1

    # --------------------------------------
    # get preferences
    # --------------------------------------
    prefs = bk.getPrefs()

    # id prefix for <sup> footnote anchors
    fnanchor_id = prefs['anchorid']

    # id prefix for <p> footnote definitions
    fndef_id = prefs['fndefid']

    # class for <a> backlink numbers in footnote definitions file
    backlink_class = prefs['backlink']

    kindle_compat = prefs['kindle']
    ibooks_compat = prefs['ibooks']
    notesource = prefs['notesource']

    # debug mode
    if 'debug' not in prefs:
        prefs['debug'] = False
        bk.savePrefs(prefs)
    debug = prefs['debug']

    # get epub version number
    if bk.launcher_version() >= 20160102:
        epubversion = bk.epub_version()
    else:
        epubversion = BeautifulSoup(bk.get_opf(), 'lxml').find('package')['version']

    # -------------------------
    # footnote linking process
    # -------------------------
    template_anchor = '''<a class="duokan-footnote" href="#{fndef_id}{id}" id="{fnanchor_id}{id}"><img alt="" src="../Images/note.png"/></a>'''
    template_def = '''
	  <li class="duokan-footnote-item" id="{fndef_id}{id}">
		<a class="{backlink_class}" href="#{fnanchor_id}{id}">◎</a>{text}​​​​​​​​</li>\n</ol>'''
    if kindle_compat and ibooks_compat:
        template_anchor = '''<a style="text-decoration:none!important;color:black;" class="duokan-footnote" epub:type="noteref" href="#{fndef_id}{id}" id="{fnanchor_id}{id}"><img alt="" src="../Images/note.png"/></a>'''
        template_def = '''
	  <li class="duokan-footnote-item" id="{fndef_id}{id}">
		<p><a class="{backlink_class}" style="text-decoration:none!important;color:black;" href="#{fnanchor_id}{id}">◎</a>{text}​​​​​​​​</p></li>\n</ol>'''
    else:
        if kindle_compat:
            template_anchor = '''<a style="text-decoration:none!important;color:black;" class="duokan-footnote" href="#{fndef_id}{id}" id="{fnanchor_id}{id}"><img alt="" src="../Images/note.png"/></a>'''
            template_def = '''
		  <li class="duokan-footnote-item" id="{fndef_id}{id}">
			<p><a class="{backlink_class}" style="text-decoration:none!important;color:black;" href="#{fnanchor_id}{id}">◎</a>{text}​​​​​​​​</p></li>\n</ol>'''
        if ibooks_compat:
            template_anchor = '''<a class="duokan-footnote" epub:type="noteref" href="#{fndef_id}{id}" id="{fnanchor_id}{id}"><img alt="" src="../Images/note.png"/></a>'''
            template_def = '''
		  <li class="duokan-footnote-item" id="{fndef_id}{id}">
			<a class="{backlink_class}" style="color:black;" href="#{fnanchor_id}{id}">◎</a>{text}​​​​​​​​</li>\n</ol>'''

    anchor_count = 0
    def_count = 0
    pattern_anchor = re.compile(r'(?<!<p>)\[\d+\]')
    pattern_def = re.compile(r'\<p\>\[\d+\](.+)\<\/p\>')

    # validate note source
    note_html = None
    note_html_original = note_html
    if notesource:
        if not notesource.startswith('Text/'):
            notesource = 'Text/' + notesource
        temp_list = [opf_href for (manifest_id, linear, opf_href) in bk.spine_iter()]
        if notesource in temp_list:
            iter_list = [
                (manifest_id, linear, opf_href)
                for (manifest_id, linear, opf_href) in bk.spine_iter()
                if opf_href != notesource
            ]
            note_html = bk.readfile(bk.href_to_id(notesource))
    else:
        iter_list = list(bk.spine_iter())

    for (manifest_id, linear, opf_href) in iter_list:
        print('-' * 20, opf_href, '-' * 20)
        html = bk.readfile(manifest_id)
        html_original = html

        note_anchor = re.search(pattern_anchor, html)
        if note_anchor is not None:  # only once for each file with notes
            html = re.sub(
                r'\<\/head\>',
                r'<link href="../Styles/footnote.css" rel="stylesheet" type="text/css"/>\n</head>',
                html,
            )

            if ibooks_compat:
                html = re.sub(
                    r'\<\/body\>',
                    r'<aside epub:type="footnote">\n<ol class="duokan-footnote-content">\n</ol>\n</aside>\n</body>',
                    html,
                )
                soup = BeautifulSoup(html, 'html.parser')
                soup.html['xmlns:epub'] = 'http://www.idpf.org/2007/ops'
                bk.writefile(manifest_id, str(soup))
                del soup
                # update html string
                html = bk.readfile(manifest_id)
                html_original = html
            else:
                html = re.sub(
                    r'\<\/body\>',
                    r'<ol class="duokan-footnote-content">\n</ol>\n</body>',
                    html,
                )

            local_count = 0
            while note_anchor is not None:
                anchor_count = anchor_count + 1
                local_count += 1
                template = template_anchor.format(
                    id=anchor_count, fnanchor_id=fnanchor_id, fndef_id=fndef_id
                )
                html = re.sub(pattern_anchor, template, html, 1)
                print(
                    'Anchor No.'
                    + str(anchor_count)
                    + ': '
                    + note_anchor.group(0).strip('[]^')
                )
                note_anchor = re.search(pattern_anchor, html)

            if note_html:
                note_def = re.search(pattern_def, note_html)
                for i in range(1, local_count + 1):
                    def_count = def_count + 1
                    note_html = re.sub(pattern_def, r'', note_html, 1)
                    template = template_def.format(
                        id=def_count,
                        text=note_def.group(1).strip('[]^'),
                        fnanchor_id=fnanchor_id,
                        fndef_id=fndef_id,
                        backlink_class=backlink_class,
                    )
                    html = re.sub(r'\<\/ol\>', template, html, 1)
                    print('Note No.' + str(def_count) + ': ' + note_def.group(1))
                    note_def = re.search(pattern_def, note_html)
            else:
                note_def = re.search(pattern_def, html)
                while note_def is not None:
                    def_count = def_count + 1
                    html = re.sub(pattern_def, r'', html, 1)
                    template = template_def.format(
                        id=def_count,
                        text=note_def.group(1).strip('[]^'),
                        fnanchor_id=fnanchor_id,
                        fndef_id=fndef_id,
                        backlink_class=backlink_class,
                    )
                    html = re.sub(r'\<\/ol\>', template, html, 1)
                    print('Note No.' + str(def_count) + ': ' + note_def.group(1))
                    note_def = re.search(pattern_def, html)
        else:
            print("No note is found")

        if not html == html_original:
            bk.writefile(manifest_id, html)

    if not note_html == note_html_original:
        bk.writefile(bk.href_to_id(notesource), note_html)
        print(
            '\nInfo: Remember to delete footnote source file %s manually.' % notesource
        )

    insert_note_css(bk, backlink_class=backlink_class)

    print(
        "\nInfo: Footnote generation succeeded, after which you'd better beautify all text files."
    )
    return 0


def insert_note_css(bk, filename='footnote.css', backlink_class='fnsymbol'):
    basename = filename
    uid = "footnotecss"
    mime = "text/css"

    # try to load custom footnote.css added by user,
    # fallback to built-in footnote.css file when attempt failed
    backlink_class_flag = False
    footnote_css = os.path.join(CUSTOM_DIR, filename)
    if os.path.exists(footnote_css):
        print('Info: custom css file is used.')
    else:
        footnote_css = os.path.join(BASE_DIR, filename)
        backlink_class_flag = True

    encoding = _get_file_encoding(footnote_css)
    with open(footnote_css, 'r', encoding=encoding) as f:
        data = f.read()
    if backlink_class_flag:
        data = re.sub(r'a\.fnsymbol', r'a.{}'.format(backlink_class), data)

    bk.addfile(uid, basename, data, mime)
    return 0


def _get_file_encoding(filename):
    with open(filename, 'rb') as f:
        encoding = chardet.detect(f.read())
    return encoding['encoding']


def main():
    print("I reached main when I should not have\n")
    return -1


if __name__ == "__main__":
    sys.exit(main())
