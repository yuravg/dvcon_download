#!/usr/bin/env python

import io
import os
import sys
import datetime

# support Python version <3
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

"""
install PyPDF2 with pip:
$ pip install pypdf2
"""
from PyPDF2 import PdfFileReader


FNAME = 'index.html'


def write2file(fname, s, info="Write file: "):
    """Write output file."""
    try:
        f = io.open(fname, 'w')
        f.write(s)
        f.close()
        if info:
            print('%s%s' % (info, fname))
    except Exception:
        sys.exit("ERROR! Can not write file: '%s'!\nExit from program!" % fname)


class HtmlData(object):
    """Prepare html page"""

    def __init__(self, title=""):
        """insert html title"""
        self.title = """<html>
<head>%s</head>
<body>\n""" % title
        self.content = ""
        self.end = """</body>
</html>\n"""

    def __str__(self):
        """return Page content as string"""
        return "%s%s%s" % (self.title, self.content, self.end)

    def __add__(self, text):
        """add text to page content"""
        self.content = '%s%s' % (self.content, text)

    def add_heading(self, text, level=1):
        """insert html heading"""
        head = "<h%d>%s</h%d>\n" % (level, text, level)
        self.__add__(head)

    def add_paragraph(self, text):
        """insert html paragraph"""
        body = "<p>%s</p>\n" % text
        self.__add__(body)

    def add_link(self, url, text):
        """insert link to page content"""
        link = """<a href="%s">%s</a>""" % (url, text)
        self.add_paragraph(link)


class OrgData(object):
    """Prepare org-mode data"""
    def __init__(self, title=""):
        self.data = "%s\n\n" % title

    def __str__(self):
        """return org-mode data as string"""
        return self.data

    def __add__(self, text):
        """add text to org-mode data"""
        self.data = "%s%s" % (self.data, text)

    def add_text(self, text):
        self.__add__("%s\n" % text)

    def add_level(self, text, level=1):
        """insert org-mode level"""
        lev = "%s %s\n" %("*"*level, text)
        self.__add__(lev)

    def add_link(self, url, text):
        """insert link to org-mode"""
        link = "[[file:%s][%s]]\n" % (url, text)
        self.__add__(link)


def extract_pdf_information(pdf_path):
    """
    Author: {information.author}
    Creator: {information.creator}
    Producer: {information.producer}
    Subject: {information.subject}
    Title: {information.title}
    Number of pages: {number_of_pages}
    """
    try:
        with open(pdf_path, 'rb') as f:
            pdf = PdfFileReader(f)
            information = pdf.getDocumentInfo()
            number_of_pages = pdf.getNumPages()
        return information
    except Exception:
        print('Can not get information from file: %s' % pdf_path)


def extract_pdf_lines(pdf_path):
    """Extract lines from pdf file"""
    text = ""
    empty_line = False
    try:
        with open(pdf_path, 'rb') as f:
            pdf = PdfFileReader(f)
            page = pdf.getPage(0).extractText()
            buf = StringIO(page)
            for _ in range(20):
                rdata = buf.readline()
                if rdata == " \n":
                    if empty_line:
                        break
                    empty_line = True
                else:
                    empty_line = False
                text = '%s%s' % (text, rdata)
    except Exception:
        print('Can not get lines from file: %s' % pdf_path)
    text = text.replace('\n', '')
    return text


def get_files_list(dir_name):
    """For the given path, get the List of all files in the directory tree"""
    file_list = os.listdir(dir_name)
    files = list()
    for i in file_list:
        full_path = os.path.join(dir_name, i)
        if os.path.isdir(full_path):
            files = files + getListOfFiles(full_path)
        else:
            files.append(full_path)
    return files


class BuildIndexFiles(object):
    """Build index files"""
    def __init__(self, title):
        self.html = HtmlData(title)
        self.org  = OrgData(title)

    def add_header(self, header):
        self.html.add_heading(header)
        self.org.add_level(header)

    def add_link(self, url, text):
        self.html.add_link(url, text)
        self.org.add_link(url, text)

    def save_files(self):
        html_fname = "index.html"
        write2file(html_fname, str(self.html))
        org_fname = "index.org"
        write2file(org_fname, str(self.org))


def main():
    time = "%s" % datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    index = BuildIndexFiles("DVCON")

    dirs = ["_2019"]
    for d in dirs:
        files = get_files_list(d)
        index.add_header(d)
        for f in files:
            info = extract_pdf_information(f)
            index.add_link(f, info.title)
            lines = extract_pdf_lines(f)
            print('* file(%s): %s' % (f, lines))
    index.save_files()


# run point
if __name__ == '__main__':
    main()
