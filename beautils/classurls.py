import types
from django.conf.urls.defaults import url, patterns

def url_from_dict(name, kw):
    key_opts = ['regex', 'view', 'args', 'name', 'kwargs']
    name = name.replace('__', '/')
    if name == '/':
        name = ''
    
    fields = {
        'name': name,
        'regex': '^'+name+'/',
        'args': '$',
        'kwargs': {}
    } 

    for key in key_opts:
        if key in kw:
            fields[key] = kw.pop(key)
            
    for key in kw.keys():
        if key.startswith('__') and key.endswith('__'):
            kw.pop(key)
    
    view = fields.pop('view')
    regex = fields.pop('regex')
    args = fields.pop('args')
    if not regex.endswith('$'):
        regex = regex + args 
    if regex == '^/$':
        regex = '^/?$'
    
    kw.update(fields.pop('kwargs'))
    
    return (regex, view, kw, fields.pop('name')) 

def make_patterns(container, prefix='', urlmaker=url_from_dict):
    items = []
    for k, v in sorted(container.__dict__.iteritems()):
        if type(v) is types.ClassType or type(v) is type:
            items.append(urlmaker(k, v.__dict__))
            
    return patterns(prefix, *items)

