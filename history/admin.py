#save as useradmin.py
from common.models import AttributeLogEntry
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.admin.options import ModelAdmin
from django.contrib.auth.models import Group, User
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.html import escape
from utils.html import link

def roles(self):
    #short_name = unicode # function to get group name
    short_name = lambda x:unicode(x)[:1].upper() # first letter of a group
    p = sorted(["<a title='%s'>%s</a>" % (x, short_name(x)) for x in self.groups.all()])
    if self.user_permissions.count(): p += ['+']
    value = ', '.join(p)
    return mark_safe("<nobr>%s</nobr>" % value)
roles.allow_tags = True
roles.short_description = 'roles'

def last(self):
    fmt = "%b %d, %H:%M"
    #fmt = "%Y %b %d, %H:%M:%S"
    value = self.last_login.strftime(fmt)
    return mark_safe("<nobr>%s</nobr>" % value)
last.allow_tags = True
last.admin_order_field = 'last_login'
last.short_description = 'last login'

def adm(self):
    return self.is_superuser
adm.boolean = True
adm.admin_order_field = 'is_superuser'

def staff(self):
    return self.is_staff
staff.boolean = True
staff.admin_order_field = 'is_staff'

User.roles = roles
User.last = last
User.adm = adm
User.staff = staff

UserAdmin = admin.site._registry[User]
UserAdmin.list_display = ['username', 'email', 'first_name', 'last_name'] \
                       + ['is_active', 'staff', 'adm', 'roles', 'last']

#use last few lines only when you have not very much users in each group
def persons(self):
    return ", ".join([x.username for x in self.user_set.all()])

Group.persons = persons

GroupAdmin = admin.site._registry[Group]
GroupAdmin.list_display = ['name', 'persons']

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