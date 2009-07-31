def seq_uniq(S):
     r = []
     for item in S:
         if not item in r:
             r.append(item)
     return r

def seq_first(S, default=None):
    """
    xrange(20) => 0
    xrange(0) => None
    """
    for data in S:
        return data
    return default

def seq_limit(S, count=10):
    """
    xrange(20), count=10 => [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    """
    list = []
    for data in S:
        list.append(data)
        if len(list) >= count:
            break
    return list

def select_keys(D, keys, defaults={}, superdefault=None):
    """
    {a=1, b=2, c=3}, (a,c) => [1, 3]
    """
    return [D.get(key, defaults.get(key, superdefault)) for key in keys]

def regroup_tails(pairs, tailsize=1):
    """
    ((k1, k2, k3, kN) -> v) => ((k1, k2, k3), {kN -> v})
    """
    group_dict = {}
    last = None
    for tuple, value in pairs:
        group = tuple[:-tailsize]
        if tailsize == 1:
            key = tuple[-1]
        else:
            key = tuple[-tailsize:]
        if last is None:
            last = group
        elif last != group:
            yield last, group_dict
            last = group
            group_dict = {}
        group_dict[key] = value
    if group_dict:
        yield last, group_dict

