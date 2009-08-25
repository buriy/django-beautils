from arrays import parse_list
from bparser import get_blocks
from django.template import TemplateSyntaxError
from django.utils.datastructures import SortedDict
import re

DEBUG = False

SUBBLOCKS = re.compile("{%\s*block\s*([^%]+?)\s*%}{%\s*endblock\s*%}")

class Gatherer(object):
    ERRORS_IGNORE = 'ignore'
    ERRORS_RAISE = 'raise'
    def __init__(self, template = None, blocks = None, errors=ERRORS_RAISE):
        self.errors = errors
        if DEBUG: print "G: New gatherer created"
        if not blocks:
            blocks = SortedDict()
        self.blocks = blocks
        self.templates = []
        if template:
            self.apply_all(template)
        
    def apply(self, template): # apply to text or 
        if not template: return
        self.remove_hidden()
        update_types = hasattr(template, 'variables')
        try:
            if not self.blocks:
                if DEBUG: print "G: Applying", template
                self.blocks.update(get_blocks(template))
            else:
                if not update_types or template.source:
                    if DEBUG: print "G: Updating from", template, update_types and "with types" or "without types"
                    self.update_existing(get_blocks(template), update_types)
                pass
        except TemplateSyntaxError:
            if self.errors == Gatherer.ERRORS_RAISE:
                raise
            if DEBUG: print "Error: Failed to parse template '%s'." % template
        if update_types and not template.source:
            #FIXME: Remove this later
            if DEBUG: print "G: Updating vars from", template
            self.update_variables(template.variables.all())
        
    def apply_all(self, template):
        if hasattr(template, 'base') and template.base:
            self.apply_all(template.base)
        self.apply(template)
    
    def update_variables(self, variables):
        var_blocks = dict([(v.name,v) for v in variables])
        self.update_existing(var_blocks, update_types=True)

    def remove_hidden(self):
        for b in self.blocks.keys():
            if self.blocks[b].hidden:
                del self.blocks[b]

    def update_existing(self, new_blocks, update_types=False):
        if not new_blocks: return
        for b in new_blocks.keys():
            if b in self.blocks.keys():
                sb = self.blocks[b]
                new = new_blocks[b]
                sb.value = new.value
                if update_types:
                    if new.type == 'block' and sb.type != 'block':
                        sb.type = 'html'
                        sb.value = SUBBLOCKS.sub("{# \1 #}", sb.value) # no blocks under not-blocks allowed
                    elif new.type == 'link-section':
                        new.type = 'section'
                    elif new.type == 'hide':
                        sb.hidden = True
                    else:
                        sb.type = new.type
                if new.hidden:
                    sb.hidden = True
                        
    def update_from_request(self, vars, types=False):
        if DEBUG: print "G: Updating vars from request"
        for var_name, value in self.blocks.iteritems():
            new_value = vars.get('val-'+var_name, None)
            #print var_name, value, new_value
            if value.type == 'bool':
                value.value = new_value and True or False
            elif value.type == 'list' and new_value != None:
                value.value = parse_list(new_value)
            elif new_value != None:
                value.value = new_value
            if types:
                new_type = vars.get('type-'+var_name, None)
                new_hide = vars.get('hide-'+var_name, None)
                if new_type != value.type and new_type:
                    if value.type in ['bool', 'list']:
                        value._value = unicode(value.value)
                        value._type = new_type
                    value.type = new_type
                value.hidden = new_hide != None
                
        def __unicode__(self):
            return ""
    
    #def visible(self):
    #    return SortedDict([b for b in self.blocks.items() if not b.hidden])

def make_block(blocks, v, parent=None):
    if not v:
        return ''
    if v.type != 'block':
        return "{{ %s }}" % v.name
    v.parent = parent 
    pv = SUBBLOCKS.sub(lambda x: make_block(blocks, blocks.get(x.group(1), None), v), v.print_value())
    return '{%% block %s %%}%s{%% endblock %%}' % (v.name, pv)

def make_source(base, blocks, types = False):
    s = ['{%% extends "%s" %%}' % base]
    for k,v in blocks.iteritems():
        if v.type == 'block': continue
        mode = v.type
        tk = mode+":"+k 
        pv = v.print_value()
        if mode == 'bool':
            s.append('{%% set %s=%s %%}' % (k, pv))
        else:
            longform = ('"' in v.value or '\n' in v.value or '{{' in v.value or '{%' in v.value) or mode in ['html', 'list']
            if longform:
                if mode in ['text', 'html']: tk = k
                s.append('{%% set %s %%}%s{%% endset %%}' % (tk, pv))
            else:
                if mode == 'text': tk = k
                s.append('{%% set %s="%s" %%}' % (tk, pv))
            
    for k,v in blocks.iteritems():
        if v.type == 'block': # hide hide-block
            if not v.parent:
                block = make_block(blocks, v)
                s.append(block)
            

    for k,v in blocks.iteritems():
        if v.hidden:
            s.append('{%% hide %s %%}' % k)
    
    return '\n'.join(s)
