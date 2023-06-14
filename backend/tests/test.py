import sys
import time

sys.path.append('.')
from backend.api import *
from backend import parse
from config import *
from datetime import datetime
import math

if __name__ == "__main__":

    with open(DATA_CONFIG_PATH) as f:
        config = json.load(f)
    num_pages, num_tokens = test_db(config)
    if num_pages is None or num_tokens is None:
        print("Database not found or incomplete, preprocessing...")
        begin = time.time()
        preprocess(config)
        end = time.time()
        print("time = {:.2f}".format(end - begin))
    else:
        print(f"Database found, {num_pages} pages in total, {num_tokens} index records in total.")
    
    # start worker 0
    conn = establish_db_connection(0, config)
    c = conn.cursor()

    # get number of documents
    num_docs = fetch_num_docs(c)
    cc = (c, num_docs)

    # test query
    print('======Test Single Query======')
    query = "bedroom"
    indices = fetch_index_by_token(query, cc).extractall()
    # print(f"Query: {query} : ({type(indices[0])}) {indices}")

    for rank, doc_id in enumerate(indices[:5]):  
        url, text, timestamp = fetch_doc(doc_id, c)
        print(f"{rank}. {doc_id} : {url} : {datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')} : {text[:200]}")
    
    # test boolean
    print('======Test Boolean Query======')
    # print(parse.boolean_parse("(car AND NOT rent) AND (house)"))
    # print(boolean_solve("(car AND NOT rent) AND (house)", cc))
    # print(boolean_solve("rent car discount", cc).extractall())
    # print(fetch_doc(boolean_solve("rent car discount", cc).extractall()[0], c))
    start = time.time()
    indices = boolean_solve('(car AND buy AND NOT rent)', cc)
    #print(indices)
    #print(indices.extract(10))
    results = [(0, x) for x in indices.extract(10)]
    result_docs = [fetch_doc_global_id(doc_id, config) for doc_id in results[:10]]
    for i, (url, text, timestamp) in enumerate(result_docs[:5]):
        print(f"{i}. {url} : {datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')} : {text[:200]}")
    print('======Boolean Query {}s======'.format(time.time() - start))

    # test fetch global_id
    print('======Test Fetch Global Id======')
    global_id = (0, 18)
    url, text, timestamp = fetch_doc_global_id(global_id, config)
    print(f"{global_id} : {url} : {datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')} : {text[:200]}")

    #test rank search 
    print('======Test Rank Search======')
    start = time.time()
    query = "fuck you"
    result = rank_search(query, cc)
    sorted_results = [(0, x) for x in result[:10]]
    timecurrent = "2022-06-16T12:00:00Z"
    format_str = '%Y-%m-%dT%H:%M:%SZ'
    nowtime = datetime.strptime(timecurrent, format_str).timestamp()
    final_result = {}
    freshness = {}
    for group, (doc_id, score) in sorted_results[:10]:
            doc = fetch_doc_global_id((group, doc_id), config)
            final_result[(group, doc_id)] = doc
            freshness[(group, doc_id)] = math.log2(score) + 0.5 / (nowtime - doc[2])
    sorted_results = sorted(freshness.items(), key = lambda d: d[1], reverse = True)
    #result_docs = [doc_to_dict(final_result[(group, doc_id)]) for (group, doc_id), score in sorted_results[:10]]    
    #print(result_docs)
    #print(type(result))
    for rank, (doc_id, score) in enumerate(result[:5]):
        url, text, timestamp = fetch_doc(doc_id, c)
        print(f"{rank}. {doc_id} : {url} : {datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')} : {text[:200]}")
    print('======Rank Search {}s======'.format(time.time() - start))

    conn.close()
