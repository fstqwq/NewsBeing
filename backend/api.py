import multiprocessing
import sqlite3
import json
import os
from datetime import datetime
from typing import Tuple


from .parse import *


def fetch_num_docs(c):
    c.execute("SELECT COUNT(*) FROM documents")
    return c.fetchone()[0]

def fetch_num_inverted_indices(c):
    c.execute("SELECT COUNT(*) FROM inverted_index")
    return c.fetchone()[0]

def test_db(config):
    # check the existence of db
    dbpath = config['dbpath']
    num_doc = 0
    num_token = 0
    for i in range(config['num_worker']):
        dbfile = os.path.join(dbpath, config['name'] + f"-{i}.db")
        if not os.path.exists(dbfile):
            return None, None
        # count the number of documents
        with sqlite3.connect(dbfile) as conn:
            try:
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM documents")
                num_doc += c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM inverted_index")
                num_token += c.fetchone()[0]
            except:
                return None, None
    return num_doc, num_token


def preprocess_worker(id, config, gen_inverted_index = True):
    num_worker = config['num_worker']
    jsonpath = config['jsonpath']

    conn = establish_db_connection(id, config, False, True)
    c = conn.cursor()
    c.execute('''CREATE TABLE documents
                (url TEXT, text TEXT, timestamp INTEGER, id INTEGER PRIMARY KEY AUTOINCREMENT)''')
    if gen_inverted_index:
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
            
            if gen_inverted_index:
                for token in tokens:
                    c.execute("INSERT INTO inverted_index VALUES (?, ?)", (token, doc_id))

        conn.commit()
    conn.close()


def preprocess(config):
    print("Preprocessing... Config: " + str(config)[:100])
    
    if not os.path.exists(config['dbpath']):
        os.mkdir(config['dbpath'])

    num_worker = config['num_worker']
    
    pool = multiprocessing.Pool(processes=num_worker)
    pool.starmap(preprocess_worker, [(i, config) for i in range(num_worker)])

def fetch_index_by_token(token : str, cc : Tuple[sqlite3.Cursor, int]) -> SortedIndex:
    c, tot = cc
    c.execute("SELECT doc_id FROM inverted_index WHERE token=?", (token,))
    return SortedIndex(c.fetchall(), tot, False)

def fetch_index_by_text(text : str, cc : Tuple[sqlite3.Cursor, int]) -> SortedIndex:
    c, tot = cc
    tokens = make_tokens(text)
    if len(tokens) == 0:
        return SortedIndex([], tot, True) # all
    else:
        return fetch_index_by_token(tokens[0], cc)

def fetch_doc(id : int, c : sqlite3.Cursor) -> Tuple[str, str, int]:
    c.execute("SELECT url, text, timestamp FROM documents WHERE id=?", (id,))
    return c.fetchone()

def doc_to_dict(doc : Tuple[str, str, int]) -> str:
    return {'url': doc[0], 'text': doc[1], 'timestamp': datetime.fromtimestamp(doc[2]).isoformat()}

def fetch_doc_global_id(global_id, config : dict) -> Tuple[str, str, int]:
    """
    Create a cursor and fetch the document with the given global_id = (owner, id)
    """
    dbpath = config['dbpath']
    dbfile = os.path.join(dbpath, config['name'] + f"-{global_id[0]}.db")
    with sqlite3.connect(dbfile) as conn:
        conn = sqlite3.connect(dbfile)
        c = conn.cursor()
        return fetch_doc(global_id[1], c)


def fetch_tree(expr, cc : Tuple[sqlite3.Cursor, int]) -> SortedIndex:
    """
    Fetch the tree of the given expression
    """
    if isinstance(expr, str):
        return fetch_index_by_text(expr, cc)
    assert(isinstance(expr, tuple))
    if expr[0] == 'AND' or expr[0] == 'OR':
        operands = [fetch_tree(e, cc) for e in expr[1]]
        operands.sort(key=lambda x: len(x))
        result = operands[0]
        for i in range(1, len(operands)):
            if expr[0] == 'AND':
                result &= operands[i]
            else:
                result |= operands[i]
        return result
    elif expr[0] == 'NOT':
        return ~fetch_tree(expr[1], cc)
    raise Exception("Bad expression: " + str(expr))
    

def boolean_solve(expr : str, cc : Tuple[sqlite3.Cursor, int]) -> SortedIndex:
    tree = boolean_parse(expr)
    indices = fetch_tree(tree, cc)
    return indices


def establish_db_connection(id, config, readonly = True, remove_existed = False):
    dbpath = config['dbpath']
    dbfile = os.path.join(dbpath, config['name'] + f"-{id}.db")
    if remove_existed and os.path.exists(dbfile):
        os.remove(dbfile)
    # make connection, default cache size is 65536, page size is 4096, isolation level is None
    conn = sqlite3.connect(dbfile, isolation_level=None)
    conn.execute("PRAGMA cache_size = 65536")
    conn.execute("PRAGMA page_size = 4096")
    if readonly:
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA journal_mode = OFF")
        conn.execute("PRAGMA synchronous = OFF")
    return conn


def worker(id, config, input, output):
    with establish_db_connection(id, config) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM inverted_index")
        tot = c.fetchone()[0]        
        while True:
            task = input.get()
            if task is None:
                break
            try:
                ty, query = task
                if ty == 'Boolean':
                    indices = boolean_solve(query, (c, tot))
                output.put(indices)
            except Exception as e:
                output.put(e)