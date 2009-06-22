from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseBadRequest

def to_autocomplete_string(results):
    if results:
        for result in results:
            yield '%s|%s\n' % (result.name, result.pk)

def autocomplete(request, queryset, search_by):
    def iter_results(results):
        if results:
            for result in results:
                label = getattr(result, search_by, unicode(result))
                yield u'%s|%s\n' % (unicode(result), result._get_pk_val())
    
    if not request.is_ajax() or not request.GET.get('q'):
        return HttpResponseBadRequest
    
    q = request.GET.get('q')
    limit = request.GET.get('limit', 15)
    try:
        limit = int(limit)
    except ValueError:
        return HttpResponseBadRequest() 

    results = queryset.filter(**{'%s__startswith' % search_by: q})[:limit]
    return HttpResponse(iter_results(results), mimetype='text/plain')

autocomplete = cache_page(autocomplete, 60 * 60)
