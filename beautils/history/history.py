from django.contrib.auth.models import User

from beautils.middleware import threadlocals
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import ADDITION, LogEntryManager
from django.contrib.admin.models import CHANGE
from django.contrib.admin.models import LogEntry
from django.db import models
from django.contrib.admin.models import DELETION
from django.db.models import signals
from django.db.models.base import ModelBase
from django.utils.datetime_safe import strftime
import datetime

SAVE_THROUGH_ADMIN = False
if not SAVE_THROUGH_ADMIN:
    LogEntryManager.log_action = lambda *args, **kwargs: None 

def prepare_fields(instance):
    output = {}
    class_fields = instance.__class__._meta.fields
    instance._history_fields = {}
    all = dict([(f.name, f) for f in class_fields])
    for field_name in instance._history['fields']:
        modelfield = all[field_name]
        value = getattr(instance, modelfield.attname)
        if value is None: value = ''
        output[field_name] = unicode(value)
    return output

def add_signals(cls):
    def post_delete(instance, **_kwargs):
        if instance._history.get('model'):
            instance._create_log_entry(DELETION)

    def pre_save(instance, **_kwargs):
        if instance._history.get('fields', []):
            if instance.pk is None:
                instance._history_fields = {}
                for field_name in instance._history['fields']:
                    instance._history_fields[field_name] = ''
            else:
                try:
                    db_instance = instance.__class__.objects.get(pk=instance.pk)
                except instance.__class__.DoesNotExist:
                    db_instance = instance
                instance._history_fields = prepare_fields(db_instance)
        if instance._history.get('model'):
            if instance.pk is None:
                instance._history_action = ADDITION
            else:
                instance._history_action = CHANGE
    
    def post_save(instance, **_kwargs):
        if not instance._history.get('model'):
            return
        
        log_entry = instance._create_log_entry(instance._history_action)

        if instance._history.get('fields', []):
            pre_fields = instance._history_fields 
            post_fields = prepare_fields(instance)
            for name, after in post_fields.iteritems():
                #print 'looking if', name, 'changed...'
                before = pre_fields[name] 
                if before != after:
                    # field has been changed
                    #print 'changed', name, 'from', before, 'to', after
                    instance._create_field_log_entry(name, after, log_entry)
            #print 'checking done.'
            
    signals.pre_save.connect(pre_save, sender=cls, weak=False)
    signals.post_save.connect(post_save, sender=cls, weak=False)
    signals.post_delete.connect(post_delete, sender=cls, weak=False)

class ModelWithHistoryBase(ModelBase):
    def __new__(cls, name, bases, attrs):
        Model = ModelBase.__new__(cls, name, bases, attrs)
        history = getattr(Model, 'History', None)
        if history:
            history = history.__dict__
            if not 'model' in history:
                history['model'] = False 
            if 'fields' in history:
                history['model'] = True
            else:
                history['fields'] = []
                
        else:
            #raise "Please add History subclass to your model"
            history = {
                'model': False,
                'fields': []
            }
        Model._history = history
        add_signals(Model)
        return Model

class ModelWithHistory(models.Model):
    __metaclass__ = ModelWithHistoryBase
    class Meta:
        abstract = True
        
    def _create_log_entry(self, action):
        if threadlocals.get_current_user() is None:
            return
            raise Exception("Please enable ThreadsLocal middleware")
        if threadlocals.get_current_user().is_anonymous():
            user = User.objects.get(pk=0) # feature: User with pk=0 supposed to be anonymous user
        else:
            user = threadlocals.get_current_user()
        if SAVE_THROUGH_ADMIN: 
            history = LogEntry.objects.get(user=user, object_id = self.pk, action_flag = action,
                            content_type = ContentType.objects.get_for_model(self)).latest()
        else:
            history = LogEntry(user=user, object_id = self.pk, action_flag = action,
                                content_type = ContentType.objects.get_for_model(self))
            try:
                history.object_repr = repr(self)
            except Exception:
                history.object_repr = "(unknown)"
            history.save()
        return history

    def _create_field_log_entry(self, name, value, log_entry):
        if threadlocals.get_current_user() is None:
            return
            raise Exception("Please enable ThreadsLocal middleware")
        if threadlocals.get_current_user().is_anonymous():
            user = User.objects.get(pk=0) # feature: User with pk=0 supposed to be anonymous user
        else:
            user = threadlocals.get_current_user()
        from models import AttributeLogEntry
        story = AttributeLogEntry(user=user, object_id = self.pk, field_name=name, log_entry = log_entry,
                            field_value = value, content_type = ContentType.objects.get_for_model(self))
        try:
            story.object_repr = repr(self)
        except Exception:
            story.object_repr = "(unknown)"
        story.save()

    def get_history(self):
        content_type = ContentType.objects.get_for_model(self)
        return LogEntry.objects.filter(object_id=self.pk, content_type=content_type)

    def has_history(self):
        return bool(self.__class__._history.get('model', False)) 
        
    def last_edited_at(self):
        story = list(self.get_history()[:1])
        if not story:
            return datetime.datetime(2000, 1, 1, 0, 0, 0)
        else:
            return strftime(story[0].action_time, "%Y-%m-%d %H:%M")
        
    def last_edited_by(self):
        history = list(self.get_history()[:1])
        if not history:
            return User.objects.get(pk=1)
        else:
            return history[0].user

    def editor_info(self, history):
        if history:
            date = strftime(history.action_time, "%b %d, %H:%M")
            user = history.user
        else:
            date = None
            user = None
        return date, user        

    def last_edited(self):
        history = list(self.get_history().order_by('-action_time')[:1])
        date, user = self.editor_info(history and history[0])
        if date or user:
            return "%s / %s" % (date, user)
        else:
            return "" 

    def first_edited(self):
        history = list(self.get_history().order_by('action_time')[:1])
        date, user = self.editor_info(history and history[0])
        if date or user:
            return "%s / %s" % (date, user)
        else:
            return "" 
