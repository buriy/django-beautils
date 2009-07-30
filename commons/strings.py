def force_quote(s):
    if '"' in s: # escape all '"' into '\"'
        s = s.replace('"', '\\"')
    return '"%s"' % s

def quote(s, chars = ' ,"'):
    for c in chars:
        if c in s:
            return force_quote(s)
    return s
