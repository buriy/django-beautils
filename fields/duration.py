from widgets.duration import DurationField as FDurationField
from widgets.duration import TimeDelta
from django.db.models.fields import Field
from django.core.exceptions import ValidationError
from django.db import connection

class DurationProxy(object):
    def __init__(self, field):
        self.field_name = field.name

    def __get__(self, instance=None, owner=None):
        if instance is None:
            raise AttributeError, "%s can only be accessed from %s instances." % (self.field_name, owner.__name__)
        if self.field_name not in instance.__dict__:
            return None
        return instance.__dict__[self.field_name]

    def __set__(self, instance, value):
        if value and not isinstance(value, TimeDelta):
            value = TimeDelta(value=value)
        instance.__dict__[self.field_name] = value

class DurationField(Field):
    def __init__(self, *args, **kwargs):
        super(DurationField, self).__init__(*args, **kwargs)
        self.max_digits, self.decimal_places = 20, 6

    def get_internal_type(self):
        return "DecimalField"

    def contribute_to_class(self, cls, name):
        super(DurationField, self).contribute_to_class(cls, name)
        setattr(cls, name, DurationProxy(self))

    def get_db_prep_save(self, value):
        if value is None:
            return None
        if not isinstance(value, TimeDelta):
            value = TimeDelta(value=value)
        # max value 86,399,999,999,999,999,999 microseconds
        # that is 1,000,000,000 days, a bit more than 2,739,000 years
        return connection.ops.value_to_db_decimal(value.to_microseconds(), 20, 0)

    def to_python(self, value):
        if isinstance(value, TimeDelta):
            return value
        try:
            return TimeDelta(value=float(value))
        except TypeError:
            raise ValidationError('The value must be an integer.')
        except OverflowError:
            raise ValidationError('The maximum allowed value is %s' % TimeDelta.max)

    def formfield(self, form_class=FDurationField, **kwargs):
        return super(DurationField, self).formfield(form_class, **kwargs)
