import os.path

from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.forms import HiddenInput, TextInput
from django.utils import simplejson
from django.utils.safestring import mark_safe

class MulticompleteWidget(TextInput):
    """
    Multicomplete widget to use with jquery-autocomplete plugin.

    Widget can use for static and dynamic (AJAX-liked) data. Also
    you can relate some fields and it's values'll posted to autocomplete
    view.

    Widget support all jquery-autocomplete options that dumped to JavaScript
    via django.utils.simplejson.

    **Note** You must init one of ``choices`` or ``choices_url`` attribute.
    Else widget raises TypeError when rendering.
    """
    def __init__(self, attrs=None, choices=None, choices_url=None, options=None, related_fields=None):
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

        if related_fields:
            extra = {}
            if isinstance(related_fields, str):
                related_fields = list(related_fields)

            for field in related_fields:
                extra[field] = "%s_value" % field

            self.extra = extra
        else:
            self.extra = {}

    class Media:
        js = ('utils/js/jquery.autocomplete.js',
              'utils/js/jquery.multicomplete.js')
        css = {'screen': ('utils/css/jquery.autocomplete.css',)}

    def render(self, name, value=None, attrs=None):
        if not value:
            value = []
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

        final_attrs = self.build_attrs(attrs)
        id = final_attrs['id']
        id_div = id + "_div_element"
        v = simplejson.dumps (value)
        MR = settings.MEDIA_URL+'utils/'
        lines = [html_code,
u"""
<div id = "%(id_div)s"></div>
<script type="text/javascript"><!--
  $(document).ready(function() {
    renderMultistringTable ("%(id_div)s",%(v)s)
  });
--></script>
""" % locals (),
super(MulticompleteWidget, self).render(name, self.choice or "", attrs),
u"""<img src='"""+ MR + u"""images/add.png' alt="%(v)s" onclick="addToMultistringTable('%(id_div)s',$('#%(id)s').val());"></img>""" % locals (),
u"""<script type="text/javascript"><!--
    %s$('#%s').autocomplete(%s%s);
--></script>
""" % (extra, id, choices, options)
        ]
        return mark_safe('\n'.join(lines))

    def set_current_choice(self, data):
        if not self.choices:
            raise ValueError('"choices" attribute was not defined yet.')

        for k, v in self.choices:
            if k == data:
                self.choice = v
                break

    def value_from_datadict(self, data, files, name):
        name_hidden = "id_" + name + "_div_element_res"
        try:
            return [s for s in data [name_hidden].split (";") if s]
        except KeyError:
            return []

        if not self.choices:
            return super(MulticompleteWidget, self).value_from_datadict(data, files, name)

        autocomplete_name = name + '_autocomplete'

        if not autocomplete_name in data:
            self.set_current_choice(data[name])
            return data[name]

        for k, v in self.choices:
            if v == data[autocomplete_name]:
                self.set_current_choice(k)
                return k
 