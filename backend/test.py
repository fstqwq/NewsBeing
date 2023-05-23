from api import *


if __name__ == "__main__":
    # read config from data/config-sample.json
    with open('data/config-sample.json') as f:
        config = json.load(f)
    num_pages, num_tokens = test_db(config)
    if num_pages is None:
        print("Database not found or incomplete, preprocessing...")
        preprocess(config)
    else:
        print(f"Database found, {num_pages} pages in total, {num_tokens} index records in total.")
    
    # start worker 0
    conn, c = establish_db_connection(0, config)

    # test query
    query = "bedroom"
    indices = fetch_index(c, query)
    print(f"Query: {query} : ({type(indices[0])}) {indices}")

    for rank, i in enumerate(indices[:5]):
        doc_id = i[0]
        url, text, timestamp = fetch_doc(c, doc_id)
        print(f"{rank}. {doc_id} : {url} : {datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')} : {text[:200]}")
    conn.close()

    # test fetch global_id
    global_id = (0, 18)
    url, text, timestamp = fetch_doc_global_id(c, global_id, config)
    print(f"{global_id} : {url} : {datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y %H:%M:%S')} : {text[:200]}")
