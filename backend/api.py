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

stopword_set = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def test_db(config):
    # check the existence of db
    dbpath = config['dbpath']
    sum = 0
    num_token = 0
    for i in range(config['num_worker']):
        dbfile = os.path.join(dbpath, config['name'] + f"-{i}.db")
        if not os.path.exists(dbfile):
            return None, None
        # count the number of documents
        conn = sqlite3.connect(dbfile)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM documents")
        num_doc = c.fetchone()[0]
        sum += num_doc
        c.execute("SELECT COUNT(*) FROM inverted_index")
        num_token = c.fetchone()[0]
        conn.close()
    return sum, num_token

def make_tokens(text):
    words = word_tokenize(text.lower())
    words = [w for w in words if w not in stopword_set and w not in string.punctuation]
    return [lemmatizer.lemmatize(w) for w in words]

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

    for file in files[files_low:files_high]:
        for line in open(os.path.join(jsonpath, file), 'r', encoding=config['encoding']):
            # parse json
            content = json.loads(line)
            url = content['url']
            text:str = content['text']
            timestamp = datetime.fromisoformat(content['timestamp']).timestamp()
            c.execute("INSERT INTO documents VALUES (?, ?, ?, NULL)", (url, text, timestamp))
            doc_id = c.lastrowid

            tokens = set(make_tokens(text))
            
            # insert into inverted index
            for token in tokens:
                c.execute("INSERT INTO inverted_index VALUES (?, ?)", (token, doc_id))

        conn.commit()


def preprocess(config):
    print("Preprocessing...")
    print("Config: " + str(config))
    num_worker = config['num_worker']

    if not os.path.exists(config['dbpath']):
        os.mkdir(config['dbpath'])

    pool = multiprocessing.Pool(processes=num_worker)
    pool.starmap(preprocess_worker, [(i, config) for i in range(num_worker)])

def fetch_index(c, text):
    token = make_tokens(text)[0] 
    c.execute("SELECT doc_id FROM inverted_index WHERE token=?", (token,))
    return c.fetchall()

def fetch_doc(c, id):
    c.execute("SELECT url, text, timestamp FROM documents WHERE id=?", (id,))
    return c.fetchone()

def fetch_doc_global_id(c, global_id, config):
    """
    Create a cursor and fetch the document with the given global_id = (owner, id)
    """
    dbpath = config['dbpath']
    dbfile = os.path.join(dbpath, config['name'] + f"-{global_id[0]}.db")
    with sqlite3.connect(dbfile) as conn:
        conn = sqlite3.connect(dbfile)
        c = conn.cursor()
        return fetch_doc(c, global_id[1])

def establish_db_connection(id, config):
    dbpath = config['dbpath']
    dbfile = os.path.join(dbpath, config['name'] + f"-{id}.db")
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    return conn, c