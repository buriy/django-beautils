from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.forms.fields import email_re

class EmailBackend(ModelBackend):
    def authenticate(self, username = None, password = None):
        if email_re.search(username):
            try:
                user = User.objects.get(email = username)
                if user.check_password(password):
                    return user
            except User.DoesNotExist:
                return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk = user_id)
        except User.DoesNotExist:
            return None
