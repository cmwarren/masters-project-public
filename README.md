### What is this repository for? ###

This repository holds code submitted for my MSc Intelligent Systems dissertation.

### Overview ###
The project takes the following paper as its baseline:

Levy, O., Søgaard, A., & Goldberg, Y. (2017). A Strong Baseline for Learning Cross-Lingual Word Embeddings from Sentence Alignments. In EACL.

The project aims to extract new monolingual corpora from Wikipedia and Twitter, and extend the Levy et al's Multilingual SID-SGNS model to enrich the cross-lingual embeddings with additional vocabulary.

### Data dependencies ###
Levy et al's code is available from:

https://bitbucket.org/omerlevy/xling_embeddings/

Their README instructions explain how to download the required Bible and Europarl training corpora.

### Code dependencies ###

In general, where there are dependencies on Levy et al's code, the necessary files have been duplicated into this repository.

The following source directories are duplicated unaltered from Levy et al:

* /xling_embeddings/eval_data/

* /xling_embeddings/hyperwords/

* /xling_embeddings/word2vecf/


The following evaluation code has been slightly modified from Levy et al:

* /xling_embeddings/alignment_eval.py

* /xling_embeddings/wiktionary_eval.py


Levy et al's execution shell scripts have been adapted into iPython notebooks:

* /xling_embeddings/create_embeddings_lib.ipynb

* /xling_embeddings/create_baseline_embeddings.ipynb

* /xling_embeddings/evaluation_lib.ipynb

* /xling_embeddings/evaluate_baseline.ipynb



### How to train the baseline embeddings ###

* Run /xling_embeddings/create_baseline_embeddings.ipynb

### How to evaluate the baseline embeddings ###

* Run /xling_embeddings/evaluate_baseline.ipynb

### How to extract the monolingual corpora ###

* Run /extract_scripts/twitter/twitter_extract.py

* Run /extract_scripts/wikipedia/wikipedia_extract.py

Optionally, rank the sentences in the Wikipedia corpus based on a TF-IDF scoring. This requires a MongoDB enviroment.

On the command line, run Python programs:

* Run /extract_scripts/load_eval_sets.py

* Run /extract_scripts/load_sentences.py

In the mongo console:

* Run /extract_scripts/create_indexes.js

* Run /extract_scripts/doc_freq.js

* Run /extract_scripts/term_freq.js

* Run /extract_scripts/inverse_doc_freq.js

* Run /extract_scripts/words_per_sentence.js

* Run /extract_scripts/tf-idf_scoring.js

Back on the command line:

* Run /extract_scripts/unload_ranked_sentences.py

### How to train the enriched embeddings ###

* Run /xling_embeddings/create_enriched_embeddings.ipynb

### How to evaluate the enriched embeddings vs baseline ###

* Run /xling_embeddings/evaluate_oov.ipynb

### Additional Dataset Analysis Scripts ###

* /xling_embeddings/training_and_eval_set_analysis.ipynb

* /xling_embeddings/enriched-qualitative-analysis.ipynb

* /xling_embeddings/enriched-quantitative-analysis.ipynb

* /xling_embeddings/generate_gephi_input_files.ipynb

* /extract_scripts/plot_ranked_sentence_word_counts.ipynb