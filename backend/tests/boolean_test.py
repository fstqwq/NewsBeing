import sys
sys.path.append('.')

from backend import parse


boolean_expressions = [
    "car AND rent",
    "car OR rent",
    "(car) AND NOT rent",
    "(NOT car) AND rent",
    "NOT (car AND rent)",
    "()",
    "(",
    ")",
    "car",
    "car rent",
    "AND"
]

for expr in boolean_expressions:
    print("testing : ", expr)
    try:
        print(parse.boolean_parse(expr))
    except Exception as e:
        print("ERROR: ", e)