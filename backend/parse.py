
import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from functools import lru_cache
from .index import *

stopword_set = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()
punctuations = string.punctuation

@lru_cache(maxsize=512)
def lemmatize(word):
    return lemmatizer.lemmatize(word)

def make_tokens(text):
    words = word_tokenize(text.lower())
    words = [w for w in words if w not in stopword_set]
    words = [w for w in words if w not in punctuations]
    return [lemmatize(w) for w in words]

def make_token(token):
    token = token.lower()
    if token in stopword_set or token in punctuations or len(token) == 0:
        return ''
    return lemmatize(token)

def split_tokens(expr : str):
    return re.findall(r'\(|\)|\w+', expr)

op_prec = {
    'AND': 2,
    'OR': 1,
    'NOT': 3,
    '(': 5,
    ')': 0,
}

def boolean_parse(expr: str):
    tokens = split_tokens(expr)
    if 'AND' in tokens or 'OR' in tokens or 'NOT' in tokens or '(' in tokens or ')' in tokens:
        operands = []
        ops = []
        for token in tokens:
            if token in op_prec:
                while len(ops) > 0 and op_prec[token] <= op_prec[ops[-1]]:
                    if ops[-1] == '(':
                        break
                    if ops[-1] == 'NOT':
                        operands.append(('NOT', operands.pop()))
                    else:
                        operands.append((ops[-1], [operands.pop(), operands.pop()]))
                    ops.pop()
                if token != ')':
                    ops.append(token)
                else:
                    if len(ops) == 0 or ops[-1] != '(':
                        raise ValueError('Illegeal expression')
                    ops.pop()
            else:
                operands.append(make_token(token))
        while len(ops) > 0:
            if ops[-1] == '(':
                break
            if ops[-1] == 'NOT':
                operands.append(('NOT', operands.pop()))
            else:
                operands.append((ops[-1], [operands.pop(), operands.pop()]))
            ops.pop()
        if len(ops) > 0 or len(operands) != 1:
            raise ValueError('Illegeal expression')
        return operands[0]
    else:
        if len(tokens) == 1:
            return tokens
        else:
            return ('AND', tokens)