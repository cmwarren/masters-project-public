// #################################
// TO BE EXECUTED IN MONGODB CONSOLE
// #################################

// The 'pairs' collection holds a doc for every word in every sentence in the enrich corpus.
// We aggregate 'pairs' by the language and sentence_id, to create a doc in the 'words' collection
// for each distinct language word within the corpus.
// We calculate the total number of sentences in which that language word appears across the entire
// corpus i.e. the Document Frequency (DF)
db.pairs.aggregate(
    [
        {"$match": {"lang_prefix": "en0"}},
        {"$group":
            {"_id":
                {"lang_prefix": "$lang_prefix", "word": "$word"},
                "sentence_ids": {"$addToSet": "$sentence_id"}}
        },
        {"$unwind": "$sentence_ids"},
        {"$group": {"_id": "$_id", "doc_freq": {"$sum": 1}}}
    ],
    { allowDiskUse: true }
).forEach( function(doc)
    {
        db.words.insert(doc);
    }
);