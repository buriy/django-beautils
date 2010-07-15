from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import reverse
from django.forms.forms import NON_FIELD_ERRORS
from django.http import HttpResponseRedirect, str_to_unicode
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.utils.functional import wraps
from django.utils.http import urlquote

import urllib
from django.core.mail import send_mail
try: # needed for some linux distributions like debian
    from openid.yadis import xri
except ImportError:
    from yadis import xri

def _build_context(request, extra_context=None):
    if extra_context is None:
        extra_context = {}
    context = RequestContext(request)
    for key, value in extra_context.items():
        context[key] = callable(value) and value() or value
    return context

def render(template, context, request, extra_context=None):
    result_context = _build_context(request, extra_context)
    return render_to_response(template, context, result_context)

def user_passes_test2(test_func, login_url=settings.LOGIN_URL, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """

    def decorator(view_func):
        def _wrapped_view(self, request, *args, **kwargs):
            if test_func(request.user):
                return view_func(self, request, *args, **kwargs)
            path = urlquote(request.get_full_path())
            tup = login_url, redirect_field_name, path
            return HttpResponseRedirect('%s?%s=%s' % tup)
        return wraps(view_func)(_wrapped_view)
    return decorator


def login_required2(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    actual_decorator = user_passes_test2(
        lambda u: u.is_authenticated(),
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator


def not_authenticated(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    actual_decorator = user_passes_test(
        lambda u: not u.is_authenticated(),
        login_url=settings.LOGIN_REDIRECT_URL,
        redirect_field_name=redirect_field_name)
    if function:
        return actual_decorator(function)
    return actual_decorator


def not_authenticated2(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    actual_decorator = user_passes_test2(
        lambda u: not u.is_authenticated(),
        login_url=settings.LOGIN_REDIRECT_URL,
        redirect_field_name=redirect_field_name)
    if function:
        return actual_decorator(function)
    return actual_decorator

NEXT = REDIRECT_FIELD_NAME
def get_next(request, default=settings.LOGIN_REDIRECT_URL):
    next = request.REQUEST.get(NEXT, '')
    if not next or ' ' in next:
        next = default
    if next == request.get_full_path():
        next = ''
    return next

def get_next_url(request, location='', default=settings.LOGIN_REDIRECT_URL):
    next = get_next(request)
    if next.split('?', 1)[0] == default and len(next.split('?'))>1:
        next = next.split('?', 1)[1]
    else:
        next = urllib.urlencode({'next':next})
    if '?' in location:
        return location + '&' + next
    else:
        return location + '?' + next
        

def redirect_to_next(request, default=settings.LOGIN_REDIRECT_URL):
    next = get_next(request, default)
    return HttpResponseRedirect(next)

def redirect(request, page=None, **kw):
    if not NEXT in kw:
        next = get_next(request)
        if next != settings.LOGIN_REDIRECT_URL:
            kw[NEXT] = next
    return HttpResponseRedirect("%s?%s" % (
            request.build_absolute_uri(reverse(page)),
            urllib.urlencode(kw)
    ))

def require_login(request):
    return redirect_to_login(next=urlquote(request.get_full_path()))

def add_form_error(form, data):
    nfe = form.non_field_errors()
    nfe.append(data)
    form.errors[NON_FIELD_ERRORS] = nfe

DEFAULT_NEXT = getattr(settings, 'OPENID_REDIRECT_NEXT', '/')
def clean_next(next):
    if next is None:
        return DEFAULT_NEXT
    next = str_to_unicode(urllib.unquote(next), 'utf-8')
    next = next.strip()
    if next.startswith('/'):
        return next
    return DEFAULT_NEXT


def send_email(email, role = 'user', fail_silently=False, **kw):
    subject = render_to_string('accounts/%s_email_subject.txt' % role, kw)
    message = render_to_string('accounts/%s_email.txt' % role, kw)

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, 
              [email], fail_silently=fail_silently)


