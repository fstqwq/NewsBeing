import os
import json
import multiprocessing

# read config from config.json
with open('data/config.json') as f:
    config = json.load(f)

path = config['path']

def parse(file):
    url_set = set()
    for lines in open(os.path.join(path, file), 'r', encoding=config['encoding']):
        # parse json
        url = json.loads(lines)['url']
        if url in url_set:
            print('Duplicate url: ' + url)
            return None
        else:
            url_set.add(url)
    return url_set

if __name__ == "__main__":
    print(f"cpu count = {multiprocessing.cpu_count()}")
    pool = multiprocessing.Pool(processes=multiprocessing.cpu_count())
    # get the result from the processes
    result = pool.map(parse, config['jsonfiles'])

    # check whether url_sets has no intersection
    url_sets = set()
    for url_set in result:
        if url_set is None:
            print('Error: Duplicate url in the same file')
            exit(0)
        if len(url_sets & url_set) > 0:
            print('Error: Duplicate url in different files')
            exit(0)
        else:
            url_sets = url_sets | url_set

    print("PASS")