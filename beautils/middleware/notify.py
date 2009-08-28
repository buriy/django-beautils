DEFAULT_TYPE = 'information'

class NotificationMiddleware:
    def process_request(self, request):
        request.__class__.notifications = Notifications(request.session)
        return None

class Notifications:
    def __init__(self, session):
        self.session = session
        self.SESSION_VARIABLE = '_notifications'

    def get(self):
            return self.session.get(self.SESSION_VARIABLE, [])
    
    def get_and_clear(self):
            return self.session.pop(self.SESSION_VARIABLE, [])
    
    def create(self, message, type=DEFAULT_TYPE):
        """creates a notification
        
        arguments:
        message: text content of notification
        type: optional type (defaults to the value of DEFAULT_TYPE)
        """
        notifications = self.session.get(self.SESSION_VARIABLE)
        if notifications is None:
            notifications = []
            self.session[self.SESSION_VARIABLE] = notifications
        notifications.append({'content': message, 'type': type})
        self.session.modified = True
