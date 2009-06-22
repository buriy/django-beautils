from django.utils.simplejson.encoder import JSONEncoder
try:
    from django import newforms as forms
except ImportError:
    from django import forms

import datetime

def js(code):
    return """<script type="text/javascript"><!--
      $(document).ready(function() { """+code+""" });
    --></script>"""

class DateInput(forms.TextInput):
    class Media:
        css = {
            'screen': ('utils/css/datepicker.css',)
        }
        js = ('utils/js/jquery-1.3.2.min.js', 
              'utils/js/jquery-ui-1.7.2.custom.min.js')

    def __init__(self, options={'dateFormat': 'yy-mm-dd'}, attrs={}):
        self.options = JSONEncoder().encode(options)
        self.attrs = attrs
 
    def render_image(self, field_id):
        return u"<img class='datepicker-image' onclick=\"$('#%s').datepicker('show')\">" % field_id
 
    def render_js(self, field_id):
        return u'''<script type="text/javascript">
        $('#%s').datepicker(%s);</script>''' % (field_id, self.options)
 
    def render(self, name, value=None, attrs=None):
        klasses = attrs.get('class', '').split(' ')
        attrs['class'] = ' '.join(klasses + ['datepicker'])
        attrs['name'] = name
        id = attrs['id'] 
        
        r = super(DateInput, self).render(name, value, attrs)
        return r + self.render_image(id) + self.render_js(id)

from django.forms.widgets import Select
from django.utils.dates import MONTHS


class SelectYearMonthWidget(forms.widgets.Widget):
    """
    Mainly for credit cards
    """
    month_field = '%s_month'
    year_field = '%s_year'

    def __init__(self, attrs=None, years=None):
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year, this_year+10)

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val = map(int, value.split('-'))
        except (AttributeError, TypeError, ValueError):
            year_val = month_val = None

        output = []

        month_choices = MONTHS.items()
        month_choices.sort()
        select_html = Select(choices=month_choices).render(self.month_field % name, month_val, attrs = attrs)
        output.append(select_html)

        year_choices = [(i, i) for i in self.years]
        select_html = Select(choices=year_choices).render(self.year_field % name, year_val, attrs = attrs)
        output.append(select_html)

        return u'\n'.join(output)

    def value_from_datadict(self, data, files, name):
        y, m = data.get(self.year_field % name), data.get(self.month_field % name)
        if y and m:
            return '%s-%s' % (y, m)
        return None
