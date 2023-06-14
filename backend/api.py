import multiprocessing
import sqlite3
import json
import os
from datetime import datetime
from typing import Tuple, List, Dict
import math
import numpy
import numcompress
import time

from .parse import *


def fetch_num_docs(c):
    # assuming no delete occurs
    c.execute("SELECT MAX(_ROWID_) FROM documents LIMIT 1")
    return c.fetchone()[0]

def fetch_num_inverted_indices(c):
    # assuming no delete occurs
    c.execute("SELECT MAX(_ROWID_) FROM inverted_index LIMIT 1")
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
                num_doc += fetch_num_docs(c)
                num_token += fetch_num_inverted_indices(c)
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
        # c.execute('''CREATE TABLE inverted_index
        #             (token TEXT, doc_id INTEGER, tf REAL)''')
        c.execute('''CREATE TABLE inverted_index
                    (token TEXT, doc_id BLOB, tf BLOB, version INTEGER)''')
    conn.commit()

    files = config['jsonfiles']
    files_low = id * len(files) // num_worker
    files_high = (id + 1) * len(files) // num_worker

    token_doc_id: Dict[List[int]] = {}
    token_tf: Dict[List[float]] = {}
    token_seen = {}
    format_str = '%Y-%m-%dT%H:%M:%SZ'

    for i, file in enumerate(files[files_low:files_high]):
        if id == 0:
            print('Indexing {} Total {}'.format(i, files_high - files_low))

        for j, line in enumerate(open(os.path.join(jsonpath, file), 'r', encoding=config['encoding'])):
            if id == 0 and j % 1000 == 0:
                print('Line {} Total 26953'.format(j))
            # parse json
            content = json.loads(line)
            url = content['url']
            text:str = content['text']
            # timestamp = datetime.fromisoformat(content['timestamp']).timestamp()
            timestamp = datetime.strptime(content['timestamp'], format_str).timestamp()
            c.execute("INSERT INTO documents VALUES (?, ?, ?, NULL)", (url, text, timestamp))
            doc_id = c.lastrowid

            words = make_tokens(text)
            tokens = set(words)
            dic = {}
            cnt = 0
            for word in words:
                if (word not in dic):
                    dic[word] = 0
                else: 
                    dic[word] = dic[word] + 1   
                cnt = cnt + 1    
            
            if gen_inverted_index:
                # for token in tokens:
                #     c.execute("INSERT INTO inverted_index VALUES (?, ?, ?)", (token, doc_id, dic[token] / cnt))
                for token in tokens:
                    token_seen[token] = True
                    if token not in token_doc_id:
                        token_doc_id[token] = []
                        token_tf[token] = []
                    token_doc_id[token].append(doc_id)
                    token_tf[token].append(dic[token] / cnt)

        if i % 16 == 15 or i == files_high - files_low - 1:
            if id == 0:
                print('Flushing')
            for token, doc_id_arr in token_doc_id.items():
                # doc_id_arr = numpy.array(token_doc_id[token], dtype=numpy.int32) # Uncompressed
                # tf_arr = numpy.array(token_tf[token], dtype=numpy.float32) # Uncompressed
                doc_id_arr = token_doc_id[token] # Compressed
                # if len(doc_id_arr) > 1:
                #     for i in range(len(doc_id_arr) - 1, 0, -1):
                #         doc_id_arr[i] -= doc_id_arr[i - 1] # Difference
                doc_id_arr = numcompress.compress(doc_id_arr)
                tf_arr = numcompress.compress(token_tf[token]) # Compressed
                c.execute('INSERT INTO inverted_index VALUES (?, ?, ?, ?)', (token, doc_id_arr.encode(), tf_arr.encode(), i))
            conn.commit()
            token_doc_id, token_tf = {}, {}

    conn.close()


def preprocess(config):
    print("Preprocessing... Config: " + str(config)[:100])
    
    if not os.path.exists(config['dbpath']):
        os.mkdir(config['dbpath'])

    num_worker = config['num_worker']
    
    print("Start time: " + str(datetime.now()))
    pool = multiprocessing.Pool(processes=num_worker)
    pool.starmap(preprocess_worker, [(i, config) for i in range(num_worker)])
    print("End time: " + str(datetime.now()))

@lru_cache(maxsize=512)
def fetch_index_by_token(token : str, cc : Tuple[sqlite3.Cursor, int]) -> SortedIndex:
    if token == '':
        return SortedIndex([], tot, True)
    c, tot = cc
    begin = time.time()
    c.execute("SELECT doc_id, version FROM inverted_index WHERE token=?", (token,))
    ret = c.fetchall()
    mid = time.time()
    ret.sort(key=lambda x: x[1])
    doc_id_arr = []
    for item in ret:
        # doc_id_arr.extend(numpy.frombuffer(item[0], dtype=numpy.int32).tolist()) # Uncompressed
        arr = [int(item) for item in numcompress.decompress(item[0].decode())] # Compressed
        # for i in range(1, len(arr)):
        #     arr[i] += arr[i - 1] # Difference
        doc_id_arr.extend(arr) # Compressed
    result = SortedIndex(doc_id_arr, tot, False)
    end = time.time()
    print(f"DB exec ({token}) time: {end - begin}, db time = {mid - begin}, count = {len(result)}")
    return result

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
        ret = fetch_doc(global_id[1], c)
        return ret


def fetch_tree(expr, cc : Tuple[sqlite3.Cursor, int]) -> SortedIndex:
    """
    Fetch the tree of the given expression
    """
    if isinstance(expr, str):
        return fetch_index_by_token(expr, cc)
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
    raise Exception("Unreachable code reached: " + str(expr))
    

def boolean_solve(expr : str, cc : Tuple[sqlite3.Cursor, int]) -> SortedIndex:
    tree = boolean_parse(expr)
    indices = fetch_tree(tree, cc)
    return indices

@lru_cache(maxsize=512)
def fetch_ranked_list_by_token(token : str, cc : Tuple[sqlite3.Cursor, int]) -> List:
    c, tot = cc
    c.execute("SELECT doc_id, tf, version FROM inverted_index WHERE token=?", (token,))
    ret = sorted(c.fetchall(), key=lambda x: x[2])
    return ret

@lru_cache(maxsize=512)
def rank_search(query : str, cc : Tuple[sqlite3.Cursor, int]) -> SortedIndex:
    c, tot = cc
    result = {}
    words = make_tokens(query)
    dic = {}
    cnt = 0
    for word in words:
        if word not in dic: 
            dic[word] = 1
        else:
            dic[word] = dic[word] + 1
        cnt = cnt + 1 
 
    tokens = set(words)
    for token in tokens:
        qf = dic[token] / cnt
        ret = fetch_ranked_list_by_token(token, cc) 
        doc_id_arr, tf_arr = [], []
        for item in ret:
            # doc_id_arr.extend(numpy.frombuffer(item[0], dtype=numpy.int32).tolist()) # Uncompressed
            # tf_arr.extend(numpy.frombuffer(item[1], dtype=numpy.float32).tolist()) # Uncompressed
            arr = [int(item) for item in numcompress.decompress(item[0].decode())] # Compressed
            # for i in range(1, len(arr)):
            #     arr[i] += arr[i - 1] # Difference
            doc_id_arr.extend(arr) # Compressed
            tf_arr.extend(numcompress.decompress(item[1].decode())) # Compressed
        # tmp = c.fetchall()
        # df = len(tmp)
        df = len(doc_id_arr)
        w1 = qf / (qf + 1.2)
        w3 = math.log2((tot - df + 0.5) / (df + 0.5))
        print(token, df, qf)
        for i in range(len(doc_id_arr)):
            doc_id, tf = doc_id_arr[i], tf_arr[i]
            w2 = tf * 1.5 / (tf  + 1.5)
            if (doc_id in result):
                result[doc_id] = result[doc_id] + w1 * w2 * w3
            else: 
                result[doc_id] = w1 * w2 * w3    
    result1 = sorted(result.items(), key = lambda d: d[1], reverse = True)
    return result1


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
        tot = fetch_num_docs(c)
        while True:
            task = input.get()
            if task is None:
                break
            try:
                ty, query = task
                if ty == 'Boolean':
                    indices = boolean_solve(query, (c, tot))
                elif ty == 'Ranked':
                    indices = rank_search(query, (c, tot))
                output.put(indices)
            except Exception as e:
                output.put(e)
