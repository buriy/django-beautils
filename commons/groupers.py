from namedtuple import namedtuple
import operator
from itertools import imap

class TupleCounter(dict):
    def __init__(self, *cols):
        class Value(namedtuple('%sValue' % self.__class__.__name__, cols)):
            def __add__(self, rhs):
                return self._make(imap(operator.add, self, rhs))
            def __sub__(self, rhs):
                return self._make(imap(operator.add, self, rhs))
            def __iadd__(self, rhs):
                return self._make(imap(operator.add, self, rhs))
            def __isub__(self, rhs):
                return self._make(imap(operator.sub, self, rhs))
            def __neg__(self):
                return self._make(imap(operator.neg, self))
        self.nuple = Value
        self.zero = Value(*[0] * len(Value._fields))
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return self.zero
    def __setitem__(self, key, value):
        if not isinstance(value, self.nuple):
            value = self.nuple(*value)
        dict.__setitem__(self, key, value)

def first(generator, default=None):
    for data in generator:
        return data
    return default

def head(generator, count=10):
    list = []
    for data in generator:
        list.append(data)
        if len(list) >= count:
            break
    return list

def filtered(source, names):
    return [source.get(name, 0) for name in names]

def regroup(pairs, size=1):
    group_dict = {}
    last = None
    for item, value in pairs:
        group = item[:-size]
        if size == 1:
            key = item[-1]
        else:
            key = item[-size:]
        if last is None:
            last = group
        elif last != group:
            yield last, group_dict
            last = group
            group_dict = {}
        group_dict[key] = value
    if group_dict:
        yield last, group_dict

class IntCounter(dict):
    def __init__(self, pairs={}):
        if hasattr(pairs, 'items'):
            pairs = pairs.items()
        for k,v in pairs:
            self[k] += v 
    def __getitem__(self, key):
        return self.get(key, 0)
    def __setitem__(self, key, value):
        assert isinstance(value, int)
        dict.__setitem__(self, key, value)

if __name__ == "__main__":
    tc = TupleCounter('x', 'y', 'z')
    tc[0] = (1, 2, 3)
    tc[1] += (2, 3, 5)
    tc[2] = tc[1] - tc[0]
    tc[3] = tc[-1] + tc[-2]
    tc[4] = tc[0] + tc[1] - tc[2] - tc[3]
    tc[5] -= (1, 2, 3)
    tc[6] -= tc[5] - tc[1]
    assert tc[0] == (1, 2, 3)
    assert tc[1] == (2, 3, 5)
    assert tc[2] == (3, 5, 8)
    assert tc[3] == (0, 0, 0)
    assert tc[4] == (6, 10, 16)
    assert tc[5] == (-1, -2, -3)
    assert -tc[6] == (1, 1, 2)
