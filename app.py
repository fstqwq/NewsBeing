from flask import Flask, render_template, request, url_for, jsonify
import json

from backend.api import *
from backend.api_cpp import *
from config import *
from multiprocessing import Pool, Manager

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
    for i in range(config['num_worker']):
        query_queues[i].put((ty, query))
    results = []
    tot = 0
    
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
    if failed is not None:
        return {
            "code": 400,
            "msg": f"FAIL: {repr(failed)}"
        }
    return {
        "code": 200,
        "msg": f"OK: count = {tot}",
        "cnt" : tot,
        "result": [doc_to_dict(fetch_doc_global_id(doc_id, config)) for doc_id in results[:10]]
    }

@app.route('/doc', methods=['POST'])
def doc():
    global_id = request.json['global_id']
    if global_id is None:
        return {
            "code": 400,
            "msg": "FAIL: Empty global_id"
        }
    if isinstance(global_id, int):
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

