from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

class UserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, staff_id=None, boy_id=None, **kwargs):

        try:
            # Staff login
            if staff_id:
                user = CustomUser.objects.get(
                    staff_id=staff_id,
                    username=username,
                    is_staff_user=True
                )

            # Boy login
            elif boy_id:
                user = CustomUser.objects.get(
                    boy_id=boy_id,
                    username=username,
                    is_boy_user=True
                )
            else:
                return None

        except CustomUser.DoesNotExist:
            return None

        # Check password
        if user.check_password(password):
            return user

        return None
