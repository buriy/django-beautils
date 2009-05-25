try:
    from django import newforms as forms
except ImportError:
    from django import forms

import datetime

class DateInput(forms.widgets.Input):
    media_type = 'jquery'
    input_type = 'text'
    def __init__(self, *a, **kw):
        super(DateInput, self).__init__(*a, **kw)


    def render(self, name, value, attrs={}):
        b = []
        if 'class' in attrs:
            b = attrs['class'].split(' ')

        b.append('date-pick')

        attrs.update({'class': ' '.join(b)})
        return super(DateInput, self).render(name, value, attrs)

    def _media(self):
        media = super(DateInput, self).media

        media_context = {
            'jquery': 
            {
                'css': {'screen': ('/media/css/datePicker.css', )},
                'js': ('/media/js/jquery.js',
                       '/media/js/date.js',
                       '/media/js/jquery.datePicker.js',
                       '/media/js/datePicker.set.js'
                       ),
            }
        }[self.media_type]


        media.add_js(media_context['js'])
        media.add_css(media_context['css'])

        return media
    media = property(_media)

try:
    from django.newforms.widgets import Widget, Select
except ImportError:
    from django.forms.widgets import Widget, Select

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
