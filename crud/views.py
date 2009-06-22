from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template.context import RequestContext
from django.views.decorators.cache import never_cache
from django.core.paginator import InvalidPage, QuerySetPaginator
from django.core.exceptions import FieldError
from django import http
from utils.decorators import render_to
from django.utils.translation import ugettext_lazy as _
from django.template.loader import find_template_source
from django.template import TemplateDoesNotExist
from django.db.models.fields import AutoField
from utils.timer import log_exception
from history.models import AttributeLogEntry
import traceback
import re
import logging

DEBUG = True

class Controller(object):
    """
    Sample usage:
    
    class CombinedTeamViews(Controller): 
        Model = CombinedTeam
        INDEX = 'clubs_combined'
    
    registerCRUD(group='Clubs', path='clubs', cls=ClubViews)
    registerCRUD(group='Clubs', path='clubs/types', cls=ClubTypeViews)
    """
    
    def __init__(self, Form, **kwargs):
        self.Form = Form
        self.Model = Form._meta.model
        self.__dict__.update(kwargs)
            
    @render_to()
    def root(self, request, url):
        if request.method == 'GET' and not request.path.endswith('/'):
            return http.HttpResponseRedirect(request.path + '/')

        # Figure out the admin base URL path and stash it for later use
        self.root_path = re.sub(re.escape(url) + '$', '', request.path)

        url = url.rstrip('/') # Trim trailing slash, if it exists.

        # Check permission to continue or display login form.
        if not self.has_permission(request):
            return self.login(request)

        if url == '':
            return self.index(request)
        elif url == 'add':
            return self.add(request)
        elif '/' in url:
            action, id = url.split('/', 2)
            if action == 'view':
                return self.view(request, id)
            elif action == 'edit':
                return self.edit(request, id)
            elif action == 'delete':
                return self.delete(request, id)

        raise http.Http404('The requested page does not exist.')
    
    INDEX = None
    ORDER = 'name'
    PER_PAGE = 20
    
    def get_url_path(self, x=''):
        return reverse(self.INDEX, args=[x])

    def has_permission(self, request):
        return True

    def message(self, request, template_name='crud/message.html', **dictionary):
        if not 'next' in dictionary:
            dictionary.update({'next': request.META.get('HTTP_REFERER', '/')})
        return render_to_response(template_name, dictionary, context_instance=RequestContext(request))
    message = never_cache(message)

    def get_model_name(self, op):
        return "%s/%s" % (self.Model._meta.object_name.lower(), op)

    def list_fields(self):
        avail = getattr(self.Form.Meta, 'fields', None)
        display = getattr(self, 'list_display', None)
        output = []
        for x in self.Model._meta.fields:
            if not isinstance(x, AutoField):
                if not avail or x.name in avail:
                    if not display or x.name in display:
                        output.append(x)
        return output 

    def find_template(self, name):
        modelname = self.get_model_name(name)
        try:
            find_template_source(modelname)
            template_name = modelname
        except TemplateDoesNotExist, e:
            template_name = 'crud' + '/' + name
        return template_name 
        

    def add(self, request):
        dictionary = {}
        template_name = self.find_template('add.html')
    
        if request.method == 'POST':
            form = self.Form(request.POST, request.FILES)
    
            if form.is_valid():
                try:
                    self.instance = form.save()
                    dictionary.update({
                        'error': False,
                        'next': self.get_url_path(),
                        'message': _('Added'),
                        'message_long': _('%s "%s" was successfully added.') % (self.Model._meta.verbose_name, self.instance.name),
                        'user': request.user,
                        'template': template_name
                    })
                except Exception:
                    if DEBUG: traceback.print_exc()
                    log_exception(u"Problem adding %s" % self.Model._meta.object_name)
                    dictionary.update({
                        'error': True,
                        'next': request.path,
                        'message': _('Error'),
                        'message_long': _('Unable to add %s to database.' 
                        'Please, go back and try again later.') % self.Model._meta.verbose_name
                        
                    })
    
                return self.message(request, **dictionary)
            else:
                dictionary.update({'error': _('Form error')})
        else:
            form = self.Form()
    
        dictionary.update({
            'index': self.get_url_path(),
            'name': self.Model._meta.verbose_name_plural.capitalize(),
            'nick': self.Model._meta.verbose_name.lower(),
            'nick_plural': self.Model._meta.verbose_name_plural.lower(),
            'action': self.get_model_name('add'),
            'form': form, 
            'template': template_name}
        )
        return dictionary

    def delete(self, request, id, template_name='crud/delete.html'):
        try:
            self.instance = self.Model.objects.select_related().get(pk=id)
        except self.Model.DoesNotExist:
            return HttpResponseRedirect(self.get_url_path())
    
        if request.method == 'POST' and request.POST.has_key('delete'):
            self.instance.delete()
            return HttpResponseRedirect(self.get_url_path())
    
        return {
            'index': self.get_url_path(),
            'name': self.Model._meta.verbose_name_plural.capitalize(),
            'nick': self.Model._meta.verbose_name.lower(),
            'nick_plural': self.Model._meta.verbose_name_plural.lower(),
            'club': self.instance,
            'fields': self.list_fields(),
            'template': template_name,
        }
    
    def edit(self, request, id, template_name='crud/edit.html'):
        dictionary = {}
        
        try:
            self.instance = self.Model.objects.select_related().get(pk=id)
        except self.Model.DoesNotExist:
            logging.warning(u"Cannot edit %s with id=%s" % (self.Model._meta.object_name, id))
            return HttpResponseRedirect(self.get_url_path())
        if request.method == 'POST':
            form = self.Form(request.POST, request.FILES, instance=self.instance)
    
            if form.is_valid():
                try:
                    self.instance = form.save()
                    dictionary.update({
                        'error': False,
                        'name': self.Model._meta.verbose_name_plural,
                        'nick': self.Model._meta.verbose_name.lower(),
                        'next': self.get_url_path(),
                        'message': _('Edited'),
                        'message_long': _('%s "%s" was successfully edited.') % (self.Model._meta.verbose_name, self.instance.name),
                        'template': template_name,
                    })
                except Exception:
                    if DEBUG: traceback.print_exc()
                    log_exception("Problem editing %s with id=%s" % (self.Model._meta.object_name, id))
                    dictionary.update({
                        'error': True,
                        'next': self.get_url_path(),
                        'message': _('Error'),
                        'message_long': _('Unable to edit %s. Please, try again.') % (self.Model._meta.verbose_name),
                        'template': template_name,
                    })
    
                return self.message(request, **dictionary)
        else:
            form = self.Form(instance=self.instance)
            fields = []
            if hasattr(self.Model, 'has_history'):
                fields = self.Model._history.get('fields', []) 
            if fields:
                for f in form:
                    if f.name in fields:
                        f.field.history = AttributeLogEntry.last_edited_at(self.instance, f.name) 
                        #print type(f), f.name, f.field.history
        return {
            'index': self.get_url_path(),
            'name': self.Model._meta.verbose_name_plural,
            'nick': self.Model._meta.verbose_name.lower(),
            'nick_plural': self.Model._meta.verbose_name_plural.lower(),
            'club': self.instance, 
            'action': self.get_model_name('edit'),
            'form': form,
            'template': template_name,
        }
    
    def view(self, request, id, template_name='crud/view.html'):
        try:
            self.instance = self.Model.objects.select_related().get(pk=id)
        except self.Model.DoesNotExist:
            return HttpResponseRedirect(self.get_url_path())
        return {
            'index': self.get_url_path(),
            'name': self.Model._meta.verbose_name_plural.capitalize(),
            'nick': self.Model._meta.verbose_name.lower(),
            'nick_plural': self.Model._meta.verbose_name_plural.lower(),
            'next': request.META.get('HTTP_REFERER', self.get_url_path()),
            'action': self.get_model_name('view'),
            'club': self.instance,
            'fields': self.list_fields(),
            'template': template_name,
        }
    
    def current_url(self, path, query):
        if query:
            path += '?q=' + query
        return path
    
    def filter(self, crud, query):
        return crud.filter(name__icontains=query)
    
    def index(self, request, template_name='crud/index.html'):
        order = request.REQUEST.get('o', self.ORDER)
        page = int(request.REQUEST.get('p', 1))
        query = request.REQUEST.get('q')
    
        if not query:
            query = None
    
        crud = self.Model.objects.select_related()
    
        if query:
            crud = self.filter(crud, query)
        try:
            crud = crud.order_by(order)
        except FieldError:
            return HttpResponseRedirect(self.current_url(request.path, query))
    
        paginator = QuerySetPaginator(crud, self.PER_PAGE)
    
        try:
            page = paginator.page(page)
        except InvalidPage:
            return HttpResponseRedirect(self.current_url(request.path, query))
    
        return {
            'has_history': hasattr(self.Model, 'has_history'),
            'index': self.get_url_path(),
            'action': self.get_model_name('index'),
            'name': self.Model._meta.verbose_name_plural.capitalize(),
            'nick': self.Model._meta.verbose_name.lower(),
            'nick_plural': self.Model._meta.verbose_name_plural.lower(),
            'order': order,
            'fields': self.list_fields(), 
            'page': page,
            'paginator': paginator,
            'query': query,
            'template': template_name,
        }
