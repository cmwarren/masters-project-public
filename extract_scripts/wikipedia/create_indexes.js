// #################################
// TO BE EXECUTED IN MONGODB CONSOLE
// #################################

db.eval_set.createIndex({"src.word": 1}, {name: "src_word"});
db.eval_set.createIndex({"trg.word": 1}, {name: "trg_word"});

db.words.createIndex({"_id.word": 1}, {name: "word"});
db.words.createIndex({"_id.lang_prefix": 1}, {name: "lang_prefix"});
db.words.createIndex({"idf": 1}, {name: "idf"});

db.counts.createIndex({"score": 1}, {name: "score"});
db.counts.createIndex({"_id.lang_prefix": 1, "_id.word": 1, "_id.sentence_id": 1},
    {name: "counts_key", unique: true})

db.sentences.createIndex({"word_count": 1}, {name: "word_count"});
db.sentences.createIndex({"score": 1}, {name: "score"});
db.sentences.createIndex({"normalised_score": 1}, {name: "normalised_score"});