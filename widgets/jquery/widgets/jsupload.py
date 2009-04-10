from django.forms.widgets import TextInput
import os.path
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.forms.fields import Field
from django.utils.translation import ugettext as _

class JavascriptUploadWidget (TextInput):
    image_cache = None
    def __init__(self, attrs=None, upload_url=None, options=None ):
        if upload_url is None:
            raise TypeError('"upload_url" keyword argument must be supplied to use JavascriptUploadWidget.')
        super(JavascriptUploadWidget, self).__init__(attrs)
        self.options = options or {}
        self.options['upload_url'] = upload_url
        if not "remove_img" in self.options:
            self.options["remove_img"] = "/static/icons/delete.png"
        if not "animation" in self.options:
            self.options["animation"] = "/static/icons/ajax-loader.gif"

    def js_files (self, jquery=False):
        files_list = ['js/jquery.form.js', 'js/jquery.jsupload.js', 'js/lightbox/jquery-lightbox/jquery.lightbox.js']
        if jquery:
            files_list.insert(0, 'js/jquery.js')

        return [ os.path.join(settings.MEDIA_URL, f) for f in files_list ]

    def render(self, name, value=None, attrs=None):
        images_code = u''
        options = self.options
        
        try:
            options['upload_url'] = reverse(options['upload_url'])
        except NoReverseMatch:
            pass

        if not value and self.image_cache:
            value = [[],[],[],[]]
            for img in self.image_cache:
                value[0].append (img.pk)
                value[1].append (img.name)
                value[2].append (os.path.join (settings.MEDIA_URL,img.thumbnail))
                value[3].append (os.path.join (settings.MEDIA_URL,img.filename))

        options['value'] = simplejson.dumps(value or [[],[],[],[]]) #ids, names, thumbs
        options['name'] = name
        options['upload_button_text'] = _("Upload")

        #print options
        
        options_str = simplejson.dumps(options)
        code = u"""<div id="id_%(name)s" name="%(name)s" type="file"></div>
        <script type="text/javascript"><!--
        $(function () {
            $('#id_%(name)s').jsupload ( %(options_str)s );
        });
--></script>""" % locals ()
        return mark_safe(code)
    
    def value_from_datadict(self, data, files, name):
        key = 'file_list_id_' + name
        if key in data:
            value = simplejson.loads(data[key])
        else:
            value = []

        return value
    
class JavascriptUploadField(Field):
    widget = JavascriptUploadWidget

    def clean(self, data, initial=None):
        return data
 