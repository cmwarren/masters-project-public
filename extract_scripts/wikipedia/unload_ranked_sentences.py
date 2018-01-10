# -*- coding: utf-8 -*-
import os
from pymongo import MongoClient
import pymongo
import codecs


class SentenceUnloader:
    db_url = 'mongodb://localhost:27017/'

    def __init__(self, sentences_per_lang, ranked_by, training_corpus, enrich_corpus, enrich_corpus_path):

        self.db_name = training_corpus + '-' + enrich_corpus
        self.enrich_corpus_path = enrich_corpus_path

        self.mongo_client = MongoClient(self.db_url)
        self.db = self.mongo_client.get_database(self.db_name)
        self.db.set_profiling_level(pymongo.SLOW_ONLY)

        self.sentences_per_lang = sentences_per_lang
        self.ranked_by = ranked_by

    def extract_db_to_files(self, dir_path):
        if os.path.islink(dir_path):
            dir_path = os.readlink(dir_path)

        sentences_col = self.db['sentences']

        lang_prefixes = sentences_col.distinct('lang_prefix')

        for idx, lang_prefix in enumerate(lang_prefixes):
            self.extract_db_to_file(lang_prefix, dir_path)

    def extract_db_to_file(self, lang_prefix, dir_path):
        print('Starting to process language: ' + lang_prefix + '\n')

        sentences_col = self.db['sentences']
        sentences = sentences_col.find({'lang_prefix': lang_prefix},
                       projection={'_id': False, 'sentence_id': True, 'sentence_text': True},
                       sort=[(self.ranked_by, pymongo.DESCENDING)],
                       limit=self.sentences_per_lang,
                       batch_size=50)
        print('Got sentences')

        line_idx = 0
        for sentence in sentences:

            with codecs.open(dir_path + lang_prefix + '.txt', 'a', encoding='utf-8', errors='replace') as out_file:

                out_file.write(sentence['sentence_id'] + '\t' + sentence['sentence_text'] + '\n')

            # Report file progress in console output
            if line_idx % 10000 == 0:
                print(lang_prefix + ': file lines written...', line_idx)
            line_idx += 1

        print('Finished processing language: ' + lang_prefix + '\n')

    def run_extract(self):

        # Extract corpus files from ranked_15000 sentences collection
        self.extract_db_to_files(self.enrich_corpus_path)


if __name__ == '__main__':
    SentenceUnloader(1500000, 'score', 'bible', 'wikipedia', './data/ranked_1500000/').run_extract()