import sys
import time

from backend.api import *
from backend import parse
from config import *
from datetime import datetime

if __name__ == "__main__":
    import backend.init_nltk # init toolkit
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