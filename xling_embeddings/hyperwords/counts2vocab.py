from collections import Counter

from docopt import docopt

from representations.matrix_serializer import save_count_vocabulary


def main():
    args = docopt("""
    Usage:
        counts2pmi.py <counts>
    """)
    
    counts_path = args['<counts>']
    counts2vocab(counts_path)


def counts2vocab(counts_path):
    words = Counter()
    contexts = Counter()
    with open(counts_path) as f:
        for line in f:
            try:
                count, word, context = line.strip().split()
                count = int(count)
                words[word] += count
                contexts[context] += count
            except ValueError as er:
                print(line.strip())
                raise er

    words = sorted(words.items(), key=lambda (x, y): y, reverse=True)
    contexts = sorted(contexts.items(), key=lambda (x, y): y, reverse=True)

    save_count_vocabulary(counts_path + '.words.vocab', words)
    save_count_vocabulary(counts_path + '.contexts.vocab', contexts)


if __name__ == '__main__':
    main()
