#Source: http://www.djangosnippets.org/snippets/1631/

def tableize(obj):
    if type(obj) == list:
        obj = tuple(obj)

    #make sure we have an iterator of dicts, or a dictionary
    #import ipdb; ipdb.set_trace()
    if not(obj and isinstance(obj, dict) or (getattr(obj, '__iter__', False) \
        and not [x for x in obj if not isinstance(x,dict)])):
        raise TypeError("Object must be a dictionary or list/tuple/iterable of dictionaries")

    if type(obj) == dict:
        #convert to tuple of tuples
        obj = tuple([((('key',k),('value',v))) for k,v in obj.items()])
    
    #Convert to tuple of tuples
    obj = tuple([type(d)==dict and tuple(d.items()) or d for d in obj])

    #make sure each dict has the same keys
    keys = [k for k,v in obj[0]]
    try:
        [[dict(d)[k] for k in keys] for d in obj]
    except KeyError:
        assert False, "Dictionary keys do not match"

    #get column widths
    col_widths = dict([(k, len(k)) for k in keys])
    for row in obj:
        for k,v in row:
            if len(str(dict(row)[k])) > col_widths.get(k):
                col_widths[k] = len(str(dict(row)[k]))

    # build separator
    sep = '+'+'+'.join(['-'*(col_widths[k]+2) for k in keys])+'+'

    # print table headers
    lines = []
    lines.append(sep)
    lines.append('| '+' | '.join([k.ljust(col_widths[k]) for k in keys])+' |')
    lines.append(sep)
    
    # print table rows
    for row in obj:
        lines.append('| '+' | '.join([str(v).ljust(col_widths[k]) for k,v in row])+' |')

    lines.append(sep)

    return '\n'.join(lines)

def ptable(obj):
    print tableize(obj)