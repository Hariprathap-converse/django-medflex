from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User


class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)  # Find user by email
            if user.check_password(password):  # Check if password is correct
                return user
        except User.DoesNotExist:
            return None
