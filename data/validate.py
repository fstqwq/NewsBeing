import os
import json
import multiprocessing
import time

# read config from config.json
with open('data/config.json') as f:
    config = json.load(f)

path = config['path']
p = multiprocessing.cpu_count()

def parse(file):
    url_set = [set() for i in range(p)]
    for lines in open(os.path.join(path, file), 'r', encoding=config['encoding']):
        # parse json
        url = json.loads(lines)['url']
        id = hash(url) % p
        if url in url_set[id]:
            print('Duplicate url: ' + url)
            return None
        else:
            url_set[id].add(url)
    print(f"Count = {sum(len(i) for i in url_set)}")
    return url_set

def check(collections):
    s = collections[0]
    l = len(s)
    for i in range(1, len(collections)):
        newl = l + len(collections[i])
        s |= collections[i]
        if len(s) != newl:
            return False
        l = newl
    print("check pass: " + str(len(s)))
    return True

if __name__ == "__main__":
    print(f"cpu count = {p}")
    pool = multiprocessing.Pool(processes=p)
    # check whether url_sets has no intersection
    
    begin = time.time()
    result = pool.map(parse, config['jsonfiles'])
    end = time.time()
    print(f"time = {end - begin:.2f}")
    
    for i in result:
        if i is None:
            print("FAIL: Duplicate url found in the same file")
            exit(1)

    # reduce url_sets
    begin = time.time()
    tests = pool.map(check, ([result[j][i] for j in range(len(result))] for i in range(p)))
    end = time.time()
    print(f"time = {end - begin:.2f}")
    
    if all(tests):
        print("PASS")
    else:
        print("FAIL: intersection found")
        exit(1)
