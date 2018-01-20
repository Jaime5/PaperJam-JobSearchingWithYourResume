#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""parse
"""

from __future__ import print_function, unicode_literals

from glob import glob
import json
from os import path

import pdftotext

PARSED_PATH = "output.txt"


def pdf_to_text(file_path, parsed_path=PARSED_PATH):

    print("Parsing \'%s\'..." % path.basename(file_path), end=" ")

    with open(file_path, "rb") as pdf_file:
        parsed_text = pdftotext.PDF(pdf_file)

    print("done")
    # print(" ".join(parsed_text))
    return " ".join(parsed_text)


def lsfile(*data_dir):

    return glob(path.join(*data_dir))


def dump_data(data, file_name):

    with open(file_name, "w") as out_file:
        json.dump(data, out_file)


if __name__ == '__main__':

    hard_coded_path = "../data/justin.pdf"
    pdf_to_text(hard_coded_path)
