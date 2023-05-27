import sys
import time

sys.path.append('.')
from backend.api import *
from backend import parse
from config import *


def build_index_worker(id, config):
    conn = establish_db_connection(id, config, False, False)
    c = conn.cursor()

    c.execute("CREATE INDEX idx_inverted_index ON inverted_index (token)")

    conn.commit()
    conn.close()


def build_index(config):
    num_worker = config['num_worker']
    pool = multiprocessing.Pool(processes=num_worker)
    pool.starmap(build_index_worker, [(i, config) for i in range(num_worker)])


if __name__ == "__main__":
    with open(DATA_CONFIG_PATH) as f:
        config = json.load(f)
    build_index(config)
    
    