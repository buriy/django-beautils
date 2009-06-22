from django.forms.widgets import TextInput
import os.path
from django.conf import settings
from django.utils.safestring import mark_safe
from django.forms.fields import CharField
from django.forms.util import ValidationError
import operator

class ColorPickerWidget(TextInput):
    input_type = 'text'
    def __init__(self, attrs=None):
        self.files = self.js_files ()
        super (ColorPickerWidget, self).__init__(attrs=attrs)
    def js_files(self, jquery=False):
        files_list = ['widgets/farbtastic/farbtastic.js']

        if jquery:
            files_list.insert(0, 'js/jquery.js')

        files_list = [os.path.join(settings.MEDIA_URL, f) for f in files_list]

        return files_list
    def render(self, name, value, attrs=None):
        widget_str = """

<dd>
 <input type="text" id="id_%(name)s" name="%(name)s" value="%(value)s" />
 <div id="picker_%(name)s"></div>
</dd>
<script type="text/javascript" charset="utf-8">
 $(document).ready(function() {
  $('#picker_%(name)s').farbtastic('#id_%(name)s');
 });
</script>""" % locals ()

        return mark_safe(widget_str.decode())

def all(*x):
    return reduce(operator.and_, x)

class ColorPickerField(CharField):
    widget = ColorPickerWidget

    default_error_messages = {
        'hex_error': u'This is an invalid color code. It must be a html hex color code e.g. #000000',
        'empty_hex_error': u'A color value should be an empty string or consist of "#" and 6 hex digits'
    }
    
    def __init__(self, *args, **kwargs):
        super(ColorPickerField, self).__init__(*args, **kwargs)

    def clean(self, value):
        super(ColorPickerField, self).clean(value)
        if not value or value == u'None':
            return u''
        hex = '0123456789abcdefABCDEF'
        if len(value) == 7 and value[0]=='#' and all([c in hex for c in value[1:]]):
            return value
        raise ValidationError(self.error_messages['hex_error'])

    def widget_attrs(self, widget):
        return {}
