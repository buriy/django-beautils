def force_quote(s):
    if '"' in s: # escape all '"' into '\"'
        s = s.replace('"', '\\"')
    return '"%s"' % s

def quote(s, chars = ' ,"'):
    for c in chars:
        if c in s:
            return force_quote(s)
    return s

def translit_letter(l):
    if ord(l) > 0x7F:
        return chr(ord(l) ^ 0xA0)
    else:
        return l

def translit(s):
    return ''.join([translit_letter(l) for l in s.encode('koi8-r')])
                                                    