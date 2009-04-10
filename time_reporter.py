import logging
from time import time

class TimeReporter(object):
    def __init__(self, point):
        self.point = point
    
    def __call__(self, func):
        def wrapped_func(*args, **kwds):
            start_time = time()
            result = func(*args, **kwds)
            end_time = time()
            logger = logging.getLogger(self.point)
            logger.info('execution time %5.2f ms' % (
                (end_time - start_time) * 1000))
            return result
        return wrapped_func

