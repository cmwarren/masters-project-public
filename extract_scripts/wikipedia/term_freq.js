// #################################
// TO BE EXECUTED IN MONGODB CONSOLE
// #################################

// The 'pairs' collection holds a doc for every word in every sentence in the enrich corpus.
// We aggregate 'pairs' by the word value, to create a doc in the 'counts' collection for each
// distinct word in each sentence.
// We calculate a count of the number of times that word appears in the sentence i.e. the
// Term Frequency (TF).
db.pairs.aggregate(
    [
        {"$match": {"lang_prefix": "en0"}},
        {"$group":
            {"_id":
                {"lang_prefix": "$lang_prefix", "word": "$word", "sentence_id": "$sentence_id"},
                "count": {"$sum": 1}
            }
        }
    ],
    { allowDiskUse: true }
).forEach( function(doc)
    {
        db.counts.insert(doc);
    }
);