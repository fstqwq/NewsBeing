

# Efficiency

| Query, Result Count | Efficient Indexing | Cold Start | Language | Time |
| --- | --- | --- | --- | --- |
| (car AND buy AND NOT rent), 82902 | No | Yes | Python | 188 s|
| (car AND buy AND NOT rent), 82902 | Yes | Yes | Python | 1.78 s|
| (car AND buy AND NOT rent), 82902 | Yes | No | Python | 0.71 s|
| (car AND buy AND NOT rent), 82902 | Yes | Yes | Python + C++ | 1.66 s|
| (car AND buy AND NOT rent), 82902 | Yes | No | Python + C++ | 0.62 s|
| ret, ~8300 (1/16) | Yes | No | \*sqlite3 | 0.06 s |
| buy, ~43000 (1/16) | Yes | No | \*sqlite3 | 0.26 s |
| car, ~54500 (1/16) | Yes | No | \*sqlite3 | 0.33 s |