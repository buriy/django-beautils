from fragments.arrays import print_list

class BlockVar(object):
    def __init__(self, name, value, parent, comments):
        assert isinstance(name, basestring)
        self.name = name
        self.value = value
        self.parent = parent
        self.type = 'block'
        self.hidden = False
        description = []
        self.desc = '\n'.join(description)

    def print_value(self):
        return self.value
        
    def indent(self):
        if self.parent != None:
            return '+'+self.parent.indent()
        else:
            return ''
    
    def __repr__(self):
        return '<Block "%s">' % self.name
    
    def __unicode__(self):
        return 'Block "%s"' % self.name

class SimpleVar(object):
    def __init__(self, name, type, value='', desc=''):
        assert isinstance(name, basestring)
        self.name = name
        self.desc = desc
        self.hidden = False
        self.type = type
        self.value = value
    
    def get_value(self):
        return self._value
    
    def get_type(self):
        return self._type
    
    def set_value(self, value):
        #if self.name == 'section_name':
        #    print type, value
        #dynamic type detection
        if self.type == 'bool' and value in ['true', 'false']:
            value = (value == 'true')
        elif self.type == 'text' and (value in [True, False]):
            self._type = 'bool'
        elif self.type in ['text', 'html'] and type(value) is list:
            self._type = 'list'
        elif self.type == 'text' and ('"' in value or '\n' in value or '{{' in value):
            self._type = 'html'
        self._value = value
    
    def set_type(self, type):
        assert type != 'block', "Use BlockVar for blocks!"
        self._type = type
        if hasattr(self, '_value'):
            self.set_value(self.get_value())
    
    value = property(get_value, set_value)
    type  = property(get_type, set_type)
        
    def print_value(self):
        if self.type == 'list':
            return print_list(self.value)
        elif self.type == 'bool':
            return self.value and 'true' or 'false'
        else:
            return '%s' % self.value
        
    def __repr__(self):
        return '<SimpleVar "%s" (%s)>' % (self.name, self.type)
    
    def __unicode__(self):
        return '%s "%s" = %s' % (self.type, self.name, self.value)
