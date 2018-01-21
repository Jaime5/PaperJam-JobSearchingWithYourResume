#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import json

import requests
from bs4 import BeautifulSoup


BASE_URL = "https://jobs.github.com/positions/{id}.json"


def send_request(url):

    req = requests.get(url)
    return json.loads(req.text)


def make_url(id):

    response = send_request(BASE_URL.format(id=id))

    soup = BeautifulSoup(response["description"], "html.parser")

    with open("job_desc.txt", "w") as dump_file:
        dump_file.write(soup.get_text().encode("utf-8"))


if __name__ == '__main__':

    make_url("d0be3b58-fdb4-11e7-88d4-1343d07cffc8")
