import os

from django.conf import settings
from django.forms import TextInput
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

USE_DATE_INPUT = False

day_names = u"Date.dayNames=%s;" % simplejson.dumps([_('Sunday'), _('Monday'), _('Tuesday'),
                              _('Wednesday'), _('Thursday'), _('Friday'), _('Saturday')],
                              ensure_ascii=False)
abbr_day_names = u"Date.abbrDayNames=%s;" % simplejson.dumps( [_('Sun'), _('Mon'), _('Tue'),
                              _('Wed'), _('Thu'), _('Fri'), _('Sat')],
                              ensure_ascii=False)
month_names = u"Date.monthNames=%s;" % simplejson.dumps( [_('January'), _('February'), _('March'),
                              _('April'), _('May'), _('June'), _('July'), _('August'),
                              _('September'), _('October'), _('November'), _('December')],
                              ensure_ascii=False)
date_button_name = u"$.dpText.TEXT_CHOOSE_DATE = %s;" % _(simplejson.dumps('Show calendar',ensure_ascii=False))

datePicker_set_locale = day_names + abbr_day_names + month_names + date_button_name

class DatePickerWidget (TextInput):
    def __init__(self, attrs=None, options=None):
        self.attrs = attrs or {}
        self.options = options or {}
    
    def js_files(self, jquery=False):
        if not USE_DATE_INPUT:
            files_list = ['widgets/date_input/jquery.datePicker.js',
                          'widgets/date_input/date.js']
        else:
            files_list = ['widgets/date_input/jquery.dimensions.js',
                          'widgets/date_input/jquery.date_input.js']
            localization_file = 'jQuery date_input localization file name'
            fname = _(localization_file)
            if fname != unicode (localization_file):
                files_list.append ('widgets/date_input/' + fname.encode('utf8'))

        if jquery:
            files_list.insert(0, 'js/jquery.js')

        return [os.path.join(settings.MEDIA_URL, f) for f in files_list]
    def render(self, name, value=None, attrs=None):
        if USE_DATE_INPUT:
            self.attrs['class']='date_input' #'date-pick'
        else:
            self.attrs['class']='date-pick'
        html_code = super (DatePickerWidget, self).render (name, value=value, attrs=attrs)
        final_attrs = self.build_attrs(attrs)
        id = final_attrs['id']
        if USE_DATE_INPUT:
            html_code += u"""
<script type="text/javascript"><!--
  $(document).ready(function() {
  $("#%(id)s").date_input();
 });
--></script>
""" % locals ()
        else:
            loc = datePicker_set_locale
            html_code += u"""
<script type="text/javascript"><!--
  Date.format = 'yyyy-mm-dd';
  %(loc)s
  $(document).ready(function() {
  $("#%(id)s").datePicker({startDate:'1950-01-01'});
 });
--></script>
""" % locals ()
        return mark_safe(html_code)
            