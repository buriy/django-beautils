import traceback
import sys
import cStringIO
import logging
import time
import os

try:
    import settings
except:
    class Settings: pass
    settings = Settings()
    settings.LOG_FILENAME = 'log'

#you should set it to empty string if you don't want to run basicConfig
if hasattr(settings, 'LOG_FILENAME'):
    log_filename = settings.LOG_FILENAME

if hasattr(settings, 'LOG_LEVEL'):
    log_level = settings.LOG_LEVEL
else:
    log_level = logging.DEBUG

if log_filename:
    time_now = time.strftime("%Y-%m-%d")
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(levelname)-8s %(name)12s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='%s-%s.log' % (log_filename, time_now),
                        filemode='a')

logging.info("Logging started for process %s", os.getpid())

def log_exception(m, *args, **kwargs):
    ei = sys.exc_info()
    sio = cStringIO.StringIO()
    traceback.print_exception(ei[0], ei[1], ei[2], file=sio)
    s = sio.getvalue().decode('utf-8')
    sio.close()
    if s[-1:] == "\n":
        s = s[:-1]
    logging.error(m+'\n'+s, *args, **kwargs)

class TimeReporter(object):
    def __init__(self, point, errors = True):
        self.point = point
        self.errors = errors
    
    def __call__(self, func):
        def wrapped_func(*args, **kwds):
            start_time = time.time()
            try:
                result = func(*args, **kwds)
            except Exception, e:
                if self.errors: 
                    logger = logging.getLogger(self.point)
                    end_time = time.time()
                    logger.warning("failed after %5.2f ms with exception: \"%s\"" % (
                        (end_time - start_time) * 1000, str(e)))
                raise e
            end_time = time.time()
            logger = logging.getLogger(self.point)
            logger.info('execution time %5.2f ms' % (
                (end_time - start_time) * 1000))
            return result
        return wrapped_func

class TimeReporterMiddleware(object):
    def get_username(self, request):
        user = 'anonymous'
        if hasattr(request, 'user') and not request.user.is_anonymous(): 
            user = request.user.username
        return user

    def format_exception(self, exception):
        return "exception \"%s\"" % exception
                    
    def format_request(self, request):
        return "for user %s, request %s %s" % (
            self.get_username(request), request.method, request.path
        )
    
    def get_time(self, request):
        try:
            start_time = request.start_time
        except Exception, e:
            logger = logging.getLogger('view.time')
            logger.error('exception in TimeReporterMiddleware: %s' % e)
            start_time = time.time()
        end_time = time.time()        
        return (end_time - start_time)
    
    def log_report(self, message, exception):
        if exception:
            logger = logging.getLogger('view.exception')
            message += self.format_exception(exception)
            logger.warning(message)
        else:
            logger = logging.getLogger('view.time')
            logger.info(message)
    
    def report(self, request, exception=None):
        delta = self.get_time(request) * 1000
        message = 'time %5.2f ms %s' % (delta, self.format_request(request))
        self.log_report(message, exception)
    
    def process_response(self, request, response):
        self.report(request)
        return response

    def process_exception(self, request, exception):
        self.report(request, exception)

    def process_request(self, request):
        request.start_time = time.time()

class QueriesTimeReporterMiddleware(TimeReporterMiddleware):
    def report(self, request, exception=None):
        from django.db import connection
        queries = len(connection.queries)
        dbtime = sum([float(q['time']) for q in connection.queries])
        pytime = self.get_time(request) - dbtime
        super(QueriesTimeReporterMiddleware, self).report(request, exception)
        message = '%s queries, db time %5.2f ms, python %5.2f ms' % (queries, dbtime, pytime)
        self.log_report(message)

@TimeReporter('time.sleep')
def sleepy():
    time.sleep(0.1)

if __name__ == "__main__":
    sleepy()
