import multiprocessing
import string
import sqlite3
import json
import os
from datetime import datetime
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer


def preprocess_worker(id, config):
    num_worker = config['num_worker']

    jsonpath = config['jsonpath']
    dbpath = config['dbpath']
    dbfile = os.path.join(dbpath, config['name'] + f"-{id}.db")

    if os.path.exists(dbfile):
        print("Warning: removing " + dbfile)
        os.remove(dbfile)

    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    c.execute('''CREATE TABLE documents
                (url TEXT, text TEXT, timestamp INTEGER, id INTEGER PRIMARY KEY AUTOINCREMENT)''')
    # create inverted index
    c.execute('''CREATE TABLE inverted_index
                (token TEXT, doc_id INTEGER)''')
    conn.commit()

    files = config['jsonfiles']
    files_low = id * len(files) // num_worker
    files_high = (id + 1) * len(files) // num_worker

    # parse json
    stopword_set = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()

    show = True
    for file in files[files_low:files_high]:
        for line in open(os.path.join(jsonpath, file), 'r', encoding=config['encoding']):
            # parse json
            content = json.loads(line)
            url = content['url']
            text:str = content['text']
            timestamp = datetime.fromisoformat(content['timestamp']).timestamp()
            c.execute("INSERT INTO documents VALUES (?, ?, ?, NULL)", (url, text, timestamp))

            # split tokens, remove stop words, and stem
            words = word_tokenize(text.lower())
            words = [w for w in words if w not in stopword_set]
            # remove punctuation
            words = [w for w in words if w not in string.punctuation]
            words = [lemmatizer.lemmatize(word) for word in words]
            if show:
                print(words)
                show = False
        conn.commit()


def preprocess(config):
    print("Preprocessing...")
    print("Config: " + str(config))
    num_worker = config['num_worker']

    if not os.path.exists(config['dbpath']):
        os.mkdir(config['dbpath'])

    pool = multiprocessing.Pool(processes=num_worker)
    pool.starmap(preprocess_worker, [(i, config) for i in range(num_worker)])

