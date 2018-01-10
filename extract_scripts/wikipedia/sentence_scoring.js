// #################################
// TO BE EXECUTED IN MONGODB CONSOLE
// #################################

// Sum the tf-idf scores in the 'counts' collection by sentence_id and update the values into
// the 'sentences' collection.
// Do it one language at a time, for improved performance.

var i=0;
db.counts.aggregate(
    [
        {"$match":
            {"score": {"$exists": true},
            "_id.lang_prefix": "en0"}
        },
        {"$group":
            {
                "_id":
                {
                    "sentence_id": "$_id.sentence_id",
                    "lang_prefix": "$_id.lang_prefix"
                },
                "score_sum": {"$sum": "$score"}
            }
        },
        {"$lookup":
            {
                "from": "sentences",
                "localField": "_id.sentence_id",
                "foreignField": "sentence_id",
                "as": "sentence_doc"
            }
        },
        {"$project":
            {
                "score_sum": 1,
                "word_count": "$sentence_doc.word_count"
            }
        }
    ],

    {
        cursor: { batchSize: 30 },
        allowDiskUse: true
    }
).forEach(function(doc)
    {
        var word_count = (doc.word_count != null) ? doc.word_count[0] : 0;
        //print("word_count=" + word_count);
        var normalised_score = (word_count != 0) ? doc.score_sum / word_count : 0;
        //print("normalised_score=" + normalised_score);
        db.sentences.update(
            {"sentence_id": doc._id.sentence_id, "lang_prefix": doc._id.lang_prefix},
            {"$set":
                {
                    "score": doc.score_sum,
                    "normalised_score": normalised_score
                }
            }
        );
        i++;
    }
);
print("Written score to sentence docs: " + i);
