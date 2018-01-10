from os import listdir
from os.path import join
import os
from collections import Counter
import sys


def main():
    thr = int(sys.argv[1])
    dir_path = sys.argv[2]
    bible2pairs(thr, dir_path)


def bible2pairs(thr, dir_path, f_output=None):
    if os.path.islink(dir_path):
        dir_path = os.readlink(dir_path)
    for path in [join(dir_path, f) for f in listdir(dir_path) if f.endswith('.txt')]:
        language_prefix = path[-7:-4]
        with open(path) as fin:
            lines = [line.strip() for line in fin]
        vocab = read_vocab(lines, thr)
        extract_pairs(vocab, lines, language_prefix, f_output)


def extract_pairs(vocab, lines, language_prefix, f_output):
    for line in lines:
        if not '\t' in line:
            continue
        sentence_id, sentence_str = line.split('\t')
        for word in sentence_str.split(' '):
            if word in vocab and len(word) > 0:
                if f_output is None:
                    print ''.join((language_prefix, '_', word.lower(), ' ', sentence_id))
                else:
                    f_output.write(''.join((language_prefix, '_', word.lower(), ' ', sentence_id)) + '\n')


def read_vocab(lines, thr):
    vocab = Counter()
    for line in lines:
        try:
            vocab.update(Counter(line.split('\t')[1].split(' ')))
        except IndexError as e:
            print('IndexError found in line: ' + line + ': ' + e.message)
            continue
    return dict([(token, count) for token, count in vocab.items() if count >= thr])

if __name__ == '__main__':
    main()

