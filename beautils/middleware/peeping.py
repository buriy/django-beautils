from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404

class AdminPeepingMiddleware(object):
    """
    Peeping middleware, that replaces active user to another one
    for current http request. Admin permissions required to activate,
    so you can place this snippet even on the production server.
    Very useful for debugging purposes. Wish it to be part of Django.
    How to use:
    Just add ?as_user=<username> or &as_user=<username> to the request,
    where username is the name of user whose views you want to see.
    """
    def process_request(self, request):
        if 'as_user' in request.GET:
            if not request.user.is_superuser: raise Http404
            as_user = request.GET.get('as_user')
            rpc = request.GET.copy()
            #XXX: removing because some views don't like additional arguments :(
            del rpc['as_user']
            request.GET = rpc
            user = get_object_or_404(User, username = as_user)
            request.user = user
