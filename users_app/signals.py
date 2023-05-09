from .models import Profile
from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from payments_app.models import AccountCredit

@receiver(user_signed_up)
def add_profile_to_user(request, user, **kwargs):
    print('user_signed_up signal received')
    Profile.objects.create(user=user)
    AccountCredit.objects.create(user=user)
    