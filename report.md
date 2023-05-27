

# Efficiency

| Query, Result Count | Efficient Indexing | Hot Data (in DB Cache) | Language | Time |
| --- | --- | --- | --- | --- |
| (car AND buy AND NOT rent), 82902 | No | No | Python | 188 s|
| (car AND buy AND NOT rent), 82902 | Yes | No | Python | 1.78 s|
| (car AND buy AND NOT rent), 82902 | Yes | Yes | Python | 0.71 s|
| (car AND buy AND NOT rent), 82902 | Yes | No | Python + C++ | 1.66 s|
| (car AND buy AND NOT rent), 82902 | Yes | Yes | Python + C++ | 0.62 s|