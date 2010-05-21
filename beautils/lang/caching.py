import cPickle as pickle
try:
    from hashlib import md5 as md5_new #@UnusedImport
except:
    from md5 import md5 as md5_new #@Reimport

def cache_function(length):
    """
    A variant of the snippet posted by Jeff Wheeler at
    http://www.djangosnippets.org/snippets/109/
    
    Caches a function, using the function and its arguments as the key, and the return
    value as the value saved. It passes all arguments on to the function, as
    it should.
    
    The decorator itself takes a length argument, which is the number of
    seconds the cache will keep the result around.
    
    It will put in a MethodNotFinishedError in the cache while the function is
    processing. This should not matter in most cases, but if the app is using
    threads, you won't be able to get the previous value, and will need to
    wait until the function finishes. If this is not desired behavior, you can
    remove the first two lines after the ``else``.
    """
    def decorator(func):
        def inner_func(*args, **kwargs):
            from django.core.cache import cache
            
            raw = [func.__name__, func.__module__, args, kwargs]
            pickled = pickle.dumps(raw, protocol=pickle.HIGHEST_PROTOCOL)
            key = md5_new(pickled).hexdigest()
            value = cache.get(key)
            if cache.has_key(key):
                return value
            else:
                # This will set a temporary value while ``func`` is being
                # processed. When using threads, this is vital, as otherwise
                # the function can be called several times before it finishes
                # and is put into the cache.
                class MethodNotFinishedError(Exception): pass
                cache.set(key, MethodNotFinishedError(
                    'The function %s has not finished processing yet. This \
value will be replaced when it finishes.' % (func.__name__)
                ), length)
                result = func(*args, **kwargs)
                cache.set(key, result, length)
                return result
        return inner_func
    return decorator
