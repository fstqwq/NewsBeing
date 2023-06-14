from flask import Flask, render_template, request, url_for, jsonify
import json
from multiprocessing import Pool, Manager
import time
import math
from datetime import datetime

from backend.api import *
from config import *

app = Flask(__name__)


@app.route('/search', methods=['POST'])
def search():
    ty = request.json['type']
    query = request.json['query']
    if ty != 'Boolean' and ty != 'Ranked':
        return {
            "code": 400,
            "msg": "FAIL: Invalid query type"
        }
    if query == '':
        return {
            "code": 400,
            "msg": "FAIL: Empty query"
        }
    begin = time.time()
    for i in range(config['num_worker']):
        query_queues[i].put((ty, query))
    results = []
    tot = 0

    print(f"Waiting for results... {time.time() - begin}")
    
    if ty == 'Boolean':
        failed = None
        for i in range(config['num_worker']):
            indices = response_queues[i].get()
            if isinstance(indices, Exception):
                failed = indices
                continue
            elif failed is not None:
                continue
            tot += len(indices)
            results.extend([(i, x) for x in indices.extract(10)])
            print(f"Result {i}... {time.time() - begin}")
        if failed is not None:
            return {
                "code": 400,
                "msg": f"FAIL: {repr(failed)}"
            }
        result_docs = [doc_to_dict(fetch_doc_global_id(doc_id, config)) for doc_id in results[:10]]
        print(f"Done fetching ... {time.time() - begin}")
        return {
            "code": 200,
            "msg": f"OK: count = {tot}",
            "cnt" : tot,
            "result": result_docs
        }
    if ty == 'Ranked':
        failed = None
        timecurrent = "2022-06-16T12:00:00Z"
        format_str = '%Y-%m-%dT%H:%M:%SZ'
        nowtime = datetime.strptime(timecurrent format_str).timestamp()
        for i in range(config['num_worker']):
            indices = response_queues[i].get()
            if isinstance(indices, Exception):
                failed = indices
                continue
            elif failed is not None:
                continue
            tot += len(indices)
            results.extend([(i, x) for x in indices[:10]])
            print(f"Result {i}... {time.time() - begin}")
        if failed is not None:
            return {
                "code": 400,
                "msg": f"FAIL: {repr(failed)}"
            }
        sorted_results = sorted(results, key = lambda d: d[1][1], reverse = True)    
        freshness = {}
        final_result = {}
        for group, (doc_id, score) in sorted_results[:10]:
            doc = fetch_doc_global_id((group, doc_id), config)
            final_result[(group, doc_id)] = doc
            freshness[(group, doc_id)] = math.log2(score) + 0.5 / (nowtime - doc[2])
        sorted_results = sorted(freshness.items(), key = lambda d: d[1], reverse = True)
        result_docs = [doc_to_dict(final_result[(group, doc_id)]) for (group, doc_id), score in sorted_results[:10]]    
        print(f"Done fetching ... {time.time() - begin}")
        return {
            "code": 200,
            "msg": f"OK: count = {tot}",
            "cnt" : tot,
            "result": result_docs
        }


            

@app.route('/doc', methods=['GET', 'POST'])
def doc():
    global_id = request.args.get('global_id')
    if global_id is None:
        return {
            "code": 400,
            "msg": "FAIL: Empty global_id"
        }
    global_id = int(global_id)
    global_id = (global_id // MAX_PER_WORKER, global_id % MAX_PER_WORKER)
    url, text, timestamp = fetch_doc_global_id(global_id, config)
    return {
        "code": 200,
        "msg": "OK",
        "result": doc_to_dict((url, text, timestamp))
    }

if __name__ == "__main__":
    with app.app_context():
        with open(DATA_CONFIG_PATH) as f:
            config = json.load(f)
        global workers, query_queues, response_queues
        workers = []
        query_queues = []
        response_queues = [] 
        manager = Manager()
        for i in range(config['num_worker']):
            q1 = manager.Queue()
            q2 = manager.Queue()
            process = multiprocessing.Process(target=worker, args=(i, config, q1, q2))        
            process.start()
            workers.append(process)
            query_queues.append(q1)
            response_queues.append(q2)
    app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000, threaded=False)

