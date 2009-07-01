from adb.aiterator import unpack_tuple
from adb.aiterator import pack_tuple
import datetime
import time

def timed(f, t=100000):
    start = time.time()
    for _ in xrange(t):
        f()
    delta = time.time() - start
    print "%.1f times per second" % (t / delta)

IDX_SPEC = '|'
IDX_DELIM = '||'
IDX_ESC = '\\|'

_date_cache = {}
def pack_date(date):
    if not date in _date_cache:
        _date_cache[date] = "%4d%02d%02d" % (date.year, date.month, date.day) 
    return _date_cache[date]

ESC = {
       int: str,
       str: lambda val: val.replace('|','\\|'),
       unicode: lambda val: val.encode('utf-8').replace('|','\\|'),
       datetime.date: pack_date,
       #datetime.datetime: pack_datetime(val),
}

def esc(val):
#    return val
#    if isinstance(val, str): return val
    try:
        f = ESC[type(val)]
#        if f is None: return val
        return f(val)
    except KeyError:
        raise Exception('Val has unsupported type: ' + repr(val))

def unesc(val):
#    return val
    return val.replace("\\|", "|")
    #return val.replace(IDX_ESC, IDX_SPEC)

def pack_tuple(tup):
    #return IDX_DELIM.join(tup) + IDX_DELIM
    return IDX_DELIM.join([esc(x) for x in tup]) + IDX_DELIM
#    return IDX_DELIM.join(map(esc, tup)) + IDX_DELIM

#def pack_tuple_prefix(tup):
#    return IDX_DELIM.join(map(esc, tup))

def unpack_tuple(data):
    assert data[-2:] == IDX_DELIM
    return tuple([unesc(x) for x in data[:-2].split(IDX_DELIM)])
#    return tuple(map(unesc, data[:-2].split(IDX_DELIM)))
#    return tuple(data[:-2].split(IDX_DELIM))

def unpack_nuple(data, klass):
    return tuple([unesc(x) for x in data[:-2].split(IDX_DELIM)])
    return klass(*(map(unesc, data.split(IDX_DELIM))[:-1]))

data = "table:shdj\|kfhdsjk||vhcjkvhf\|jkhvdfjk||ryuiewr\|yiuwe||"
print unpack_tuple(data)

def g():
    _t, cols = data.split(':', 1)
    #txt = "table:shdjkfhdsjk||vhcjkvhfjkhvdfjk||ryuiewryiuwe||"
    #cols = txt[txt.find(':'):]
    unpacked = unpack_tuple(cols)
    assert cols == pack_tuple(unpacked) 

if __name__ == '__main__':
    print "Running..."
    timed(g, t=200000)
    
    print "Loading psyco..."
    import psyco
    psyco.full()
    
    timed(g, t=200000)