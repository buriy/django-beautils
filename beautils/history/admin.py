#save as useradmin.py
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.admin.options import ModelAdmin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape
from models import AttributeLogEntry
from superadmin.html import link

class LogEntryAdmin(ModelAdmin):
    list_display = ['user', 'action_time', 'edited_object', 'change_message']
    list_filter = ['user', 'action_time', 'content_type']
    raw_id_fields = ['user']
    pass

def logentry_edited_object(self):
    root = reverse(admin.site.root, args=[''])
    return mark_safe(link(root+self.get_admin_url(), escape(self.object_repr)))
logentry_edited_object.allow_tags = True
LogEntry.edited_object = logentry_edited_object

admin.site.register(LogEntry, LogEntryAdmin)

class AttributeLogEntryAdmin(ModelAdmin):
    list_display = ['user', 'action_time', 'edited_object', 'content_type', 'field_name', 'field_value_short']
    list_filter = ['user', 'action_time', 'content_type']
    raw_id_fields = ['user']

    def field_value_short(self, instance):
        l = len(instance.field_value)
        if l > 495:
            return instance.field_value[:490]+' ...'
        else:
            return instance.field_name

def attrlogentry_edited_object(self):
    root = reverse(admin.site.root, args=[''])
    geo = self.get_edited_object()
    return mark_safe(link(root+self.get_admin_url(), geo))
attrlogentry_edited_object.allow_tags = True
AttributeLogEntry.edited_object = attrlogentry_edited_object

admin.site.register(AttributeLogEntry, AttributeLogEntryAdmin)