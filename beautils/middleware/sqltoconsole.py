from django.conf import settings
from django.db import connections
from django.template import Template, Context

#
# Log all SQL statements direct to the console (when running in DEBUG)
#

class SQLLogToConsoleMiddleware:
    def process_response(self, request, response): 
        if not settings.DEBUG:
            return response
        
        for connection_name in connections:
            connection = connections[connection_name]
            if len(connection.queries) > 0:
                time = sum([float(q['time']) for q in connection.queries])        
                t = Template("Total query count: {{ count }}\nTotal execution time: {{ time }}\n{% for sql in sqllog %}--> {{ sql.time }}: {{ sql.sql|safe }}\n{% endfor %}")
                print "%s" % t.render(Context({'sqllog':connection.queries,'count':len(connection.queries),'time':time}))        
        return response