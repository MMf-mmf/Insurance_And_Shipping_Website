from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager
import uuid


class CustomUserManger(UserManager):
  pass

class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    rate_card_tier = models.PositiveIntegerField(null=False, blank=False, default=2)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    objects = CustomUserManger()
    def __str__(self):
        return self.email
      
      
class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    address = models.CharField(max_length=250, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    quickbooks_id = models.CharField(max_length=100, null=True, blank=True)
    quickbooks_email = models.CharField(max_length=100, null=True, blank=True)
    def __str__(self):
        return f'{self.user.email} Profile'
      
class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    email = models.EmailField(null=False, blank=False)
    message = models.TextField(null=False, blank=False)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return self.name + ' - ' + self.email




