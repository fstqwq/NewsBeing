from .api import *

import ctypes
from ctypes import cdll
import os
os.add_dll_directory('C:\\mingw64\\bin')
os.add_dll_directory(os.getcwd() + '\\backend\\cpp\\')
mydll = cdll.LoadLibrary('worker.dll')

init_cpp = mydll.init_cpp
boolean_solve_cpp = mydll.boolean_solve_cpp
boolean_solve_cpp.restype = ctypes.POINTER(ctypes.c_int)
finalize_cpp = mydll.finalize_cpp

class SortedIndexCPP:
    def __init__(self, indices, length):
        self.indices = indices
        self.length = length
    def __len__(self):
        return self.length
    def extract(self, max_count):
        return self.indices[:max_count]

def worker_cpp(id, config, input, output):
    dbfile = os.path.join(config['dbpath'], config['name'] + f"-{id}.db")
    init_cpp(id, ctypes.c_char_p(dbfile.encode()))
    while True:
        task = input.get()
        if task is None:
            break
        try:
            ty, query = task
            pgfirst, pglast = 1, 10
            if ty == 'Boolean':
                try:
                    parsed = boolean_parse(query)
                except Exception as e:
                    output.put(e)
                    continue
            query_str = f'{pgfirst}  {pglast} ' + ' '.join(parse_tree_cpp(parsed))
            print(query_str)
            indices_cpp = boolean_solve_cpp(query_str.encode())

            count = indices_cpp[0]
            arrlen = indices_cpp[1]
            indices = []
            for i in range(arrlen):
                indices.append(indices_cpp[i + 2])
            ret = SortedIndexCPP(indices, count)
            output.put(ret)
        except Exception as e:
            output.put(e)


def parse_tree_cpp(expr):
    print(expr)
    if isinstance(expr, str):
        if expr == '':
            return ["$"]
        else:
            return [expr]
    assert(isinstance(expr, tuple))
    ret = []
    for e in expr[1]:
        ret.extend(parse_tree_cpp(e))
    ret.append(expr[0])
    return ret