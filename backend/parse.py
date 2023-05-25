
import re
import nltk
import string
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from functools import lru_cache

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
    if token in stopword_set or token in punctuations:
        return None
    return lemmatize(token)

def split_tokens(expr : str):
    return re.findall(r'\(|\)|\w+', expr)


def merge_sorted_list_or(a : list, b : list):
    i, j = 0, 0
    ret = []
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            ret.append(a[i])
            i += 1
        elif a[i] > b[j]:
            ret.append(b[j])
            j += 1
        else:
            ret.append(b[j])
            i += 1
            j += 1
    ret += a[i:]
    ret += b[j:]
    return ret

def merge_sorted_list_and_not_inplace(a : list, b : list):
    i, j, k = 0, 0, 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            a[k] = a[i]
            i += 1
            k += 1
        elif a[i] > b[j]:
            j += 1
        else:
            i += 1
            j += 1
    while i < len(a):
        a[k] = a[i]
        i += 1
        k += 1
    del a[k:]

def merge_sorted_list_and_inplace(a : list, b : list):
    i, j, k = 0, 0, 0
    while i < len(a) and j < len(b):
        if a[i] < b[j]:
            i += 1
        elif a[i] > b[j]:
            j += 1
        else:
            a[k] = a[i]
            i += 1
            j += 1
            k += 1
    del a[k:]


class SortedIndex:
    def __init__(self, array, total = None, comp = False):
        # if array is a list of tuples, take the first element as the key
        if len(array) > 0 and isinstance(array[0], tuple): # from db query
            self.array = [int(i[0]) for i in array]
        elif len(array) == 0 or isinstance(array[0], int): # from db query
            self.array = array
        else:
            raise NotImplementedError()
        assert(sorted(self.array))
        self.total = total
        self.comp = comp
    
    def __repr__(self) -> str:
        if self.comp:
            return f'NOT({self.total}){self.array}'
        else:
            return f'{self.array}'
    
    def __ior__(self, other):
        """
        merge two sorted list inplace using operator AND
        warning: other may be modified.
        """
        if self.comp:
            if other.comp:
                # NOT A OR NOT B -> NOT (A AND B)
                merge_sorted_list_and_inplace(self.array, other.array)
            else:
                # NOT A OR B -> B - A
                merge_sorted_list_and_not_inplace(other.array, self.array)
                self.array = other.array
                self.comp = False
        else:
            if other.comp:
                # A OR NOT B -> NOT (B - A)
                merge_sorted_list_and_not_inplace(self.other, self)
                self.comp = True
            else:
                # A OR B
                self.array = merge_sorted_list_or(self.array, other.array)
        return self


    def __iand__(self, other):
        """
        merge two sorted list inplace using operator AND
        warning: other may be modified.
        """
        if self.comp:
            if other.comp:
                # NOT A AND NOT B -> NOT (A OR B)
                self.array = merge_sorted_list_or(self.array, other.array)
            else:
                # NOT A AND B -> B - A
                merge_sorted_list_and_not_inplace(other.array, self.array)
                self.array = other.array
                self.comp = False
        else:
            if other.comp:
                # A AND NOT B -> A - B
                merge_sorted_list_and_not_inplace(self.array, other.array)
            else:
                # A AND B
                merge_sorted_list_and_inplace(self.array, other.array)
        return self

    def __invert__(self):
        self.comp = not self.comp
        return self

    def __len__(self):
        if self.comp:
            return self.total - len(self.array) 
        else:
            return len(self.array)
    
    def extractall(self):
        if self.comp:
            return [i for i in range(self.total) if i not in self.array]
        else:
            return self.array


op_prec = {
    'AND': 2,
    'OR': 1,
    'NOT': 3,
    '(': 5,
    ')': 0,
}

def boolean_parse(expr: str):
    tokens = split_tokens(expr)
    if 'AND' in tokens or 'OR' in tokens or 'NOT' in tokens:
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
                operands.append(token)
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
        return ('AND', tokens)