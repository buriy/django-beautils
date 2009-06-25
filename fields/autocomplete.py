from django import forms
from django.utils.safestring import mark_safe
from django.utils.text import truncate_words

from django.contrib import admin
from django.db import models
from django.conf.urls.defaults import patterns

import settings
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect

from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode 
from django.utils.html import escape


class ForeignKeySearchInput(forms.HiddenInput):
    """
    A Widget for displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.
    """
    class Media:
        css = {
            'all': ('utils/css/jquery.autocomplete.css',)
        }
        js = (
            'utils/js/jquery.js',
            'utils/js/jquery.autocomplete.js',
            'utils/js/AutocompleteObjectLookups.js',
        )

    def label_for_value(self, value):
        key = self.rel.get_related_field().name
        obj = self.rel.to._default_manager.get(**{key: value})
        return truncate_words(obj, 14)

    def __init__(self, rel, search_fields, attrs=None):
        self.rel = rel
        self.search_fields = search_fields
        super(ForeignKeySearchInput, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}
        rendered = super(ForeignKeySearchInput, self).render(name, value, attrs)
        if value:
            label = self.label_for_value(value)
        else:
            label = u''
        return rendered + mark_safe(u'''
<input type="text" id="lookup_%(name)s" value="%(label)s" size="40"/>
<script type="text/javascript">

function addItem_id_%(name)s(id, name) {
    
    $("#id_%(name)s").val( id );
    $("#lookup_%(name)s").val( name );
}

$(document).ready(function(){

function liFormat_%(name)s (row, i, num) {
    var result = row[0] ;
    return result;
}
function selectItem_%(name)s(li) {
    if( li == null ) var sValue = '';
    if( !!li.extra ) var sValue = li.extra[0];
    else var sValue = li.selectValue;
    $("#id_%(name)s").val( sValue );
}

// --- Autocomplete ---
$("#lookup_%(name)s").autocomplete("../search/", {
        extraParams: {
        search_fields: '%(search_fields)s',
        app_label: '%(app_label)s',
        model_name: '%(model_name)s',
    },
    delay:10,
    minChars:0,
    matchSubset:1,
    autoFill:false,
    matchContains:1,
    cacheLength:10,
    selectFirst:true,
    formatItem:liFormat_%(name)s,
    maxItemsToShow:20,
    onItemSelect:selectItem_%(name)s
}); 
// --- Autocomplete ---
});
</script>

        ''') % {
            'search_fields': ','.join(self.search_fields),
            'MEDIA_URL': settings.MEDIA_URL,
            'model_name': self.rel.to._meta.module_name,
            'app_label': self.rel.to._meta.app_label,
            'label': label,
            'name': name,
            'value': value,
        }


class ManyToManySearchInput(forms.MultipleHiddenInput):
    """
    A Widget for displaying ForeignKeys in an autocomplete search input 
    instead in a <select> box.
    """
    class Media:
        css = {
            'all': ('utils/css/jquery.autocomplete.css',)
        }
        js = (
            'utils/js/jquery.js',
            'utils/js/jquery.autocomplete.js',
            'utils/js/AutocompleteObjectLookups.js ',
        )


    def __init__(self, rel, search_fields, attrs=None):
        self.rel = rel
        self.search_fields = search_fields
        super(ManyToManySearchInput, self).__init__(attrs)
        self.help_text = ''
        #self.help_text = u"Two symbols to search"

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}

        if value is None:
            value = []
        
        label = ''
        selected = ''
        for id in value:
            obj = self.rel.to.objects.get(id=id)

            selected = selected + mark_safe(u"""
                <div class="to_delete deletelink" ><input type="hidden" name="%(name)s" value="%(value)s"/>%(label)s</div>""" 
                )%{
                    'label': obj.name,
                    'name': name,
                    'value': obj.id,
        }

        
        return mark_safe(u'''
<input type="text" id="lookup_%(name)s" value="" size="40"/>%(label)s
<div class="ac_chosen" style="padding-left:105px; width:1000px;">
<font style="color:#999999;font-size:10px !important;">%(help_text)s</font>
<div id="box_%(name)s" style="padding-left:20px;cursor:pointer;">

    %(selected)s
</div></div>

<script type="text/javascript">

function addItem_id_%(name)s(id,name) {
    // --- add element from popup ---
    $('<div class="to_delete deletelink"><input type="hidden" name="%(name)s" value="'+id+'"/>'+name+'</div>')
    .click(function () {$(this).remove();})
    .appendTo("#box_%(name)s");

    $("#lookup_%(name)s").val( '' );
}

$(document).ready(function(){
    function liFormat_%(name)s (row, i, num) {
        var result = row[0] ;
        return result;
    }
    function selectItem_%(name)s(li) {
        if( li == null ) return

        // --- create new element ---
        $('<div class="to_delete deletelink"><input type="hidden" name="%(name)s" value="'+li.extra[0]+'"/>'+li.selectValue+'</div>')
        .click(function () {$(this).remove();})
        .appendTo("#box_%(name)s");

        $("#lookup_%(name)s").val( '' );
    }
        
    // --- Autocomplete ---
    $("#lookup_%(name)s").autocomplete("../search/", {
            extraParams: {
            search_fields: '%(search_fields)s',
            app_label: '%(app_label)s',
            model_name: '%(model_name)s',
        },
        delay:10,
        minChars:0,
        matchSubset:1,
        autoFill:false,
        matchContains:1,
        cacheLength:10,
        selectFirst:true,
        formatItem:liFormat_%(name)s,
        maxItemsToShow:20,
        onItemSelect:selectItem_%(name)s
    }); 
// --- delete initial elements ---
    $(".to_delete").click(function () {$(this).remove();});
});
</script>

        ''') % {
            'search_fields': ','.join(self.search_fields),
            'model_name': self.rel.to._meta.module_name,
            'app_label': self.rel.to._meta.app_label,
            'label': label,
            'name': name,
            'value': value,
            'selected':selected,
            'help_text':self.help_text
        }

class AutocompleteModelAdmin(admin.ModelAdmin):
    def get_urls(self):
        base = super(AutocompleteModelAdmin, self).get_urls()
        return patterns('', ('search/$', self.search)) + base 

    def urls(self):
        return self.get_urls()
    urls = property(urls)
    
    def __call__(self, request, url):
        if url is None:
            pass
        elif url == 'search':
            return self.search(request)
        return super(AutocompleteModelAdmin, self).__call__(request, url)

    def search(self, request):
        
        #       Searches in the fields of the given related model and returns the 
        #       result as a simple string to be used by the jQuery Autocomplete plugin
        
        query = request.GET.get('q', '')

        app_label = request.GET.get('app_label', None)
        model_name = request.GET.get('model_name', None)
        search_fields = request.GET.get('search_fields', None)

        #print '-----------------------'
        #print search_fields, app_label, model_name, query
        
        if search_fields and app_label and model_name and query != None:
            def construct_search(field_name):
                # use different lookup methods depending on the notation
                if field_name.startswith('^'):
                    return "%s__istartswith" % field_name[1:]
                elif field_name.startswith('='):
                    return "%s__iexact" % field_name[1:]
                elif field_name.startswith('@'):
                    return "%s__search" % field_name[1:]
                else:
                    return "%s__icontains" % field_name

            model = models.get_model(app_label, model_name)
            q = None
            for field_name in search_fields.split(','):
                name = construct_search(field_name)
                #print name,'=',query
                if q:
                    q = q | models.Q( **{str(name):query} )
                else:
                    q = models.Q( **{str(name):query} )
            #print 'q = ', q
            qs = model.objects.filter( q )
            #print 'qs = ', qs
            
            data = ''.join([u'%s|%s\n' % (f.__unicode__(), f.pk) for f in qs])
            return HttpResponse(data)
        return HttpResponseNotFound()

    def formfield_for_dbfield(self, db_field, request=None, **kwargs):
        related_search_fields = getattr(self, 'related_search_fields', {})
        # For ForeignKey use a special Autocomplete widget.
        if isinstance(db_field, models.ForeignKey) and db_field.name in related_search_fields:
            kwargs['widget'] = ForeignKeySearchInput(db_field.rel,
                                    related_search_fields[db_field.name])

            # extra HTML to the end of the rendered output.
            formfield = db_field.formfield(**kwargs)
            # Don't wrap raw_id fields. Their add function is in the popup window.
            if not db_field.name in self.raw_id_fields:
                # formfield can be None if it came from a OneToOneField with
                # parent_link=True
                if formfield is not None:
                    formfield.widget = AutocompleteWidgetWrapper(formfield.widget, db_field.rel, self.admin_site)
            return formfield
                    
        # For ManyToManyField use a special Autocomplete widget.
        if isinstance(db_field, models.ManyToManyField)and db_field.name in related_search_fields:
            kwargs['widget'] = ManyToManySearchInput(db_field.rel,
                                    related_search_fields[db_field.name])
            db_field.help_text = ''

            # extra HTML to the end of the rendered output.
            formfield = db_field.formfield(**kwargs)
            # Don't wrap raw_id fields. Their add function is in the popup window.
            if not db_field.name in self.raw_id_fields:
                # formfield can be None if it came from a OneToOneField with
                # parent_link=True
                if formfield is not None:
                    formfield.widget = AutocompleteWidgetWrapper(formfield.widget, db_field.rel, self.admin_site)
            return formfield
        
        return super(AutocompleteModelAdmin, self).formfield_for_dbfield(db_field, request=request, **kwargs)
    
    def response_add(self, request, obj, post_url_continue='../%s/'):
        """
        Determines the HttpResponse for the add_view stage.
        """
        opts = obj._meta
        pk_value = obj._get_pk_val()
        
        msg = _('The %(name)s "%(obj)s" was added successfully.') % {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj)}
        # Here, we distinguish between different save types by checking for
        # the presence of keys in request.POST.
        if request.POST.has_key("_continue"):
            self.message_user(request, msg + ' ' + _("You may edit it again below."))
            if request.POST.has_key("_popup"):
                post_url_continue += "?_popup=%s" % request.POST.get('_popup')
            return HttpResponseRedirect(post_url_continue % pk_value)
        
        if request.POST.has_key("_popup"):
            #htturn response to Autocomplete PopUp
            if request.POST.has_key("_popup"):
                return HttpResponse('<script type="text/javascript">opener.dismissAutocompletePopup(window, "%s", "%s");</script>' % (escape(pk_value), escape(obj)))
                        
        elif request.POST.has_key("_addanother"):
            self.message_user(request, msg + ' ' + (_("You may add another %s below.") % force_unicode(opts.verbose_name)))
            return HttpResponseRedirect(request.path)
        else:
            self.message_user(request, msg)

            # Figure out where to redirect. If the user has change permission,
            # redirect to the change-list page for this object. Otherwise,
            # redirect to the admin index.
            if self.has_change_permission(request, None):
                post_url = '../'
            else:
                post_url = '../../../'
            return HttpResponseRedirect(post_url)
    
class AutocompleteWidgetWrapper(RelatedFieldWidgetWrapper):
    def render(self, name, value, *args, **kwargs):
        rel_to = self.rel.to
        related_url = '../../../%s/%s/' % (rel_to._meta.app_label, rel_to._meta.object_name.lower())
        self.widget.choices = self.choices
        output = [self.widget.render(name, value, *args, **kwargs)]
        if rel_to in self.admin_site._registry: # If the related object has an admin interface:
            # TODO: "id_" is hard-coded here. This should instead use the correct
            # API to determine the ID dynamically.
            output.append(u'<a href="%sadd/" class="add-another" id="add_id_%s" onclick="return showAutocompletePopup(this);"> ' % \
                (related_url, name))
            output.append(u'<img src="%simg/admin/icon_addlink.gif" width="10" height="10" alt="%s"/></a>' % (settings.ADMIN_MEDIA_PREFIX, _('Add Another')))
        return mark_safe(u''.join(output))
