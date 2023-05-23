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
