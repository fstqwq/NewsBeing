
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
    words = [w for w in words if w.isascii() and w not in stopword_set]
    words = [w for w in words if w not in punctuations]
    return [lemmatize(w) for w in words]

def make_token(token):
    if not token.isascii():
        return ''
    token = token.lower()
    if token in stopword_set or token in punctuations or len(token) == 0:
        return ''
    return lemmatize(token)


op_prec = {
    'AND': 2,
    'OR': 1,
    'NOT': 3,
    '(': 5,
    ')': 0,
}

def boolean_parse(expr: str):
    tokens = word_tokenize(expr)
    if '(' in tokens and ')' in tokens:
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
    elif len(expr) >= 2 and expr[0] == '[' and expr[-1] == ']' and '[' not in expr[1:-1] and ']':
        if len(tokens) == 1:
            return tokens[0]
        else:
            return ('AND', tokens)
    else:
        raise ValueError('Illegeal expression')
    
from yattag import Doc
from typing import Dict, List

def highlight_doc(doc_dict : Dict, query : str):

    keywords = set(lemmatize(i) for i in word_tokenize(query.lower()) if len(i) > 0 and i not in punctuations)
    true_keywords = set(lemmatize(i) for i in word_tokenize(query.lower()) if len(i) > 0 and i not in punctuations and i not in stopword_set)
    doc, tag, text = Doc().tagtext()
    bdoc, btag, btext = Doc().tagtext()
    lines = doc_dict['text'].split('\n')
    has_highlight = False
    bcount = 0
    for line in lines:
        with tag('p'):
            for token in line.split():
                if not has_highlight and any(i in punctuations for i in token):
                    bdoc, btag, btext = Doc().tagtext() # clear
                    if bcount != 0:
                        btext('...')
                        bcount = 0
                filterd_token = lemmatize(''.join([i for i in token.lower() if i.isascii()]))
                if filterd_token in true_keywords:
                    has_highlight = True
                if filterd_token in keywords:
                    if bcount < 200:
                        with btag('mark'):
                            btext(token)
                        btext(' ')
                    with tag('mark'):
                        text(token)
                    text(' ')
                else:
                    if bcount < 200:
                        btext(token)
                        btext(' ')
                    text(token)
                    text(' ')
                bcount += 1
    if bcount > 200:
        btext('...')
    doc_dict['body'] = doc.getvalue()
    brief = bdoc.getvalue()
    if not has_highlight:
        brief = doc_dict['text'][:500] + ('' if len(doc_dict['text']) <= 500 else '...')
    doc_dict['brief'] = brief
    return doc_dict