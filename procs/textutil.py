#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from dateutil import parser as date_parser
from nltk import pos_tag
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
import spotlight

lemma = WordNetLemmatizer()

host = "http://model.dbpedia-spotlight.org/en/annotate"


def penn_to_wn(tag):

    if tag in ("JJ", "JJR", "JJS"):
        return wn.ADJ

    elif tag in ("RB", "RBR", "RBS"):
        return wn.ADV

    elif tag in ("VB", "VBD", "VBG", "VBN", "VBP", "VBZ"):
        return wn.VERB

    return wn.NOUN


def normalize_text(content, ignore_terms=[]):

    norm_text = content.encode("ascii", "ignore")

    # offset: index offset for start of word.

    # similarityScore: uniqueness of word/link or relation of word.
    # basically keyword is not a synonym the higher the score

    # support: number of links supported with dbpedia, min threshold

    # surfaceForm: keyword itself
    # uri: the location of other data for the keyword.
    annotations = spotlight.annotate(host, norm_text, confidence=0.3,
                                     support=2)

    annotations = [i["surfaceForm"] for i in annotations]
    # from pprint import pprint
    # pprint(annotations)

    annotations = (
        word for word in annotations
        if not any([x in word for x in ignore_terms])
    )
    annotations = [word for word in annotations if not word.isdigit()]
    annotations = pos_tag(annotations)
    annotations = [
        lemma.lemmatize(word[0], penn_to_wn(word[-1]))
        for word in annotations
    ]

    time_filtered = []

    for word in annotations:
        try:
            if date_parser.parse(word):
                pass

        except (TypeError, ValueError):
            time_filtered.append(word)

    return " ".join(filter(None, time_filtered)).lower()
