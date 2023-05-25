
import flask
import json
from backend.api import *

app = flask.Flask(__name__)

with open('data/config-sample.json') as f:
    config = json.load(f)

@app.route('/search', methods=['POST'])
def search():
    ty = flask.request.json['type']
    query = flask.request.json['query']
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
    if ty == 'Boolean':
        # single thread tmp:
        with establish_db_connection(0, config) as conn:
            c = conn.cursor()
            num_docs = fetch_num_docs(c)
            cc = (c, num_docs)
            indices = boolean_solve(query, cc)
            return {
                "code": 200,
                "msg": "OK: count = len(indices)",
                "cnt" : len(indices),
                "result": [doc_to_dict(fetch_doc(doc_id, c)) for doc_id in indices.extract(5)]
            }
        
    else:
        raise NotImplementedError()