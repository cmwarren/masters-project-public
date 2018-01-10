### What is this repository for? ###

This repository holds code submitted for my MSc Intelligent Systems dissertation.

### Overview ###
The project takes the following paper as its baseline:

Levy, O., Søgaard, A., & Goldberg, Y. (2017). A Strong Baseline for Learning Cross-Lingual Word Embeddings from Sentence Alignments. In EACL.

### Code & Data Dependencies ###
Levy et al's code is available from:

https://bitbucket.org/omerlevy/xling_embeddings/

Their README instructions explain how to download the required datasets.

The following source directories are duplicated unaltered from Levy et al:

* /xling_embeddings/word2vecf/

* /xling_embeddings/hyperwords/

* /xling_embeddings/word2vecf/


The following source files have been slightly modified from Levy et al:

* /xling_embeddings/alignment_eval.py

* /xling_embeddings/wiktionary_eval.py


Levy et al's execution shell scripts have been adapted into iPython notebooks:

* /xling_embeddings/create_embeddings_lib.ipynb

* /xling_embeddings/create_baseline_embeddings.ipynb

* /xling_embeddings/evaluation_lib.ipynb

* /xling_embeddings/evaluate_baseline.ipynb



### How to train the embeddings ###


### How to evaluate the embeddings ###


