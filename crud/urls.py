from django.conf.urls.defaults import patterns, url
from crud.models import get_CRUDs

urlpatterns = []
for opt in reversed(get_CRUDs()):
    urlpatterns += patterns('',
        url(r'^%s/(.*)$' % opt.path, opt.root, name=opt.name),
#       url(r'^cities/(.*)$', cities.root, name='geo_cities'),
    )
