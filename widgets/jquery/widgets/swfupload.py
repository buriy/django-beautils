from django.forms.widgets import FileInput, HiddenInput
import os.path
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils import simplejson
from django.utils.safestring import mark_safe
from django.forms.fields import ImageField
from django.utils.translation import ugettext as _

#XXX: Use for settings.py:
#SWFUPLOAD_FLASH_URL = 'swfupload/flash9.swf'
#SWFUPLOAD_UPLOAD_URL = '/upload/image/'

class SWFUploadWidget(FileInput):
    def __init__(self, attrs=None, flash_url=None, upload_url=None, options=None, handlers=None, plugins=None, js_files=None):
        if flash_url is None and not hasattr(settings, 'SWFUPLOAD_FLASH_URL'):
            raise TypeError('"flash_url" keyword argument must be supplied.')

        if upload_url is None and not hasattr(settings, 'SWFUPLOAD_UPLOAD_URL'):
            raise TypeError('"upload_url" keyword argument must be supplied.')

        super(SWFUploadWidget, self).__init__(attrs)

        self.options, self.handlers = options or {}, handlers or {}
        self.plugins, self.files = plugins or [], js_files or []

        self.options['flash_url'] = flash_url or settings.SWFUPLOAD_FLASH_URL
        self.options['upload_url'] = upload_url or settings.SWFUPLOAD_UPLOAD_URL

    def js_files(self):
        files_list = ['js/swfupload.js',]

        if 'cookies' in self.plugins:
            files_list.append('js/swfupload.cookies.js')

        if 'graceful_degradation' in self.plugins:
            files_list.append('js/swfupload.graceful_degradation.js')

        if 'queue' in self.plugins:
            files_list.append('js/swfupload.queue.js')

        if 'swfobject' in self.plugins:
            files_list.append('js/swfupload.swfobject.js')

        for f in self.files:
            if not f in files_list:
                files_list.append(f)

        for i, f in enumerate(files_list):
            files_list[i] = os.path.join(settings.MEDIA_URL, f)

        return files_list

    def render(self, name, value=None, attrs=None):
        handlers = self.handlers
        images_code = u''
        options = self.options

        options['file_post_name'] = options.get('file_post_name', name)
        options['flash_url'] = os.path.join(settings.MEDIA_URL, options['flash_url'])

        try:
            options['upload_url'] = reverse(options['upload_url'])
        except NoReverseMatch:
            pass

        if handlers:
            for k, v in self.handlers.items():
                options['%s_handler' % k] = v

        options['swfupload_element_id'] = 'ui_%s' % name
        options['custom_settings'] = {
            'progressTarget': 'progress_%s' % name,
            'cancelButtonId': 'btn_%s' % name,
        }

        options = simplejson.dumps(options, indent=4, sort_keys=True)

        if handlers:
            for k, v in self.handlers.items():
                options = options.replace(': "%s"' % v, ': %s' % v)

        js_code = mark_safe(u"""<script type="text/javascript"><!--
    var upload_%s = new SWFUpload(%s);
--></script>""" % (
            name, options
        ))

        html_code = u"""<div id="ui_%s"%s>
    <fieldset class="progressbar loaded_images" id="progress_%s">
        <legend>%s</legend>
    </fieldset>
    <div class="flash-buttons">
        <input type="button" value="%s" class="button" onclick="upload_%s.selectFiles();" />
        <input type="button" value="%s" class="button" id="btn_%s" onclick="cancelQueue(upload_%s);" />
    </div>
</div>
%s
%s
%s\n"""

        if 'graceful_degradation' in self.plugins:
            input_code = super(SWFUploadWidget, self).render(name, value, attrs)
            style = ' style="display: none;"'
        else:
            input_code, style = '', ''

        if hasattr(self, 'image_cache') and getattr(self, 'image_cache').count():
            for i in getattr(self, 'image_cache'):
                delete_url = reverse('clubs_delete_image', kwargs={'id': i.pk})
                images_code += '<li>%s\n%s\n%s\n%s</li>\n' % (
                    HiddenInput().render(name + '_cache', i.pk),
                    u'<a href="%s" class="thickbox" rel="images"><img src="%s" alt="%s" title="%s" width="%d" height="%d" /></a>' % (
                        i.get_filename_url(), i.get_thumbnail_url(), i.name, i.name,
                        i.get_thumbnail_width(), i.get_thumbnail_height()
                    ),
                    u'<span>%s</span>' % i.name,
                    u'<a href="%s" onclick="deleteImage(\'%s\', $(this).parent()); return false;">%s</a>' % (
                        delete_url, delete_url, unicode(_('Delete'))
                    ),
                )
            js_function = """<script type="text/javascript"><!--
    function deleteImage(url, elem) {
        $.ajax({
            mode: 'queue',
            url: url,
            success: function(html) {
                var ul = $(elem).parent();
                $(elem).remove();

                if (!ul.children().length) {
                    ul.remove();
                }
            }
        });
    }
--></script>"""
            images_code = mark_safe(u'%s\n<ul class="loaded_images">\n%s</ul>' % (js_function, images_code))

        return mark_safe(html_code % (
            name, style, name, unicode(_('Uploaded files')), unicode(_('Upload file')),
            name, unicode(_('Cancel Uploads')), name, name, input_code, js_code, images_code
        ))

    def value_from_datadict(self, data, files, name):
        cache_name = '%s_cache' % name

        if cache_name in data:
            value = [int(i) for i in data.getlist(cache_name)]
        else:
            value = []

        if name in files:
            value.append(files[name])

        return value

class SWFUploadField(ImageField):
    widget = SWFUploadWidget

    def clean(self, data, initial=None):
        """if isinstance(data, list):
            for i, im in enumerate(data):
                if isinstance(im, int):
                    continue

                data[i] = super(SWFUploadField, self).clean(im, initial)"""

        return data
