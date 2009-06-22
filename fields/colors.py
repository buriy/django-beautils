from django.db.models.fields import CharField
from widgets.colorpicker import ColorPickerField

class ColorField(CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        super(ColorField, self).__init__(*args, **kwargs)
    
    def formfield(self, **kwargs):
        defaults = {
            'max_length': self.max_length, 
            'form_class': ColorPickerField
        }
        defaults.update(kwargs)
        return super(CharField, self).formfield(**defaults)
