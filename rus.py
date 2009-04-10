def translit_letter(l):
    if ord(l) > 0x7F:
        return chr(ord(l) ^ 0xA0)
    else:
        return l

def translit(s):
    return ''.join([translit_letter(l) for l in s.encode('koi8-r')])

