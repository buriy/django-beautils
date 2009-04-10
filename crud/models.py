from crud.views import Controller

_crud_cache = {}

def get_CRUDs():
    return [v for k,v in sorted(_crud_cache.iteritems())]

def registerCRUD(path=None, cls=None, **kwargs):
    try:
        Crud = cls.CRUD
        Manager = getattr(Crud, 'MANAGER', Controller)
        instance = Manager(Form=cls, **Crud.__dict__)
        cls._crud = instance
        del cls.CRUD
    except Exception:
        import traceback;traceback.print_exc()
        raise
    kwargs['path'] = path
    kwargs['name'] = kwargs.get('name', instance.INDEX)
    kwargs['model'] = kwargs.get('model', instance.Model._meta.object_name)
    kwargs['verbose_name'] = kwargs.get('verbose_name', instance.Model._meta.verbose_name.capitalize())
    kwargs['verbose_name_plural'] = kwargs.get('verbose_name_plural', instance.Model._meta.verbose_name_plural.capitalize())
    kwargs['group'] = kwargs.get('group', instance.__module__)
    uid = kwargs['group']+':'+kwargs['name']
    instance.__dict__.update(**kwargs)
    _crud_cache[uid] = instance
    
def autodiscover():
    """
    Auto-discover INSTALLED_APPS views.py modules and fail silently when 
    not present. This forces an import on them to register any admin bits they
    may want.
    """
    import imp
    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        try:
            appinit = __import__(app, {}, {}, [app.split(".")[-1]])
            imp.find_module("controllers", appinit.__path__)
        except ImportError:
            # there is no app controllers.py, skip it
            continue
        __import__("%s.controllers" % app)
