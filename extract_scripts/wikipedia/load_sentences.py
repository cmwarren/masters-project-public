# -*- coding: utf-8 -*-
import os
from os import listdir
from os.path import join
from pymongo import MongoClient
import pymongo
import hashlib
import threading
import time


class SentenceLoader:
    db_url = 'mongodb://localhost:27017/'

    def __init__(self, training_corpus, enrich_corpus, enrich_corpus_path):

        self.db_name = training_corpus + '-' + enrich_corpus
        self.enrich_corpus_path = enrich_corpus_path

        self.mongo_client = MongoClient(self.db_url)
        # self.mongo_client.drop_database(self.db_name)
        self.db = self.mongo_client.get_database(self.db_name)
        self.db.set_profiling_level(pymongo.SLOW_ONLY)

        progress_col = self.db.create_collection('progress')

        sentences_col = self.db.create_collection('sentences')
        # Mongo shell: db.sentences.createIndex({"sentence_id":1}, {name: "sentence_id", unique: true} )
        sentences_col.create_index([("sentence_id", pymongo.ASCENDING)], name='sentence_id', unique=True)
        # Mongo shell: db.sentences.createIndex({"lang_prefix": 1, "sentence_hash": 1},
        #                                       {name: "sentence_text", unique: true} )
        sentences_col.create_index([("lang_prefix", pymongo.ASCENDING), ("sentence_hash", pymongo.ASCENDING)],
                                   name='sentence_text', unique=True)
        # Mongo shell: db.sentences.createIndex({"lang_prefix": 1, "sentence_num": 1},
        #                                       {name: "sentence_num", unique: true} )
        sentences_col.create_index([("lang_prefix", pymongo.ASCENDING), ("sentence_num", pymongo.ASCENDING)],
                                   name='sentence_num', unique=True)

        pairs_col = self.db.create_collection('pairs')
        # Mongo shell: db.pairs.createIndex({"word":1}, {name: "word"} )
        pairs_col.create_index([("word", pymongo.TEXT)], name='word')
        # Mongo shell: db.pairs.createIndex({"sentence_id":1}, {name: "sentence_id"} )
        pairs_col.create_index([("sentence_id", pymongo.ASCENDING)], name='sentence_id')

    class ExtractFileThread(threading.Thread):
        def __init__(self, cls, instance, threadName, path, run_event):
            threading.Thread.__init__(self)
            self.cls = cls
            self.instance = instance
            self.threadName = threadName
            self.path = path
            self.run_event = run_event

        def run(self):
            self.cls.extract_file_to_db(self.instance, self.threadName, self.path, self.run_event)

    def extract_files_to_db(self, dir_path):
        if os.path.islink(dir_path):
            dir_path = os.readlink(dir_path)

        run_event = threading.Event()
        run_event.set()

        threads = []

        try:
            for idx, path in enumerate(
                    [join(dir_path, f) for f in listdir(dir_path) if f.endswith('en0.txt') and '_duplicates' not in f]):
                thread = self.ExtractFileThread(self.__class__, self, 'Thread' + str(idx), path, run_event)
                threads.append(thread)
                thread.start()

            while [thread.isAlive() for thread in threads]:
                time.sleep(5)

        except KeyboardInterrupt:
            print("attempting to close threads")
            run_event.clear()
            for thread in threads:
                thread.join()
            print("threads successfully closed")

    def extract_file_to_db(self, threadName, path, run_event):
        print('Thread: ' + threadName + '; Starting to process file: ' + path + '\n')
        language_prefix = path[-7:-4]

        with open(path) as fin:
            k = path.rfind(".")
            fdups_path = path[:k] + "_duplicates." + path[k + 1:]
            db_doc_count = 0
            progress_col = self.db['progress']
            sentences_col = self.db['sentences']
            pairs_col = self.db['pairs']

            for line_idx, line in enumerate(fin):

                # Break out of the loop if the parent thread has been stopped
                if not run_event.is_set():
                    break

                # Report file progress in console output
                if line_idx-1 % 500000 == 0:
                    print(path + ': file lines processed...', line_idx-1)

                # Check if we are re-running in catch-up mode
                progress = progress_col.find_one({'process': 'extract', 'path': path})

                # If we already got past this line in the file, continue
                if progress is not None and \
                        progress['count'] >= line_idx:
                    continue

                # Skip some bad data seen in the Spanish input file
                if '\t' not in line:
                    continue

                # Parse DB values from file line
                sentence_id, sentence_str = line.split('\t')
                sentence_num = int(sentence_id[5:])
                sentence_str = sentence_str.strip()

                # Make a unique hash of the sentence text to use as the unique index value in the DB
                sentence_hash = hashlib.md5(sentence_str.decode('utf-8').encode('utf-8')).hexdigest()

                try:
                    # Attempt to insert the sentence
                    sentences_col.insert_one({'sentence_id': sentence_id, 'lang_prefix': language_prefix,
                                              'sentence_text': sentence_str, 'sentence_hash': sentence_hash,
                                              'sentence_num': sentence_num})
                except pymongo.errors.DuplicateKeyError as err:

                    # Is the error due to duplicate sentence text?
                    if 'index: sentence_text' not in err.message:
                        # Failed for some other reason
                        # Try doing fix for duplicate sentence id

                        # Reallocate the sentence_id by incrementing highest id number found in DB
                        max_sentence_num = sentences_col.find_one({'lang_prefix': language_prefix},
                                                sort=[("sentence_num", pymongo.DESCENDING)])['sentence_num']
                        new_sentence_num = max_sentence_num + 1
                        new_sentence_id = sentence_id[0:5] + str(new_sentence_num)

                        try:
                            # Re-attempt to insert the sentence
                            sentences_col.insert_one({'sentence_id': new_sentence_id, 'lang_prefix': language_prefix,
                                                      'sentence_text': sentence_str, 'sentence_hash': sentence_hash,
                                                      'sentence_num': new_sentence_num})

                        except pymongo.errors.DuplicateKeyError as err:

                            # Fix hasn't worked - give up and report the error
                            print(err.message)
                            with open(fdups_path, 'a') as fdups:
                                fdups.write(sentence_id + '\t' + sentence_str + '\n')

                            # Record file progress and continue to next file line
                            progress_col.find_one_and_update({'process': 'extract', 'path': path},
                                                                  {'$set': {'count': line_idx}},
                                                                  upsert=True)
                            continue
                    else:
                        # Silent failure for duplicate sentence text
                        # Record file progress and continue to next file line
                        progress_col.find_one_and_update({'process': 'extract', 'path': path},
                                                              {'$set': {'count': line_idx}},
                                                              upsert=True)
                        continue

                # Insert to sentence collection has worked - now insert into pairs collection
                for word in sentence_str.split(' '):
                    doc = {'lang_prefix': language_prefix, 'word': word.lower(), 'sentence_id': sentence_id}
                    pairs_col.insert_one(doc)

                # Report DB progress in console output
                if db_doc_count % 500000 == 0:
                    print(path + ': DB writes...', db_doc_count)
                db_doc_count += 1

                # Record file progress and continue to next file line
                progress_col.find_one_and_update({'process': 'extract', 'path': path},
                                                      {'$set': {'count': line_idx}},
                                                      upsert=True)
        print('Thread: ' + threadName + '; Finished processing file: ' + path + '\n')

    def run_extract(self):

        # Create sentences & pairs collections from corpus files
        self.extract_files_to_db(self.enrich_corpus_path)


if __name__ == '__main__':
    SentenceLoader('bible', 'wikipedia','./data/').run_extract()