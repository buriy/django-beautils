from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.contrib.admin.util import quote
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _
from django.utils.datetime_safe import strftime
from django.contrib.admin.models import LogEntry

class AttributeLogEntry(models.Model):
    class Meta:
        verbose_name = _('attribute log entry')
        verbose_name_plural = _('attribute log entries')
        db_table = 'django_attribute_log'
        #db_table = 'common_attribute_log'
        ordering = ('-action_time',)
        app_label = 'admin'

    action_time = models.DateTimeField(_('action time'), auto_now=True)
    user = models.ForeignKey(User)
    content_type = models.ForeignKey(ContentType, blank=True, null=True)
    log_entry = models.ForeignKey(LogEntry, related_name = 'attribute_changes')
    object_id = models.IntegerField(_('object id'), blank=True, null=True)
    field_name = models.CharField(_('field name'), max_length=200, blank=True, null=True)
    field_value = models.TextField(_('field value'), null=True, blank=True)
    
    def __repr__(self):
        return smart_unicode(self.action_time)

    @staticmethod
    def get_history(obj, field):
        content_type = ContentType.objects.get_for_model(obj)
        return AttributeLogEntry.objects.filter(object_id=obj.pk, field_name=field, content_type=content_type)

    def get_edited_object(self):
        "Returns the edited object represented by this log entry"
        return self.content_type.get_object_for_this_type(pk=self.object_id)

    def get_admin_url(self):
        """
        Returns the admin URL to edit the object represented by this log entry.
        This is relative to the Django admin index page.
        """
        return mark_safe(u"%s/%s/%s/" % (self.content_type.app_label, self.content_type.model, quote(self.object_id)))

    @staticmethod
    def last_edited_at(obj, field):
        history = list(AttributeLogEntry.get_history(obj, field)[:1])
        if not history:
            return None
        else:
            return strftime(history[0].action_time, "%Y-%m-%d %H:%M")
        
    @staticmethod
    def last_edited_by(obj, field):
        history = list(AttributeLogEntry.get_history(obj, field)[:1])
        if not history:
            return None
        else:
            return history[0].user
