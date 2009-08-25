from django.conf import settings
from django.contrib.admin.options import ModelAdmin
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.contrib.admin import site
from django.contrib.admin.util import quote
import admin_auth #@UnusedImport

def new_render(self, name, value, *args, **kwargs):
    rel_to = self.rel.to
    related_url = '../../../%s/%s/' % (rel_to._meta.app_label, rel_to._meta.object_name.lower())
    self.widget.choices = self.choices
    output = [self.widget.render(name, value, *args, **kwargs)]
    if rel_to in self.admin_site._registry: # If the related object has an admin interface:
        # TODO: "id_" is hard-coded here. This should instead use the correct
        # API to determine the ID dynamically.
        output.append(u'<a href="%sadd/" class="add-another" id="add_id_%s" onclick="return showAddAnotherPopup(this);"> ' % \
            (related_url, name))
        output.append(u'<img src="%simg/admin/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Add Another')))
        if value:
            output.append(u'<a href="%s%s/" class="edit-it" id="edit_id_%s"> ' % \
                (related_url, value, name))
            output.append(u'<img src="%simg/admin/icon_changelink.gif" width="10" height="10" alt="%s"/></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Edit object')))
    return mark_safe(u''.join(output))

original_render = RelatedFieldWidgetWrapper.render
RelatedFieldWidgetWrapper.render = new_render

def get_admin_object_url(instance):
    """
    Returns the admin URL to edit the object represented by this log entry.
    This is relative to the Django admin index page.
    """
    opts = instance.__class__._meta
    root = reverse(site.root, args=[''])
    return mark_safe(u"%s%s/%s/%s/" % (root, opts.app_label, opts.object_name.lower(), quote(instance.pk)))

def get_admin_class_url(model):
    """
    Returns the admin URL to edit the object represented by this log entry.
    This is relative to the Django admin index page.
    """
    opts = model._meta
    root = reverse(site.root, args=[''])
    return mark_safe(u"%s%s/%s/" % (root, opts.app_label, opts.object_name.lower()))

def fieldlist(model, exclude=['id']):
    return [x.name for x in model._meta.fields if not x.name in exclude]

def reg_simple(model, klass=ModelAdmin, exclude=['id'], include=[], **kwargs):
    class admin(klass):
        list_display = fieldlist(model, exclude) + include
    
    for k,v in kwargs.iteritems():
        setattr(admin, k, v)
        
    site.register(model, admin)