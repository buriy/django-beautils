from django.http import HttpResponse
from django.template.context import RequestContext
from django.template import loader

def render_to(template_path=None, **render_kw):
    def wrapper(view):
        if not callable(view):
            raise ValueError, 'Expected callable argument'
        def decorator(request, *args, **kwargs):
            view_result = view(request, *args, **kwargs) or {}
            if isinstance(view_result, HttpResponse):
                return view_result
            view_result.update(render_kw)
            context = RequestContext(request, view_result)
            template = loader.get_template(view_result.pop('template', template_path))
            return HttpResponse(template.render(context))
        return decorator
    return wrapper