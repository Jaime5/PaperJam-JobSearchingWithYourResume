#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import json
from os import path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from . import BUZZWORDS
from .textio import lsfile, pdf_to_text
from .textutil import normalize_text


class ScoreDoc(object):

    def __init__(self, doc_path, corpora, corpus_path):

        self.corpus = []
        self.train_resumes = []
        self.tfidf_matrix = None
        self.feature_names = None

        for corpus in corpora:
            if not path.exists(path.join(corpus_path, corpus)):
                raise IOError("No files found in corpus \"{}\"".format(corpus))

            self.train_resumes.extend(lsfile(corpus_path, corpus, "*.txt"))

        for resume_file_path in self.train_resumes:
            with open(resume_file_path) as resume_file:
                self.corpus.append(resume_file.read())

        self.train_resumes = [
            i.replace(corpus_path, "") for i in self.train_resumes
        ]

        self.resume = [pdf_to_text(doc_path)]

        self.buzzwords = {}
        with open(BUZZWORDS) as buzzwords_file:
            self.buzzwords = json.load(buzzwords_file)

    def generate_tfidf(self, ignore_terms=[], max_feats=None,
                       ngram_range=(1, 3), stop_words=None):

        tfidf = TfidfVectorizer(
            preprocessor=lambda x: normalize_text(
                x, ignore_terms=ignore_terms
            ),
            max_features=max_feats,
            ngram_range=ngram_range,
            stop_words=stop_words,
        )

        self.tfidf_matrix = tfidf.fit_transform(self.resume + self.corpus)
        self.feature_names = tfidf.get_feature_names()

    def get_score(self, file_name="resume_scores.json", top=5):

        cos_sim = linear_kernel(
            self.tfidf_matrix[:1], self.tfidf_matrix).flatten()[1:]
        top_indicies = cos_sim.argsort()[:-(top + 1):-1]

        resume_names = np.asarray(self.train_resumes)
        resume_names = list(resume_names[top_indicies])
        resume_names = [
            {
                "index": i,
                "label": j.split("/")[1],
                "name": j.split("/")[-1],
            } for i, j in enumerate(resume_names)
        ]

        feature_index = self.tfidf_matrix[0].nonzero()[1]
        tfidf_scores = zip(
            feature_index, (self.tfidf_matrix[0, i] for i in feature_index)
        )
        tfidf_scores_features = dict(
            (self.feature_names[i], s) for (i, s) in tfidf_scores
        )

        buzzwords = dict(
            (self.feature_names[i], self.is_buzzword(self.feature_names[i]))
            for (i, _) in tfidf_scores
        )
        buzzwords = {k: v for k, v in buzzwords.iteritems() if v}

        data = {
            "top_docs": resume_names,
            "tfidf_scores": tfidf_scores_features,
            "buzzwords": buzzwords,
        }

        with open(file_name, "w") as out_file:
            json.dump(data, out_file)

    def is_buzzword(self, term):

        for category, buzzwords_list in self.buzzwords.items():
            for buzzword in buzzwords_list:
                buzzword = buzzword.split() + [buzzword]
                if term in buzzword:
                    return category
