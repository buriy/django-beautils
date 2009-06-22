import os.path

from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.forms import HiddenInput, TextInput
from django.utils import simplejson
from django.utils.safestring import mark_safe

class AutocompleteWidget(TextInput):
    """
    Autocomplete widget to use with jquery-autocomplete plugin.

    Widget can use for static and dynamic (AJAX-liked) data. Also
    you can relate some fields and it's values'll posted to autocomplete
    view.

    Widget support all jquery-autocomplete options that dumped to JavaScript
    via django.utils.simplejson.

    **Note** You must init one of ``choices`` or ``choices_url`` attribute.
    Else widget raises TypeError when rendering.
    """
    def __init__(self, attrs=None, choices=None, choices_url=None, options=None, related_fields=None, plain_options=None):
        """
        Optional arguments:
        -------------------

            * ``choices`` - Static autocomplete choices (similar to choices
            used in Select widget).

            * ``choices_url`` - Path to autocomplete view or autocomplete
            url name.

            * ``options`` - jQuery autocomplete plugin options. Auto dumped
            to JavaScript via SimpleJSON

            * ``related_fields`` - Fields that relates to current (value
            of this field will sended to autocomplete view via POST)
        """
        self.attrs = attrs or {}
        self.choice, self.choices, self.choices_url = None, choices, choices_url
        self.options = options or {}
        self.plain_options = plain_options or {}

        if related_fields:
            extra = {}
            if isinstance(related_fields, str):
                related_fields = [related_fields]

            for field in related_fields:
                extra[field] = "%s_value" % field

            self.extra = extra
        else:
            self.extra = {}

    class Media:
        css = {
            'screen': ('utils/css/jquery.autocomplete.css',)
        }
        js = ('utils/js/jquery-1.3.2.min.js', 
              'utils/js/jquery-ui-1.7.2.custom.min.js',
              'utils/js/jquery.autocomplete.js')

        
    def render(self, name, value=None, attrs=None):
        if not self.choices and not self.choices_url:
            raise TypeError('One of "choices" or "choices_url" keyword argument must be supplied obligatory.')

        if self.choices and self.choices_url:
            raise TypeError('Only one of "choices" or "choices_url" keyword argument can be supplied.')

        choices = ''

        if self.choices:
            self.set_current_choice(value)
            choices = simplejson.dumps([unicode(v) for k, v in self.choices], ensure_ascii=False)
            html_code = HiddenInput().render(name, value=value)
            name += '_autocomplete'
        else:
            html_code = ''

        if self.choices_url:
            try:
                choices = simplejson.dumps(reverse(str(self.choices_url)))
            except NoReverseMatch:
                choices = simplejson.dumps(self.choices_url)

        if self.options or self.extra:
            if 'extraParams' in self.options:
                self.options['extraParams'].update(self.extra)
            else:
                self.options['extraParams'] = self.extra

            options = ', ' + simplejson.dumps(self.options, indent=4, sort_keys=True)
            extra = []

            for k, v in self.extra.items():
                options = options.replace(simplejson.dumps(v), v)
                extra.append(u"function %s() { return $('#id_%s').val(); }\n" % (v, k))

            extra = u''.join(extra)
        else:
            extra, options = '', ''

        plain_options = ['%s: %s' % (k, v) for k, v in self.plain_options.items()]
        plain_options = ', '.join(plain_options)
        if plain_options:
            plain_options = '.setOptions({%s})' % plain_options

        final_attrs = self.build_attrs(attrs)
        html_code += super(AutocompleteWidget, self).render(name, self.choice or value, attrs)
        html_code += u"""
<script type="text/javascript"><!--
    %s$('#%s').autocomplete(%s%s)%s;
--></script>
""" % (extra, final_attrs['id'], choices, options, plain_options)

        return mark_safe(html_code)

    def set_current_choice(self, data):
        if not self.choices:
            raise ValueError('"choices" attribute was not defined yet.')

        for k, v in self.choices:
            if k == data:
                self.choice = v
                break

    def value_from_datadict(self, data, files, name):
        if not self.choices:
            return super(AutocompleteWidget, self).value_from_datadict(data, files, name)

        autocomplete_name = name + '_autocomplete'

        if not autocomplete_name in data:
            self.set_current_choice(data[name])
            return data[name]

        for k, v in self.choices:
            if v == data[autocomplete_name]:
                self.set_current_choice(k)
                return k
