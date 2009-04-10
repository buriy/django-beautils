from django.core.files.uploadedfile import UploadedFile
from utils.upload import image_upload, UploadError
from django.forms.util import ValidationError

from django.utils.translation import ugettext as _

def clean_image_field(image, cache, ImageModel):
    if image and isinstance (image, list) and isinstance (image[0], list): #jsupload?
        cache = []
        for i in image[0]:
            if isinstance (cache, list):
                cache.append (i)
        return

    for i in image:
        if isinstance(i, UploadedFile):
            try:
                image = image_upload(i, ImageModel)
            except UploadError:
                raise ValidationError(_('Unable to upload image to the site.'))

            if cache is None:
                cache = image
            else:
                cache.add(image)
        elif not cache is None and not isinstance(cache, list):
            try:
                im = cache.get(pk=i)
                continue
            except:
                pass

            try:
                im = ImageModel.objects.select_related().get(pk=i)
            except ImageModel.DoesNotExist:
                pass

            cache.add(im)
        else:
            if cache is None:
                cache = []

            cache.append(i)
    return cache
