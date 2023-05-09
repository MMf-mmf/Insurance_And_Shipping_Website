from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Profile, Contact
# for admin site
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username',)
        
# for admin site        
class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ('email', 'username',)
        
#form for Profile model
class ProfileForm(forms.ModelForm):  
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'email', 'address', 'postal_code', 'city',)
        
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('name', 'email', 'message',)
