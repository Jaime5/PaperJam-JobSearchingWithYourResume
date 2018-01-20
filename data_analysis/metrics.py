#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import json
from os import path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from plots import plot_tfidf
from textio import pdf_to_text, lsfile
from textutil import normalize_text


class ScoreDoc(object):

    def __init__(self, doc_path, corpora, corpus_path):

        self.corpus = []
        self.train_resumes = []
        self.tfidf_matrix = None
        self.feature_names = None

        for corpus in corpora:
            if not path.exists(path.join(corpus_path, corpus)):
                raise IOError("No files found in corpus \"{}\"".format(corpus))

            print(lsfile(corpus_path, corpus))
            self.train_resumes.extend(lsfile(corpus_path, corpus))

        for resume_file_path in self.train_resumes:
            with open(resume_file_path) as resume_file:
                self.corpus.append(resume_file.read())

        self.train_resumes = [
            i.replace(corpus_path, "") for i in self.train_resumes
        ]

        self.resume = [pdf_to_text(doc_path)]

    def generate_tfidf(self, ignore_terms=[], max_feats=None,
                       ngram_range=(1, 2), stop_words=None):

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

    def get_score(self, top_docs=5, top_tfidf=0):

        # find the cosine similarity between the target doc with corpus
        cos_sim = linear_kernel(
            self.tfidf_matrix[:1], self.tfidf_matrix).flatten()[1:]

        resume_names = []

        #  if corpus contains multiple documents
        if (len(self.train_resumes) > 1):

            # get the 'top' docs with highest cosine similarity
            top_indices = cos_sim.argsort()[:-(top_docs + 1):-1]

            resume_names = np.asarray(self.train_resumes)
            resume_names = list(resume_names[top_indices])
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
        tfidf_scores_feats = dict(
            (self.feature_names[i], s) for (i, s) in tfidf_scores
        )

        if (not top_tfidf):

            return {
                "cos_sim": list(cos_sim),
                "top_docs": resume_names,
                "tfidf_scores": tfidf_scores_feats,
            }

        top_scores = sorted(set(tfidf_scores_feats.values()),
                            reverse=True)[:top_tfidf]
        top_tfidf_scores_feats = {
            i: v for i, v in tfidf_scores_feats.items() if v in top_scores
        }

        return {
            "cos_sim": list(cos_sim),
            "top_docs": resume_names,
            "tfidf_scores": top_tfidf_scores_feats,
        }

    def dump_data(self, data, file_name="resume_scores.json"):

        with open(file_name, "w") as out_file:
            json.dump(data, out_file)


if __name__ == '__main__':

    corpora = ["test.txt"]
    doc_path = "../data/sabbir.pdf"

    # Locations
    IGNORE_TERMS = ["baltimore", "md", "maryland"]

    # Names
    IGNORE_TERMS += [
        "sabbir", "ahmed", "justin", "chavez", "jaime", "orellana"
    ]

    obj = ScoreDoc(doc_path, corpora, ".")
    obj.generate_tfidf(stop_words="english", ignore_terms=IGNORE_TERMS)
    tfidf_data = obj.get_score(top_tfidf=5)

    plot_tfidf(tfidf_data)
