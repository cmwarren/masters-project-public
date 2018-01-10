from bs4 import BeautifulSoup
import codecs
import re
import os
import nltk.data
from wikitools import api
from wikitools import wiki
from nltk.tokenize import word_tokenize
import json


class WikipediaExtract:

    RE = re.compile(r"""
        \[[\d]+?\]  | # Match reference citations e.g. [4]
        """, re.VERBOSE)
    pages_per_lang = 1000

    # lang_codes = {'ar': 0, 'en': 0, 'es': 0, 'fi': 0, 'fr': 0, 'he': 0, 'hu': 0, 'pt': 0, 'tr': 0}
    lang_codes = {'en': 0, 'es': 0, 'fi': 0, 'fr': 0}
    en_lang_code = 'en'
    wiktionary_path = '../../levy_xling_embeddings/bible/wiktionary-eval/'
    #prefixes = ['oov', 'inv']
    prefixes = ['oov']
    progress_tracker = None

    sites = dict()

    sent_detectors = {
        'en': nltk.data.load('tokenizers/punkt/english.pickle'),
        'es': nltk.data.load('tokenizers/punkt/spanish.pickle'),
        'fi': nltk.data.load('tokenizers/punkt/finnish.pickle'),
        'fr': nltk.data.load('tokenizers/punkt/french.pickle'),
        'hu': nltk.data.load('tokenizers/punkt/hungarian.pickle'),  # Downloaded from github: mhq/train_punkt
        'pt': nltk.data.load('tokenizers/punkt/portuguese.pickle'),
        'tr': nltk.data.load('tokenizers/punkt/turkish.pickle')
        # Arabic & Hebrew trained tokenizers not available...
    }

    def __init__(self):

        for site_lang_code in self.lang_codes.keys():
            self.sites[site_lang_code] = wiki.Wiki('https://' + site_lang_code + '.wikipedia.org/w/api.php')

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

    def get_random_page_ids_for_lang(self, lang_code):

        # Call the API to get a random sample of page ids
        site = self.sites[lang_code]

        # API allows random page_ids to be retrieved max 500 at a time
        page_ids = []
        params = {'action': 'query', 'generator': 'random', 'grnnamespace': '0',
                  'grnlimit': 500, 'prop': 'info'}
        for i in range(0, int(self.pages_per_lang/500)):
            request = api.APIRequest(site, params)
            result = request.query()
            page_ids.extend(result['query']['pages'].keys())

        if self.pages_per_lang % 500 > 0:
            params['grnlimit'] = self.pages_per_lang % 500
            request = api.APIRequest(site, params)
            result = request.query()
            page_ids.extend(result['query']['pages'].keys())

        return page_ids

    def query_page_ids_for_lang(self, query, lang_code):

        # Call the API to query a sample of page ids
        site = self.sites[lang_code]

        # API allows page_ids to be retrieved max 500 at a time
        page_ids = []
        params = {'action': 'query', 'generator': 'search', 'gsrwhat': 'text',
                  'gsrsearch': query, 'grnlimit': 10, 'prop': 'info'}

        request = api.APIRequest(site, params)
        result = request.query()
        if 'query' in result:
            if 'pages' in result['query']:
                page_ids = result['query']['pages'].keys()
        print ('page_ids: ' + str(page_ids))
        if page_ids is None:
            page_ids = []

        return page_ids

    def output_page_ids(self, page_ids, subdir, lang_code, progress_key, b_output_raw=False):
        # Generate a name for the output file
        out_dir = './' + subdir
        filename = out_dir + '/' + lang_code + '0.txt'

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        # Clear down any previous version of the output file
        if os.path.isfile(filename):
            if self.lang_codes[lang_code] == 0:
                os.remove(filename)

        # Prepare an output file
        out_file = codecs.open(filename, 'a', encoding='utf-8', errors='replace')

        # Optionally, for testing purposes, output the <p> tag content
        ptag_file = None
        if b_output_raw:
            ptag_path = './' + subdir + '/p-tags'

            if not os.path.exists(ptag_path):
                os.mkdir(ptag_path)

            filename_p = ptag_path + '/wikipedia-' + lang_code + '.txt'

            # Clear down any previous version of the output file
            if os.path.isfile(filename_p):
                os.remove(filename_p)

            ptag_file = codecs.open(filename_p, 'a', encoding='utf-8', errors='replace')

        for index, page_id in enumerate(page_ids):
            self.output_page_id(page_id, out_file, subdir, lang_code, index, progress_key, b_output_raw, ptag_file)

        out_file.close()
        if b_output_raw:
            ptag_file.close()

    def output_page_id(self, page_id, out_file, subdir, lang_code, index, progress_key, b_output_raw=False, ptag_file=None):

        print(str(index) + ': ' + page_id + ' --> ' + out_file.name)
        sent_counter = self.lang_codes[lang_code]

        # Call the API to get the page content - will be in HTML
        params = {'action': 'parse', 'pageid': page_id, 'prop': 'text', 'contentmodel': 'wikitext',
                  'contentformat': 'text/plain'}

        site = self.sites[lang_code]
        request = api.APIRequest(site, params)
        result = request.query()
        content = result['parse']['text']['*']

        # Optionally, for testing purposes, output the raw content
        if b_output_raw:
            raw_path = './' + subdir + '/raw'
            if not os.path.exists(raw_path):
                os.mkdir(raw_path)
            filename_raw = raw_path + '/wikipedia-' + lang_code + '-' + str(index) + '.txt'
            print(page_id + ' --> ' + filename_raw)
            f_raw = codecs.open(filename_raw, 'w', encoding='utf-8', errors='replace')
            f_raw.write(content)
            f_raw.close()

        # Extract only the <p> tags from the HTML
        soup = BeautifulSoup(content, 'html.parser')
        soup_p_tags = soup.find_all('p')
        p_text = [p_tag.get_text() for p_tag in soup_p_tags]

        for paragraph in p_text:

            if b_output_raw and ptag_file is not None:
                ptag_file.write(paragraph + '\n')

            # Skip any empty <p> tags
            if paragraph == '':
                continue

            # Remove all line breaks - we want to end up with one whole sentence per line
            # i.e. remove intra-sentence line breaks, then replace inter-sentence line breaks
            paragraph = paragraph.replace('\n', ' ')

            # Use Punkt tokenizer to segment the paragraph into sentences
            try:
                sent_detector = self.sent_detectors[lang_code]
                sentences = sent_detector.tokenize(paragraph)

            except KeyError as e:
                # Punkt tokenizer not available for this language - make do without...
                sentences = [paragraph]
                pass

            for sentence in sentences:
                # Strip out any remaining markup using regex
                # Strip leading/trailing whitespace
                sentence = self.strip_markup(sentence).strip()
                # Remove unicode zero-width spaces
                sentence = sentence.replace(u'\u200b', '')

                # If this leaves a blank sentence, then skip to next
                if sentence == '':
                    continue

                # Tokenize and append to the output file
                tokens = word_tokenize(sentence)

                out_file.write('wp_' + lang_code + str(sent_counter) + '\t' + ' '.join(tokens).lower() + '\n')

                sent_counter += 1

        self.lang_codes[lang_code] = sent_counter
        self.progress_tracker[progress_key]['sentence-count'] = sent_counter

    def strip_markup(self, content):
        return self.RE.sub('', content)

    def search_for_wiktionary_eval_words(self, prefix, src_lang, tgt_lang):

        print('########### Starting language pair - source: ' + src_lang + ' target: ' + tgt_lang + ' ###########')

        in_filename = self.wiktionary_path + prefix + '-' + src_lang + '-' + tgt_lang + '.txt'
        progress_key = src_lang + '-' + tgt_lang + '-' + prefix

        out_filename = './data/search_results/' + prefix + '/' + tgt_lang + '0.txt'
        missing_filename = './data/search_results/' + prefix + '/missing-' + tgt_lang + '0.txt'

        if progress_key in self.progress_tracker:
            if self.progress_tracker[progress_key]['word-count'] != 0:
                sent_counter = self.progress_tracker[progress_key]['sentence-count']
        else:
            self.progress_tracker[progress_key] = {'word-count': 0, 'sentence-count': self.lang_codes[tgt_lang]}
            if self.lang_codes[tgt_lang] == 0:
                # Clear down any previous version of the output file
                if os.path.isfile(out_filename):
                    os.remove(out_filename)
                if os.path.isfile(missing_filename):
                    os.remove(missing_filename)

        words = [(l.split("|||")[-1].strip(), l.split("|||")[0].strip())
                 for l in codecs.open(in_filename, encoding='utf-8', errors='replace').readlines()]

        word_count = 0
        no_results_count = 0
        for tgt_word, src_word in words:

            if word_count < self.progress_tracker[progress_key]['word-count']:
                word_count += 1
                continue

            # Skip over some noisy data in the eval set
            # fi, hu, pt - all seem to have a lot of this?
            if tgt_word == '::':
                word_count += 1
                continue

            # TODO Remove temporary code to limit job size
            #if word_count > 10:
            #    break

            print('### ' + tgt_word + ' ### ' + str(word_count) + ' of ' + str(len(words)))
            query_page_ids = self.query_page_ids_for_lang(tgt_word, tgt_lang)
            if query_page_ids is None or len(query_page_ids) == 0:
                no_results_count += 1
                self.output_missing_queries('data/search_results/' + prefix, tgt_lang, [tgt_word])
                print('No results found - count: ' + str(no_results_count))
            else:
                self.output_page_ids(query_page_ids, 'data/search_results/' + prefix, tgt_lang, progress_key, b_output_raw=False)
            word_count += 1
            self.progress_tracker[progress_key]['word-count'] = word_count
            self.serialize_progress_tracker()

        print('No results found for ' + str(no_results_count) + ' of ' + str(word_count) + ' words')

    def output_missing_queries(self, out_dir, lang_code, missing_queries):

        missing_filename = out_dir + '/missing-' + lang_code + '0.txt'

        if not os.path.exists(out_dir):
            os.mkdir(out_dir)

        # Clear down any previous version of the output file
        if os.path.isfile(missing_filename):
            if self.lang_codes[lang_code] == 0:
                os.remove(missing_filename)

        with codecs.open(missing_filename, 'a', encoding='utf-8', errors='replace') as missing_file:
            for query in missing_queries:
                missing_file.write(query + '\n')

    def run_extract(self):

        foreign_lang_codes = self.lang_codes.keys()
        foreign_lang_codes.remove(self.en_lang_code)
        for foreign_lang_code in foreign_lang_codes:
            for prefix in self.prefixes:
                print('######## ' + prefix.upper() + ' ########')

                # Search for words in source language
                self.search_for_wiktionary_eval_words(prefix, self.en_lang_code, foreign_lang_code)

                # Search for words in target language
                #self.search_for_wiktionary_eval_words(prefix, foreign_lang_code, self.en_lang_code)


if __name__ == '__main__':
    WikipediaExtract().run_extract()
