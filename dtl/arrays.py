def is_array(val):
    val = val.strip()
    return val.startswith('[[') and val.endswith(']]')

def parse_array(val):
    list = val.split("||")
    array = []
    for item in list:
        array.append(item)
    return array

def pass_array(val):
    stripped = val.strip()
    if is_array(stripped):
        return parse_array(stripped[2:-2])
    else:
        return val

def parse_list(v):
    v = v.strip()
    if is_array(v):
        return parse_array(v[2:-2])
    else:
        return [v]

def print_list(data):
    if type(data) in (tuple, list, dict):
        return '[[%s]]' % ("||".join([print_list(item) for item in data]))
    else:
        return "%s" % data
