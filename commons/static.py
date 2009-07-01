import types
import sys

class StaticMeta(type):
    _registry = {}
    
    def __new__(metaclass, name, bases, attrs): #@NoSelf
        super_new = super(StaticMeta, metaclass).__new__
        parents = [b for b in bases if isinstance(b, StaticMeta)]
        if not parents and name != 'Static':
            # should be created with __metaclass__ = type 
            return super_new(metaclass, name, bases, attrs)

        # Create the class.
        class_instance = super_new(metaclass, name, bases, {'__module__': attrs.pop('__module__')})
        
        # If class overrides our _new_
        if '_add_to_class_' in attrs:
            class_instance._add_to_class_ = classmethod(attrs.pop('_add_to_class_'))
        
        if '_new_' in attrs:
            class_instance._add_to_class_('_new_', classmethod(attrs.pop('_new_'))) 
        
        # Run attribute initializers
        class_instance._new_(attrs, parents)
        
        # Call constructor method
        class_instance._init_()

        #StaticMeta.register(module, name, class_instance)
        #register_models(class_instance._meta.app_label, class_instance)
        class_name = class_instance._name_()
        #print "Registering", class_name
        if not class_name in metaclass._registry:
            metaclass._registry[class_name] = class_instance
        
        # Because of the way imports happen (recursively), we may or may not be
        # the first time this model tries to register with the framework. There
        # should only be one class for each model, so we always return the
        # registered version.
        return metaclass._registry[class_name]

class Static(object):
    __metaclass__ = StaticMeta

    def __new__(self, *args, **kwargs):
        raise Exception("Class instantiation is not allowed for %s" % self)

    def _add_to_class_(self, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(self, name)
        elif isinstance(value, types.FunctionType):
            setattr(self, name, classmethod(value))
        elif isinstance(value, property):
            raise "Properties are not supported!", name
        else:
            setattr(self, name, value)

    def _new_(self, attrs, parents):
        for name, attr in attrs.iteritems():
            self._add_to_class_(name, attr)

    def _init_(self):
        pass

    def _name_(self):
        model_module = sys.modules[self.__module__]
        return model_module.__name__ + '.'+self.__name__
    
def test():
    """
    >>> test()
    Creating __main__.Test
    Creating __main__.Test2 with x=1, y=2
    Test.x = 0
    Test.method(1) = 1
    Test2.x = 1
    Test2.method(1) = (5, 1, 2)
    """
    
    class Test(Static):
        x = 0
        def _init_(self):
            print 'Creating', self._name_()
    
        def method(self, arg):
            return arg

            
    class Test2(Test):
        x = 1
        y = 2
        
        def method(self, arg):
            return arg, self.x, self.y

        def _name_(self):
            return super(self, self)._name_() + ' with x=%s, y=%s' % (self.x, self.y) 

    print 'Test.x =', Test.x
    try:
        # Static classes instantiations are disabled by default
        Test(a=1)
        assert False
    except Exception:
        pass
    print 'Test.method(1) =', Test.method(1)
    print 'Test2.x =', Test2.x
    print 'Test2.method(1) =', Test2.method(5)


if __name__ == '__main__':
    if '--debug' in sys.argv:
        test()
    else:
        import doctest
        print 'Tests: %s failures of %s tests' % doctest.testmod()