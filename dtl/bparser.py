from django.template import VariableNode, TOKEN_BLOCK, TOKEN_COMMENT, TOKEN_TEXT, \
    TOKEN_VAR, StringOrigin
from django.template.context import Context
from django.template.debug import DebugParser, DebugLexer
from django.template.defaulttags import ForNode, IfNode, IfEqualNode
from django.template.loader_tags import ExtendsNode, BlockNode
from django.utils.datastructures import SortedDict
from fragments import set_n_extends
from fragments.set_n_extends import SetBlockNode, SetNode, HideNode
from fragments.variables import BlockVar, SimpleVar
from links.tags import SectionNode, LinkNode
from utils.tags import SwitchNode
from fragments.arrays import pass_array
from assets.tags import ImageNode
from links.sectionloop import SectionLoopNode

def parse_opener(parser, cmd, token):
    if cmd == 'set':
        args = token.contents.strip().split(' ', 1)[1].strip()
        if not '=' in args: # block-set
            varname = args.split('=')[0]
            type = 'html'
            if ':' in varname:
                type, varname = varname.split(':', 1)
            var = SimpleVar(varname, type, '')
            parser.blocks[varname] = var
            parser.push_source([], [], var)
    elif cmd == 'block':
        args = token.contents.strip().split(' ', 1)[1].strip()
        source, comments, parent = parser.get_source()
        source.append("{%% %s %%}" % token.contents.strip())
        source.append("{% endblock %}")
        var = BlockVar(args, '', parent, comments)
        parser.blocks[args] = var
        subsource, subcomments = [], []
        parser.push_source(subsource, subcomments, var)
        #FIXME: var.comments are available after parse!
        
def parse_closer(parser, token):
    cmd = token.contents.strip().split(' ', 1)[0]
    if cmd == 'endset':
        source, comments, var = parser.pop_source()
        value = ''.join(source[:-1]).strip()
        var.value = pass_array(value)
        var.desc = "\n".join(comments)
    elif cmd == 'endblock':
        source, comments, parent = parser.pop_source()
        parent.value = ''.join(source[:-1]).strip()
            
def parse_token(parser, token):
    source, comments, _var = parser.get_source()
    if token.token_type == TOKEN_COMMENT:
        source.append("{# %s #}" % token.contents)
        comments.append(token.contents)
    elif token.token_type == TOKEN_VAR:
        source.append("{{ %s }}" % token.contents)
    elif token.token_type == TOKEN_TEXT:
        source.append(token.contents)
    elif token.token_type == TOKEN_BLOCK:
        source.append("{%% %s %%}" % token.contents)

class BlockParser(DebugParser):
    def __init__(self, tokens):
        super(BlockParser, self).__init__(tokens)
        self._sources = []
        source, comments, parent = [], [], None
        self.push_source(source, comments, parent)
        self.blocks = SortedDict()
        
    def next_token(self):
        token = super(BlockParser, self).next_token()
        parse_token(self, token)
        return token
    
    def enter_command(self, command, token):
        parse_opener(self, command, token)
        super(BlockParser, self).enter_command(command, token)
        
    def prepend_token(self, token):
        parse_closer(self, token)
        super(BlockParser, self).prepend_token(token)
        
    def push_source(self, source, comments, parent):
        self._sources.append([source, comments, parent])

    def get_source(self):
        return self._sources[-1]
    
    def pop_source(self):
        return self._sources.pop()

def parse_var(var):
    if var.lookups and len(var.lookups) == 1:
        return var.lookups[0]
    else:
        return None

def find_vars(expr):
    if isinstance(expr, list):
        for x in expr:
            for v in find_vars(x):
                yield v
    v = parse_var(expr.var)
    if v: yield v
    for _func, args in expr.filters:
        for lookup, arg in args:
            if lookup:
                v = parse_var(arg)
                if v: yield v

def split_by_comma(text):
    return map(lambda x:x.strip(), text.split(','))

class TypeParser(object):
    def __init__(self, tokens):
        self.tokens = tokens
    
    def parse_vars(self):
        self._vars = SortedDict()
        self._errors = []
        self._ignores = Context()
        parser = BlockParser(self.tokens)
        nodelist = parser.parse()
        assert len(parser._sources) == 1
        self.blocks = parser.blocks
        self.add_nodelist(nodelist)
        return self._vars

    def set_variable_type(self, name, type):
        decl = split_by_comma(type)
        if not name in self._vars:
            self._errors.append('Variable "%s" is not yet declared!' % name)
            return  
        var = self._vars[name]
        if 'hidden' in decl:
            var.hidden = True
            decl.remove('hidden')
        var.type = decl[0]
    
    def add_variable(self, var):
        #print 'add_variable', (var.name, var.type)
        assert isinstance(var, (BlockVar, SimpleVar))
        if var.name in self._ignores:
            if var.name in self._vars:
                #FIXME
                if self._vars[var.name].type == 'bool' and var.type != 'bool':
                    self._vars[var.name] = var
                elif self._vars[var.name].type != 'section' and var.type == 'section':
                    self._vars[var.name] = var
                elif var.value and var.type != 'bool':
                    self._vars[var.name] = var
            elif var.value:
                self._vars[var.name] = var
            return
        if var.name in self._vars:
            #defining variable twice
            self._errors.append('Variable "%s" is declared twice!' % var.name)
        self._vars[var.name] = var
        self.add_ignore(var.name)

    def add_expr(self, expr, vartype='text', default=''):
        #print-'add_expr', (unicode(expr), vartype, default)
        for var in find_vars(expr):
            self.add_variable(SimpleVar(var, vartype, default))
    
    def add_ignore(self, name):
        assert isinstance(name, basestring)
        self._ignores[name] = name
    
    def add_define(self, vartype, name, value):
        val = ".".join(value.var.lookups or [])
        if val in ['true', 'false']:
            self.add_variable(SimpleVar(name, vartype, val=='true'))
        elif val.startswith('section.'): # from constant
            self.add_variable(SimpleVar(name, 'section', val[8:]))
        elif val: # from var
            for var in find_vars(value):
                self.add_variable(SimpleVar(var, 'text', ''))
            #print-'add_define', (vartype, name, unicode(value))
            self.add_variable(SimpleVar(name, 'html', '{{ %s }}' % value))
        else: # from literal
            self.add_variable(SimpleVar(name, vartype, value.var.literal))
    
    def add_nodelist(self, nodelist, ignores=[]):
        self._ignores.push()
        for i in ignores:
            self.add_ignore(i)
        for node in nodelist:
            self.add_node(node)
        self._ignores.pop()
    
    def add_node(self, node):
        if isinstance(node, (SetBlockNode, BlockNode)):
            self.add_variable(self.blocks[node.name])
            self.add_nodelist(node.nodelist, [node.name])
        elif isinstance(node, ForNode):
            self.add_expr(node.sequence, 'list', [])
            self.add_nodelist(node.nodelist_loop, node.loopvars)
        elif isinstance(node, SectionLoopNode):
            self.add_expr(node.sequence, 'section', '')
            self.add_nodelist(node.nodelist_loop, node.loopvars)
        elif isinstance(node, IfNode):
            for _ifnot, expr in node.bool_exprs:
                self.add_expr(expr, 'bool', True)
            self.add_nodelist(node.nodelist_true)
            self.add_nodelist(node.nodelist_false)
        elif isinstance(node, VariableNode):
            self.add_expr(node.filter_expression)
        elif isinstance(node, SetNode):
            self.add_define(node.type, node.name, node.value)
        elif isinstance(node, HideNode):
            self._vars[node.name].hidden = True
        elif isinstance(node, ImageNode):
            self.add_variable(SimpleVar(node.name, 'image'))
        elif isinstance(node, IfEqualNode):
        #    for expr in [node.var1, node.var2]:
        #        self.add_expr(expr)
            self.add_nodelist(node.nodelist_true)
            self.add_nodelist(node.nodelist_false)
        elif isinstance(node, SwitchNode):
            choices = []
            for tests, _nodelist in node.cases:
                for expr in tests:
                    if not expr.var.lookups:
                        choices.append(expr.literal)
                    else:
                        self.add_expr(expr)
            for var in find_vars(node.variable):
                self.add_variable(SimpleVar(var, 'select', choices and choices[0], choices))
            for tests, _nodelist in node.cases:
                self.add_nodelist(node.nodelist_true, [node.loopvars])
        elif isinstance(node, ExtendsNode):
            if node.parent_name_expr:
                self.add_variable(SimpleVar("parent_prototype", 'extends', 'unknown'))
            else:
                self.add_variable(SimpleVar("parent_prototype", 'extends', node.parent_name))
            self.add_nodelist(node.nodelist)
        elif isinstance(node, set_n_extends.ExtendsNode):
            self.add_variable(SimpleVar("parent_prototype", 'extends', node.parent_node))
            self.add_nodelist(node.nodelist)
        elif isinstance(node, SectionNode):
            self.add_define('section', node.variable, node.link_name)
        elif isinstance(node, LinkNode):
            self.add_expr(node.section, 'section', '')
            self.add_expr(node.link_name)
            self.add_ignore(node.variable)
        elif hasattr(node, 'nodelist'):
            self.add_nodelist(node.nodelist)
    
def get_blocks(template):
    if hasattr(template, 'source'):
        template = template.source
    return get_blocks_and_errors(template, debug=True)[0]

def get_blocks_and_errors(template, debug=True):
    #x = re.findall("\{%\s*block\s*([\w-]+)\s*%\}(.*?)\{%\s*endblock\s*%\}", template, re.S)
    errors = []
    origin = StringOrigin(template)
    lex = DebugLexer(template, origin).tokenize()
    parser = TypeParser(lex)
    try:
        parser.parse_vars()
    except Exception, e:
        errors = [unicode(e)]
        if debug:
            pass#raise
            import traceback; traceback.print_exc()
    return parser._vars, errors

