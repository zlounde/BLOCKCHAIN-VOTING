from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Candidate

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
# ===================================================================================================

class CandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['name', 'department', 'image']

# class SessionForm(forms.ModelForm):
#     class Meta:
#         model = Session
#         fields = ['title', 'start_time', 'end_time']

from django import forms
from .models import Candidate, ElectionTitle, Department

from django import forms
from .models import School, Department, ElectionTitle

class ElectionTitleForm(forms.ModelForm):
    class Meta:
        model = ElectionTitle
        fields = ['title', 'school', 'department']