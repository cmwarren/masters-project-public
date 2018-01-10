// #################################
// TO BE EXECUTED IN MONGODB CONSOLE
// #################################

// Match each word in the 'words' collection against the Wiktionary evaluation set for the relevant
// language.
// If there is a match, then calculate the Inverse Document Frequency (IDF) and assign it to the
// word doc in the 'words' collection.

print("==== Spanish ====");

// Calculate the number of sentences
var N=db.sentences.find({"lang_prefix": "es0"}).length();
print("N="+ N);

// Count how many words we expect to be updated
var words_to_update = db.words.aggregate(
    [
        {"$match":
            {"_id.lang_prefix": "es0",
                "idf":
                    {"$exists": false}
            }
        },
        {"$lookup":
            {"from": "eval_set",
                "localField": "_id.word",
                "foreignField": "src.word",
                "as": "eval_set_docs"}
        },
        { "$unwind": "$eval_set_docs" },
        { "$redact": {
            "$cond": [
                { "$eq": [ "es", "$eval_set_docs.src.lang_prefix" ] },
                    "$$KEEP",
                    "$$PRUNE"
            ]
        }},
        {"$match":
            {"eval_set_docs": { $ne: [] }}},
        {"$count": "words_to_update"}
    ]
);
printjson(words_to_update._batch);

var i=0;

// Calculate IDF only for the words in the eval set
db.words.aggregate(
    [
        {"$match":
            {"_id.lang_prefix": "es0",
              "idf":
                {"$exists": false}
            }
        },
        {"$lookup":
            {"from": "eval_set",
                "localField": "_id.word",
                "foreignField": "src.word",
                "as": "eval_set_docs"}
        },
        { "$unwind": "$eval_set_docs" },
        { "$redact": {
            "$cond": [
                { "$eq": [ "es", "$eval_set_docs.src.lang_prefix" ] },
                    "$$KEEP",
                    "$$PRUNE"
            ]
        }},
        {"$match":
            {"eval_set_docs": { $ne: [] }}}
    ]
).forEach( function(doc)
    {
        i++;
        var idf = Math.log10(N/doc.doc_freq);
        var result = db.words.update(
            {"_id.lang_prefix": doc._id.lang_prefix, "_id.word": doc._id.word},
            {"$set": {"idf": idf}});
    }
);
print("Updated records: " + i);


print("==== French ====");
// Calculate the number of sentences
N=db.sentences.find({"lang_prefix": "fr0"}).length();
print("N="+ N);

// Count how many words we expect to be updated
words_to_update = db.words.aggregate(
    [
        {"$match":
            {"_id.lang_prefix": "fr0",
                "idf":
                    {"$exists": false}
            }
        },
        {"$lookup":
            {"from": "eval_set",
                "localField": "_id.word",
                "foreignField": "src.word",
                "as": "eval_set_docs"}
        },
        { "$unwind": "$eval_set_docs" },
        { "$redact": {
            "$cond": [
                { "$eq": [ "fr", "$eval_set_docs.src.lang_prefix" ] },
                    "$$KEEP",
                    "$$PRUNE"
            ]
        }},
        {"$match":
            {"eval_set_docs": { $ne: [] }}},
        {"$count": "words_to_update"}
    ]
);
printjson(words_to_update._batch);

i=0;

// Calculate IDF only for the words in the eval set
db.words.aggregate(
    [
        {"$match":
            {"_id.lang_prefix": "fr0",
                "idf":
                    {"$exists": false}
            }
        },
        {"$lookup":
            {"from": "eval_set",
                "localField": "_id.word",
                "foreignField": "src.word",
                "as": "eval_set_docs"}
        },
        { "$unwind": "$eval_set_docs" },
        { "$redact": {
            "$cond": [
                { "$eq": [ "fr", "$eval_set_docs.src.lang_prefix" ] },
                    "$$KEEP",
                    "$$PRUNE"
            ]
        }},
        {"$match":
            {"eval_set_docs": { $ne: [] }}}
    ]
).forEach( function(doc)
    {
        i++;
        var idf = Math.log10(N/doc.doc_freq);
        var result = db.words.update(
            {"_id.lang_prefix": doc._id.lang_prefix, "_id.word": doc._id.word},
            {"$set": {"idf": idf}});
    }
);
print("Updated records: " + i);


print("==== Finnish ====");
// Calculate the number of sentences
N=db.sentences.find({"lang_prefix": "fi0"}).length();
print("N="+ N);

// Count how many words we expect to be updated
words_to_update = db.words.aggregate(
    [
        {"$match":
            {"_id.lang_prefix": "fi0",
                "idf":
                    {"$exists": false}
            }
        },
        {"$lookup":
            {"from": "eval_set",
                "localField": "_id.word",
                "foreignField": "src.word",
                "as": "eval_set_docs"}
        },
        { "$unwind": "$eval_set_docs" },
        { "$redact": {
            "$cond": [
                { "$eq": [ "fi", "$eval_set_docs.src.lang_prefix" ] },
                    "$$KEEP",
                    "$$PRUNE"
            ]
        }},
        {"$match":
            {"eval_set_docs": { $ne: [] }}},
        {"$count": "words_to_update"}
    ]
);
printjson(words_to_update._batch);

i=0;

// Calculate IDF only for the words in the eval set
db.words.aggregate(
    [
        {"$match":
            {"_id.lang_prefix": "fi0",
                "idf":
                    {"$exists": false}
            }
        },
        {"$lookup":
            {"from": "eval_set",
                "localField": "_id.word",
                "foreignField": "src.word",
                "as": "eval_set_docs"}
        },
        { "$unwind": "$eval_set_docs" },
        { "$redact": {
            "$cond": [
                { "$eq": [ "fi", "$eval_set_docs.src.lang_prefix" ] },
                    "$$KEEP",
                    "$$PRUNE"
            ]
        }},
        {"$match":
            {"eval_set_docs": { $ne: [] }}}
    ]
).forEach( function(doc)
    {
        i++;
        var idf = Math.log10(N/doc.doc_freq);
        var result = db.words.update(
            {"_id.lang_prefix": doc._id.lang_prefix, "_id.word": doc._id.word},
            {"$set": {"idf": idf}});
    }
);
print("Updated records: " + i);


print("==== English ====");
// Calculate the number of sentences
N=db.sentences.find({"lang_prefix": "en0"}).length();
print("N="+ N);

// Count how many words we expect to be updated
words_to_update = db.words.aggregate(
    [
        {"$match":
            {"_id.lang_prefix": "en0",
                "idf":
                    {"$exists": false}
            }
        },
        {"$lookup":
            {"from": "eval_set",
                "localField": "_id.word",
                "foreignField": "trg.word",
                "as": "eval_set_docs"}
        },
        { "$unwind": "$eval_set_docs" },
        { "$redact": {
            "$cond": [
                { "$eq": [ "en", "$eval_set_docs.trg.lang_prefix" ] },
                    "$$KEEP",
                    "$$PRUNE"
            ]
        }},
        {"$match":
            {"eval_set_docs": { $ne: [] }}},
        {"$count": "words_to_update"}
    ]
);
printjson(words_to_update._batch);

i=0;

// Calculate IDF only for the words in the eval set
db.words.aggregate(
    [
        {"$match":
            {"_id.lang_prefix": "en0",
                "idf":
                    {"$exists": false}
            }
        },
        {"$lookup":
            {"from": "eval_set",
                "localField": "_id.word",
                "foreignField": "trg.word",
                "as": "eval_set_docs"}
        },
        { "$unwind": "$eval_set_docs" },
        { "$redact": {
            "$cond": [
                { "$eq": [ "en", "$eval_set_docs.trg.lang_prefix" ] },
                    "$$KEEP",
                    "$$PRUNE"
            ]
        }},
        {"$match":
            {"eval_set_docs": { $ne: [] }}}
    ]
).forEach( function(doc)
    {
        i++;
        var idf = Math.log10(N/doc.doc_freq);
        var result = db.words.update(
            {"_id.lang_prefix": doc._id.lang_prefix, "_id.word": doc._id.word},
            {"$set": {"idf": idf}});
    }
);
print("Updated records: " + i);