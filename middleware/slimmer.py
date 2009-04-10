from wn.io import slimmer
import time, datetime
from django.conf import settings

class SlimmerMiddleware(object):
    def process_response(self, request, response):
        original_length = len(response.content)
        start = time.time()
        if not settings.DEBUG:
            response.content = slimmer.xhtml_slimmer(response.content)
        end = time.time() - start
        
        if response.content.startswith('<html'):
            response.content += '\n<!--This page was packed %s from %dK to %dK in %fms  -->' % (datetime.datetime.now().strftime('%a %d %b %Y at %H:%M:%S'), float(original_length) / 1024, float(len(response.content)) / 1024, end)
        return response
        
