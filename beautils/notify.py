from django.utils.encoding import StrAndUnicode

DEFAULT_TYPE = 'information'

def notifications(request):
    """
    Returns notifications for the session and the current user.

    Note that this processor is only useful to use explicity if you are not
    using the (enabled by default) auth processor, as it also provides the
    notifications (by calling this method).

    The notifications are lazy loaded, so no notifications are retreived and deleted
    unless requested from the template.

    Both contrib.session and contrib.auth are optional. If neither is provided,
    no 'notifications' variable will be added to the context.
    """
    if hasattr(request, 'session') or hasattr(request, 'user'):
        return {'notifications': LazyNotifications(request)}
    return {}

class LazyNotifications(StrAndUnicode):
    """
    A lazy proxy for session and authentication notifications.
    """
    def __init__(self, request):
        self.request = request

    def __iter__(self):
        return iter(self.notifications)

    def __len__(self):
        return len(self.notifications)

    def __nonzero__(self):
        return bool(self.notifications)

    def __unicode__(self):
        return unicode(self.notifications)

    def __getitem__(self, *args, **kwargs):
        return self.notifications.__getitem__(*args, **kwargs)

    def _get_notifications(self):
        if hasattr(self, '_notifications'):
            return self._notifications

        # First, retreive any notifications for the user.
        if hasattr(self.request, 'user') and \
           hasattr(self.request.user, 'get_and_delete_messages'):
            self._notifications = [{'content': message, 'type': DEFAULT_TYPE} for
                message in self.request.user.get_and_delete_messages()]
        else:
            self._notifications = []

        # Next, retrieve any notifications for the session.
        if hasattr(self.request, 'session'):
            self._notifications += self.request.notifications.get_and_clear()
        return self._notifications
    notifications = property(_get_notifications)
