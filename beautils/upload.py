from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from traceback import print_exc
import os
import uuid
import PIL #@UnresolvedImport

class UploadError(Exception):
    pass

def image_upload(data, Model):
    if isinstance(data, UploadedFile):
        uploaded = data
    elif not data or not data.name:
        raise UploadError('"data" argument was broken.')
    else:
        from django.forms import ImageField, ValidationError

        try:
            uploaded = ImageField().clean(data)
        except ValidationError, e:
            raise UploadError(e)

    try:
        image = Model.objects.create_with_thumbnail(uploaded)
    except Exception, e:
        print_exc()
        raise UploadError('Unable to write image data to database.', e)

    return image

class ImageManager(models.Manager):
    IMAGE_REWRITE = False
    IMAGES_DIR = 'logos'
    THUMBNAILS_DIR = 'thumbs'
    THUMBNAIL_DIMENSIONS = (32, 32)

    def media_dir (self, subdir): 
        return os.path.join(settings.MEDIA_ROOT, subdir)

    def strip_media_dir (self, directory): 
        return directory.replace(settings.MEDIA_ROOT, '').lstrip('/')
    
    def get_new_filename(self, filename):
        d, nameext = os.path.split(filename)
        _name, ext = os.path.splitext(nameext)
        name = "img_" + uuid.uuid1 ().hex
        return os.path.join(d, name + ext)

    def create_with_thumbnail(self, filename, content=None, thumb_dimensions=None):
        if not isinstance(filename, UploadedFile) and not content:
            raise TypeError('Image "content" was not supplied. Thumb generating failed.')
        elif not content:
            content = filename.read () #content
            filename = filename.name
        elif isinstance(filename, UploadedFile):
            filename = filename.name

        images_dir = self.media_dir(self.IMAGES_DIR)
        thumbs_dir = self.media_dir(self.THUMBNAILS_DIR)

        if not os.path.isdir(images_dir): 
            os.mkdir(images_dir)

        if not os.path.isdir(thumbs_dir):
            os.mkdir(thumbs_dir)

        filename = self.get_new_filename (os.path.join(images_dir, filename))
        
        rewrite = self.IMAGE_REWRITE

        if not rewrite and os.path.isfile(filename):
            filename = self.get_new_filename(filename)

        f = open(filename, 'wb')
        try:
            f.write(content)
        finally:
            f.close()

        thumbnail = os.path.join(thumbs_dir, os.path.basename(filename))

        if thumb_dimensions is None:
            thumb_dimensions = self.THUMBNAIL_DIMENSIONS

        width, height = thumb_dimensions

        base, ext = os.path.splitext(thumbnail)
        thumbnail = '%s_%dx%d%s' % (base, width, height, ext)

        im = PIL.Image.open(filename)
        if im.mode not in ('L', 'RGB'):
            im = im.convert('RGB')
        im.thumbnail(thumb_dimensions, PIL.Image.ANTIALIAS)

        new_width, new_height = im.size

        if new_width == width and new_height == height:
            im.save(thumbnail, im.format)
        else:
            new_im = PIL.Image.new('RGB', (width, height), (255, 255, 255))
            new_im.paste(im, ((width - new_width) / 2, (height - new_height) / 2))
            new_im.save(thumbnail, im.format)

        return super(ImageManager, self).create(
            name=os.path.basename(filename),
            filename=self.strip_media_dir(filename), 
            thumbnail=self.strip_media_dir(thumbnail)
        )
