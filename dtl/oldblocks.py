from arrays import is_array, parse_array
from django.template import Lexer, TOKEN_BLOCK, TOKEN_COMMENT, TOKEN_TEXT
from django.template import TOKEN_VAR
from django.utils.datastructures import SortedDict
from variables import BlockVar, SimpleVar

def parse(nodes, blocks, source, vars, ignores, comments, stop=None, parent=None):
    #x = re.findall("\{%\s*block\s*([\w-]+)\s*%\}(.*?)\{%\s*endblock\s*%\}", template, re.S)
    while nodes:
        token = nodes.pop(0)
        if token.token_type == TOKEN_COMMENT:
            source.append("{# %s #}" % token.contents)
            comments.append(token.contents)
        elif token.token_type == TOKEN_VAR:
            var = token.contents.strip().split('|',1)[0]
            if not '.' in var and not var in ignores:
                vars.append(SimpleVar(var, 'text', ''))
            source.append("{{ %s }}" % token.contents)
        elif token.token_type == TOKEN_TEXT:
            source.append(token.contents)
        elif token.token_type == TOKEN_BLOCK:
            bits = token.contents.strip().split(' ')
            if not bits[0] in ['block', 'endblock', 'endset']:
                source.append("{%% %s %%}" % token.contents)
            if bits[0] == stop:
                return
            if bits[0] == 'set':
                second = ' '.join(bits[1:])
                if '=' in second:
                    varname, val = second.split('=',1)
                    if val.startswith('"') and val.endswith('"') and val != '"': 
                        val = val[1:-1]
                    if not varname in ignores:
                        vars.append(SimpleVar(varname, 'text', val))
                else:
                    varname = second
                    subsource, subcomments = [], []
                    parse(nodes, blocks, subsource, vars, ignores, comments, 'endset', parent)
                    if not varname in ignores:
                        value = ''.join(subsource).strip()
                        if is_array(value):
                            vars.append(SimpleVar(varname, 'list', parse_array(value[2:-2])))
                        else:
                            vars.append(SimpleVar(varname, 'html', value))
                    
            if bits[0] == 'extends':
                vars.append(SimpleVar("parent_prototype", 'extends', bits[1]))
            if bits[0] == 'section':
                vars.append(SimpleVar(bits[-1], 'section', ''))
                ignores.add(bits[-1])
            if bits[0] == 'block':
                source.append("{%% %s %%}" % token.contents)
                source.append("{% endblock %}")
                var = BlockVar(bits[1], '', parent, comments)
                blocks[bits[1]] = var
                subsource, subcomments = [], [] 
                parse(nodes, blocks, subsource, vars, ignores, subcomments, 'endblock', var)
                var.value = ''.join(subsource).strip()
                #fixme: var.comments are available after parse!
            if bits[0] == 'for':
                bits = token.contents.strip().split(' ')
                if bits[-1] == 'reversed':
                    varname, in_index = bits[-2], -3
                else:
                    varname, in_index = bits[-1], -2
                loopvars = map(lambda x:x.strip(), ' '.join(bits[1:in_index]).split(','))
                if not '.' in varname and not varname in ignores:
                    vars.append(SimpleVar(varname, 'list', []))
                subignores = set(list(ignores)) 
                subignores.update(loopvars)
                parse(nodes, blocks, source, vars, subignores, comments, 'endfor', parent)
            if bits[0] == 'if':
                names = [v for v in bits if not v in ['and', 'or', 'not', 'if'] and not '.' in v]
                for varname in names:
                    vars.append(SimpleVar(varname, 'bool', 'true'))
                parse(nodes, blocks, source, vars, ignores, comments, 'endif', parent)

def get_blocks(template):
    return get_blocks_and_errors(template)[0]

def get_blocks_and_errors(template, debug=False):
    #x = re.findall("\{%\s*block\s*([\w-]+)\s*%\}(.*?)\{%\s*endblock\s*%\}", template, re.S)
    blocks, source, vars, ignores, comments, errors = SortedDict(), [], [], set(), [], []
    lex = Lexer(template, None).tokenize()
    try:
        parse(lex, blocks, source, vars, ignores, comments)
    except Exception, e:
        errors = [unicode(e)]
        if debug:
            raise
        import traceback; traceback.print_exc()
    varblocks = SortedDict() 
    for var in vars:
        varblocks[var.name] = var
    for name, bl in blocks.iteritems():
        varblocks[name] = bl
    return varblocks, errors
