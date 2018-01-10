// #################################
// TO BE EXECUTED IN MONGODB CONSOLE
// #################################

// Calculate the TF-IDF score for each distinct word in each sentence.

// Aggregate distinct words for each sentence using the 'counts' collection, where there exists
// an IDF score against the corresponding word in the 'words' collection.

// Note: In the previous step, IDF scores were only assigned to word docs that exist in the
// eval_set collection. So, effectively this means that words not in the eval_set collection
// score zero; they are of no help in achieving accuracy on that particular evaluation task.

var i = 0;

db.counts.aggregate(
    [
        {"$lookup":
            {"from": "words",
                "localField": "_id.word",
                "foreignField": "_id.word",
                "as": "word_doc"}
        },
        { "$unwind": "$word_doc" },
        { "$redact":
            {"$cond":
                [
                    { "$eq": [ "$_id.lang_prefix", "$word_doc._id.lang_prefix" ] },
                        "$$KEEP",
                        "$$PRUNE"
                ]
            }
        },
        {"$match":
            {"$and": [
                {"word_doc": { $ne: [] }},
                {"word_doc.idf": {"$exists": true}},
                {"score": {"$exists": false}} // Make it re-startable
            ]}
        },
        {"$project": {
            "count": "$count",
            "idf": "$word_doc.idf"
        }}
    ],
    {
        cursor: { batchSize: 50 }
    }
).forEach(function(doc)
    {
        // Calculate TF-IDF score
        var score = doc.count * doc.idf;
        db.counts.update(
            {
                "_id.lang_prefix": doc._id.lang_prefix,
                "_id.word": doc._id.word,
                "_id.sentence_id": doc._id.sentence_id
            },
            {"$set": {"score": score}}
        );
        i++;
    }
);
print("Written score to counts docs: " + i);
