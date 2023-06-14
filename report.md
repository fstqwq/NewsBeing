

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

# Efficiency 2

Document 43.49G
| Preprocess | Boolean Query | Rank Query | Total Size | Index Size |
| --- | --- | --- | --- | --- |
| 2160s | 0.78s | 0.32s | 63G | 18.71G (Without Compression) |
| 2250s | 0.86s | 0.38s | 56G | 11.68G (With Compression) |
| 2325s | 1.07s | 0.36s | 55G | 11.48G (With Compression and Gap Storage) |

# Preprocess Real
Start time: 2023-06-14 06:23:39.490280
End time: 2023-06-14 07:23:13.735123