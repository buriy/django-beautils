from django.db import connection
from django.template import Template, Context
from django.conf import settings

#
# Log all SQL statements direct to the console (when running in DEBUG)
#

class SQLLogToConsoleMiddleware:
    def process_response(self, request, response): 
        if settings.DEBUG:
            if len(connection.queries) > 0:
                time = sum([float(q['time']) for q in connection.queries])        
                t = Template("Total query count: {{ count }}\nTotal execution time: {{ time }}\n{% for sql in sqllog %}--> {{ sql.time }}: {{ sql.sql|safe }}\n{% endfor %}")
                print "%s" % t.render(Context({'sqllog':connection.queries,'count':len(connection.queries),'time':time}))        
        return response