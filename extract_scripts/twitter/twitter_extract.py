
# -*- coding: utf-8 -*-
import twitter_client as tc
import codecs
import os
import json
import sys


class TwitterExtractor:

    path = '../../levy_xling_embeddings/bible/wiktionary-eval/'
    en_lang_code = 'en'
    #lang_codes = {'ar': 0, 'en': 0, 'es': 0, 'fi': 0, 'fr': 0, 'he': 0, 'hu': 0, 'pt': 0, 'tr': 0}
    lang_codes = {'en': 0, 'es': 0, 'fi': 0, 'fr': 0}
    prefixes = ['oov', 'inv']
    progress_tracker = None

    def __init__(self):
        self.tc = tc.MyTwitterApiClient()

        self.deserialize_progress_tracker()

    def __del__(self):
        # TODO - Make this thread-safe?  Would need to serialize again each time count is incremented
        self.serialize_progress_tracker()

    def deserialize_progress_tracker(self):
        # Deserialize progress tracker state
        try:
            with open('./progress_tracker.txt', 'r') as f:
                self.progress_tracker = json.load(f)
        except (IOError, EOFError):
            self.init_progress_tracker()

        if self.progress_tracker is None:
            self.init_progress_tracker()

    def serialize_progress_tracker(self):
        # Serialize progress_tracker state
        with open('./progress_tracker.txt', 'w') as f:
            json.dump(self.progress_tracker, f)

    def init_progress_tracker(self):
        # Set up progress tracker for the first time
        self.progress_tracker = dict()

    def extract_tweets(self):

        foreign_lang_codes = self.lang_codes.keys()
        foreign_lang_codes.remove(self.en_lang_code)
        for foreign_lang_code in foreign_lang_codes:
            #self.extract_tweets_for_lang_pair(self.en_lang_code, foreign_lang_code)
            self.extract_tweets_for_lang_pair(foreign_lang_code, self.en_lang_code)

    def extract_tweets_for_lang_pair(self, src_lang, tgt_lang):

        print('########### Starting language pair - source: ' + src_lang + ' target: ' + tgt_lang + ' ###########')
        sent_counter = self.lang_codes[tgt_lang]
        for prefix in self.prefixes:
            print('######## ' + prefix.upper() + ' ########')
            in_filename = self.path + prefix + '-' + src_lang + '-' + tgt_lang + '.txt'
            progress_key = src_lang + '-' + tgt_lang + '-' + prefix

            out_dir = './data/' + prefix

            if not os.path.exists(out_dir):
                os.mkdir(out_dir)

            out_filename = out_dir + '/' + tgt_lang + '0.txt'
            missing_filename = out_dir + '/missing-' + tgt_lang + '0.txt'

            if progress_key in self.progress_tracker:
                if self.progress_tracker[progress_key]['word-count'] != 0:
                    sent_counter = self.progress_tracker[progress_key]['sentence-count']
            else:
                self.progress_tracker[progress_key] = {'word-count': 0, 'sentence-count': sent_counter}
                if sent_counter == 0:
                    # Clear down any previous version of the output file
                    if os.path.isfile(out_filename):
                        os.remove(out_filename)
                    if os.path.isfile(missing_filename):
                        os.remove(missing_filename)

            words = [(l.split("|||")[-1].strip(), l.split("|||")[0].strip())
                     for l in codecs.open(in_filename, encoding='utf-8', errors='replace').readlines()]

            missing_file = codecs.open(missing_filename, 'a', encoding='utf-8', errors='replace')

            try:
                word_count = 0
                no_results_count = 0
                for tgt_word, src_word in words:

                    if word_count <= self.progress_tracker[progress_key]['word-count']:
                        word_count += 1
                        continue

                    # Skip over some noisy data in the eval set
                    # fi, hu, pt - all seem to have a lot of this?
                    if tgt_word == '::':
                        word_count += 1
                        continue

                    print('### ' + tgt_word + ' ### ' + str(word_count) + ' of ' + str(len(words)))
                    [b_tweets_output, sent_counter] = self.tc.output_tweets(lang_code=tgt_lang, query=tgt_word, filename=out_filename, sent_counter=sent_counter)
                    if not b_tweets_output:
                        no_results_count += 1
                        # Capture a list of queries that didn't match any tweets
                        missing_file.write(tgt_word + '\n')
                        print('No results found - count: ' + str(no_results_count))

                    word_count += 1
                    self.progress_tracker[progress_key]['word-count'] = word_count
                    self.progress_tracker[progress_key]['sentence-count'] = sent_counter
                    self.serialize_progress_tracker()
                    self.lang_codes[tgt_lang] = sent_counter

            except:
                print "Unexpected error:", sys.exc_info()[0]
                raise
            finally:
                missing_file.close()
            print('No results found for ' + str(no_results_count) + ' of ' + str(word_count) + ' words')


def main():
    extractor = TwitterExtractor()
    extractor.extract_tweets()


if __name__ == "__main__":
    main()
