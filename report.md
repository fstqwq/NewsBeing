

# Efficiency

| Query, Result Count | Efficient Indexing | In DB Cache | Language | Time |
| --- | --- | --- | --- | --- |
| (car AND buy AND NOT rent), 82902 | No | No | Python | 188 s|
| (car AND buy AND NOT rent), 82902 | Yes | No | Python | 1.78 s|
| (car AND buy AND NOT rent), 82902 | Yes | Yes | Python | 0.71 s|