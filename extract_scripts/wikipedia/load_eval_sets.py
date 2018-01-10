# -*- coding: utf-8 -*-
import os
from os import listdir
from os.path import join
from pymongo import MongoClient
import pymongo

class WiktionaryEvalLoader:

    db_url = 'mongodb://localhost:27017/'

    def __init__(self, training_corpus, enrich_corpus, eval_corpus_path):

        self.db_name = training_corpus + '-' + enrich_corpus
        self.eval_corpus_path = eval_corpus_path

        self.mongo_client = MongoClient(self.db_url)
        # self.mongo_client.drop_database(self.db_name)
        self.db = self.mongo_client.get_database(self.db_name)
        self.db.set_profiling_level(pymongo.SLOW_ONLY)

        eval_col = self.db.create_collection('eval_set')

    def extract_files_to_db(self, dir_path):
        if os.path.islink(dir_path):
            dir_path = os.readlink(dir_path)

        eval_col = self.db['eval_set']

        for idx, path in enumerate(
                [join(dir_path, f) for f in listdir(dir_path) if f.endswith('enwiktionary.txt')]):
            print('Starting to process file: ' + path + '\n')

            k = path.rfind('/') + 1
            src_lang_prefix = path[k+3:k+5]
            trg_lang_prefix = path[k:k+2]

            with open(path) as fin:

                for line_idx, line in enumerate(fin):

                    # Report file progress in console output
                    if line_idx - 1 % 1000 == 0:
                        print(path + ': file lines processed...', line_idx - 1)

                    # Parse DB values from file line
                    src_word, trg_word = line.split('|||')
                    src_word = src_word.strip()
                    trg_word = trg_word.strip()

                    # Skip some bad data
                    if src_word == '::' or trg_word == '::':
                        continue

                    eval_col.insert_one({'src': {'word': src_word, 'lang_prefix': src_lang_prefix},
                                        'trg': {'word': trg_word, 'lang_prefix': trg_lang_prefix}})

    def run_load(self):

        # Create eval collection from evaluation corpus files
        self.extract_files_to_db(self.eval_corpus_path)

if __name__ == '__main__':
    WiktionaryEvalLoader('bible', 'wikipedia', '../../levy_xling_embeddings/eval_data/wiktionary/').run_load()