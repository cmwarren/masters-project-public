# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient
import pymongo
import pandas as pd


class RankingAnalyzer:
    db_url = 'mongodb://localhost:27017/'

    def __init__(self, volume, metric, training_corpus, enrich_corpus, enrich_corpus_path):

        self.db_name = training_corpus + '-' + enrich_corpus
        self.enrich_corpus_path = enrich_corpus_path

        self.mongo_client = MongoClient(self.db_url)
        self.db = self.mongo_client.get_database(self.db_name)
        self.db.set_profiling_level(pymongo.SLOW_ONLY)

        self.volume = volume
        self.metric = metric

    def extract_word_counts(self, dir_path):
        if os.path.islink(dir_path):
            dir_path = os.readlink(dir_path)

        sentences_col = self.db['sentences']

        lang_prefixes = sentences_col.distinct('lang_prefix')

        df_word_counts = pd.DataFrame()

        for lang_prefix in lang_prefixes:
            word_count_list = []
            word_count_cursor = self.extract_word_counts_for_lang(lang_prefix)
            for result in word_count_cursor:
                word_count_list.append(int(result['word_count']))

            df_word_counts[lang_prefix] = word_count_list
            print('Finished processing language: ' + lang_prefix + '\n')

        df_word_counts.to_csv(dir_path + 'ranked-word-counts_' + self.metric + '.csv')

    def extract_word_counts_for_lang(self, lang_prefix):
        print('Starting to process language: ' + lang_prefix + '\n')

        sentences_col = self.db['sentences']
        word_counts = sentences_col.find({'lang_prefix': lang_prefix},
                       projection={'_id': False, 'word_count': True},
                       sort=[(self.metric, pymongo.DESCENDING)],
                       limit=self.volume,
                       batch_size=50)
        print('Got word counts for lang: ' + lang_prefix)

        return word_counts

    def run_extract(self):

        # Extract word counts from ranked_15000 sentences collection
        self.extract_word_counts(self.enrich_corpus_path)


if __name__ == '__main__':
    training_corpus = 'bible'
    enrich_corpus = 'wikipedia'
    volume = 15000
    output_dir = './data/ranked_15000/'
    metric = 'normalised_score'

    RankingAnalyzer(volume, metric, training_corpus, enrich_corpus, output_dir).run_extract()