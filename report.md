

# Efficiency


| Query | Efficient Indexing | In DB Cache | Language | Time |
| --- | --- | --- | --- | --- |
| (car AND buy AND NOT rent) | No | No | Python | 188 s|
| (car AND buy AND NOT rent) | Yes | No | Python | 1.80 s|
| (car AND buy AND NOT rent) | Yes | Yes | Python | 0.71 s|