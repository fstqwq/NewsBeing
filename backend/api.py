import sqlite3
import json


def init_db(config):
    conn = sqlite3.connect(config['database'])
    c = conn.cursor()

    # Create table for search engine
    # Each records contains text, timestamp, and url
    # We will use the text to generate reverse index for search
    # The primary key is the url
    c.execute('''CREATE TABLE IF NOT EXISTS documents
                    (url TEXT PRIMARY KEY, text TEXT, timestamp TEXT)''')
    conn.commit()


def preprocess(config, num_jobs = 1):
    pass



