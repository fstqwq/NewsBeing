from flask import Flask, render_template, request, url_for, jsonify
from flask_cors import CORS
import json
from multiprocessing import Pool, Manager
import time
import math
from datetime import datetime

from backend.api import *
from config import *
from backend.parse import highlight_doc
from ai.api import *

app = Flask(__name__)
CORS(app, resources=r'*')

@lru_cache(maxsize=512)
def issue_query(query : str):
    query = query.strip()
    if query == '':
        return {
            "code": 400,
            "msg": "FAIL: Empty query"
        }
    if (query.startswith('(') and query.endswith(')')) or (query.startswith('[') and query.endswith(']')):
        ty = 'Boolean'
    else:
        ty = 'Ranked'

    for i in range(config['num_worker']):
        query_queues[i].put((ty, query))
    results = []
    tot = 0
    
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
            results.extend([(i, x) for x in indices.extract(100)])
        if failed is not None:
            return {
                "code": 400,
                "msg": f"FAIL: {str(failed)}"
            }
        result_docs = [highlight_doc(doc_to_dict(fetch_doc_global_id(doc_id, config)), query.replace('AND', '').replace('NOT', '').replace('OR', '')) for doc_id in results[:200]]
        return {
            "code": 200,
            "msg": f"OK: count = {tot}",
            "type": "Boolean",
            "cnt" : tot,
            "result": result_docs
        }
    elif ty == 'Ranked':
        failed = None
        timecurrent = "2022-06-16T12:00:00Z"
        format_str = '%Y-%m-%dT%H:%M:%SZ'
        nowtime = datetime.strptime(timecurrent, format_str).timestamp()
        for i in range(config['num_worker']):
            indices = response_queues[i].get()
            if isinstance(indices, Exception):
                failed = indices
                continue
            elif failed is not None:
                continue
            tot += len(indices)
            results.extend([(i, x) for x in indices[:100]])
        if failed is not None:
            return {
                "code": 400,
                "msg": f"FAIL: {repr(failed)}"
            }
        sorted_results = sorted(results, key = lambda d: d[1][1], reverse = True)    
        freshness = {}
        final_result = {}
        for group, (doc_id, score) in sorted_results[:100]:
            doc = fetch_doc_global_id((group, doc_id), config)
            #print(doc_id, score)
            final_result[(group, doc_id)] = doc
            freshness[(group, doc_id)] = math.log2(score + 1e-9) + 0.5 / (nowtime - doc[2])
        sorted_results = sorted(freshness.items(), key = lambda d: d[1], reverse = True)
        result_docs = [highlight_doc(doc_to_dict(final_result[(group, doc_id)]), query) for (group, doc_id), score in sorted_results[:200]]    
        return {
            "code": 200,
            "msg": f"OK: count = {tot}",
            "type": "Ranked",
            "cnt" : tot,
            "result": result_docs
        }
    else:
        assert False


DUMMY = "I’m sorry but I prefer not to continue this conversation. I’m still learning so I appreciate your understanding and patience.🙏"
@lru_cache(maxsize=512)
def issue_summary(query):
    try:
        if 'ai_enable' in config and config['ai_enable']:
            query_queues[-1].put(('summary', query))
            summary = response_queues[-1].get()
            return True, summary
        else:
            return True, {'summary_text': DUMMY}
    except Exception as e:
        return False, {'summary_text': str(e)}

@lru_cache(maxsize=512)
def issue_qa(question, context):
    try:
        if 'ai_enable' in config and config['ai_enable']:
            query_queues[-1].put(('qa', (question, context)))
            answer = response_queues[-1].get()
            return True, answer
        else:
            return True, {"answer" : DUMMY}
    except Exception as e:
        return False, {"answer" : str(e)}

@app.route('/qa', methods=['POST'])
def qa():
    question = request.json['question']
    context = request.json['context']
    begin = time.time()
    status, answer = issue_qa(question, context) 
    end = time.time()
    if not status:
        issue_qa.cache_clear()
    answer['time'] = f"{end - begin : .4f}"
    return {
        "code": 200,
        "msg": "OK",
        "answer": answer
    }

@app.route('/summary', methods=['POST'])
def summary():
    search_result = issue_query(request.json['query']) # should be in cache
    if search_result['code'] != 200 or 'result' not in search_result or (result := search_result['result']) == []:
        search_result['summary'] = 'Nothing to summarize'
        return search_result
    docs = [x['text'] for x in result]
    begin = time.time()
    status, summary = issue_summary(tuple(docs[:5]))
    end = time.time()
    if not status:
        issue_summary.cache_clear()
    summary['time'] = f"{end - begin : .4f}"
    return {
            "code": 200,
            "msg": "OK",
            "summary": summary,
        }

@app.route('/search', methods=['POST'])
def search():
    # ty = request.json['type']
    if 'query' not in request.json:
        return {
            "code": 400,
            "msg": "FAIL: Empty query"
        }
    query = request.json['query']
    # if ty not in ['Boolean', 'Ranked', 'Summary', 'QA']:
    #     return {
    #         "code": 400,
    #         "msg": "FAIL: Invalid query type"
    #     }
    begin = time.time()
    result = issue_query(query)
    end = time.time()

    result['time'] = f"{end - begin : .4f}"
    return result

            

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
            print("Start worker ", i)
            q1 = manager.Queue()
            q2 = manager.Queue()
            process = multiprocessing.Process(target=worker, args=(i, config, q1, q2))        
            process.start()
            workers.append(process)
            query_queues.append(q1)
            response_queues.append(q2)
        if 'ai_enable' in config and config['ai_enable']:
            print("Start AI worker")
            q1 = manager.Queue()
            q2 = manager.Queue()
            process = multiprocessing.Process(target=ai_worker, args=(config, q1, q2))        
            process.start()
            workers.append(process)
            query_queues.append(q1)
            response_queues.append(q2)
    app.run(debug=True, use_reloader=False, host='127.0.0.1', port=5000, threaded=False)
    import signal
    def on_exit(signum, frame):
        exit(0)
    signal.signal(signal.SIGINT, on_exit)

