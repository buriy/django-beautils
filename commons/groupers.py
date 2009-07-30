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
