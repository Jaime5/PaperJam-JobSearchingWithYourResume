#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""parse
"""

from __future__ import absolute_import, print_function, unicode_literals

from glob import glob
from os import path
import subprocess

from . import HTML_CONVERTED_OUT, HTML_CONVERTED_PATH, PARSED_PATH


def pdf_to_text(file_path, parsed_path=PARSED_PATH):

    print("Parsing \'%s\'..." % path.basename(file_path), end=" ")

    subprocess.call(["pdftotext", file_path, parsed_path])

    with open(parsed_path) as parsed_file:
        parsed_text = (
            line.decode("utf-8").strip() for line in parsed_file.readlines()
        )

    print("Done")
    return " ".join(parsed_text)


def pdf_to_html(file_path):

    if not path.exists(HTML_CONVERTED_OUT):
        subprocess.call(
            ["pdftohtml", "-s", "-c", "-q", file_path, HTML_CONVERTED_PATH]
        )

    with open(HTML_CONVERTED_OUT) as parsed_file:
        parsed_html = (
            line.decode("utf-8").strip() for line in parsed_file.readlines()
        )

    return parsed_html


def save_html(content, file_path="target_doc.html"):

    with open(file_path, "w") as html_file:
        html_file.write(content)


def lsfile(*data_dir):

    return glob(path.join(*data_dir))
