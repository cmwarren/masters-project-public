// #################################
// TO BE EXECUTED IN MONGODB CONSOLE
// #################################

// Count the number of words per sentence, so that we can normalise the sentence scores.

db.pairs.aggregate(
    [
        {"$group":
                {"_id": {"sentence_id": "$sentence_id", "lang_prefix": "$lang_prefix"},
                    "word_count": {"$sum": 1}}}
    ],
    {
        cursor: { batchSize: 50 },
        allowDiskUse: true
    }
).forEach(function(doc)
    {
        db.sentences.update(
            {"sentence_id": doc._id.sentence_id, "lang_prefix": doc._id.lang_prefix},
            {"$set": {"word_count": doc.word_count}}
        );
    }
);