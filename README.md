# News Being

... or New Bing SE.

## Usage

### Search Query

If you want to start a Ranked search, simply type the query as you use google.

If you want to use the Boolean query, use one of the following method:

1. `(EXPRESSION)` where expression must be valid expression using `AND`, `OR`, `NOT` or `()`.
If you want to query these three keywords, use the lowercase form. Example: `(car AND buy AND NOT rent)`
2. `[KEYWORD(1) KEYWORD(2) .... KEYWORD(n)]` where all keywords are combined with operator `AND`. Example: `[Cyberpunk 2077 CD Project Red]`

### Q&A

TBD


## Requirement


### Backend

`Python`: 3.11
```
pip install -r requirements.txt
python backend/init_nltk.py
```

### Frontend

See `web/README.md`.




### Database preparation

1. Download Dataset: https://huggingface.co/datasets/allenai/c4/tree/main/realnewslike
2. Unzip JSON files into data/, modify the config.json if needed.

### Frontend Backend Interface

1. POST /search 
   
Input: 

```json
{
    "query": "QUERY_STRING"
}
```

Output:

```json
{
    "code": 200, /* or others as error code */
    "msg": "OK", /* or error */
    "type": "TYPE_STRING", /* Boolean or Ranked */
    "cnt" : 114,
    "result": [
        {
            "url": "URL_STRING", 
            "text": "TEXT_STRING", 
            "timestamp": "TIMESTAMP_STRING"
        },
    ],
    "summary": [ /* optional */
        {
            "text": "TEXT_STRING",
            "related": ["RELATED_LINK_A", "RELATED_LINK_B"]
        }
    ]
}
```

2. POST /qa

Input: 

```json
{
    "question" : "QUESTION_STRING",
    "query": "QUERY_STRING"
}
```

Output:

```json
{
    "code": 200, /* or others as error code */
    "msg": "OK", 
    "cnt" : 114,
    "qa" :  [ /* optional */
        {
            "text": "TEXT_STRING",
            "related": ["RELATED_LINK_A", "RELATED_LINK_B"]
        }
    ]
}
```

## Copy of the Project Requirement

1. Dataset

    All documents indexed by the search engine should come from the real-news-like
folder of the C4 dataset (about 15G):
https://huggingface.co/datasets/allenai/c4/tree/main/realnewslike

2. Search system

    A Query can be any item, person, event, or question related to one or several pieces
of news. Your search engine should support the following two forms of search:

    1) Boolean Search (25%): Users provide search keys and operations between keys. The
    system needs to return all the original documents. The query language must include
    operations such as AND, OR, NOT.

    2) ranked Search (20%): Given a search query, the search system is supposed to return a
    ranked list of search results (origin documents). You need to consider factors like
    semantic relevance and freshness. To implement this, you may use any ranking method.
3. Search result processing
    
    In addition to the original documents that were required to be returned in the previous
section, we now want to return the result of processing or understanding those documents.
A good search engine should also support some advance functions:

    1) Multi-news summarization (15%): This is an advanced feature of Ranked search. Group
    news from the same event into one category and generate a summary. Different news
    events related to query should generate separate summaries. For each generated
    summary, we must also know which original documents were generated for that
    summary.

    2) QA (15%): For example, when you query "How old is Donald Trump?" A good search
    engine will return "76" as the first result for this question, and link this answer to the
    document collection that implies the answer. Note that although our corpus does not
    contain knowledge data such as wiki, we can still conduct QA part within the scope of
    news (eg. " How many casualties in xxx incident? ").
    Note that this section is open, so you can implement either of the above two functions,
    or you can implement other functions related to the understanding/processing of search
    results as you wish. When you are demoing, state what you did, and the best overall result
    will get higher marks.

4. UI and report:
Implement GUI Interface for demo and project report (25%). The functionality of
Section 3 is based on rank search, in other words, boolean search as a separate interface.
These new features are supported only in rank search.


References:

1. https://github.com/Alex-Fabbri/Multi-News
2. https://arxiv.org/abs/2110.08499
3. https://arxiv.org/pdf/2112.07916v2.pdf
4. https://paperswithcode.com/task/multi-document-summarization
5. https://paperswithcode.com/task/question-answering