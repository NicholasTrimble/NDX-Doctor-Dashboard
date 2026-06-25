from django import forms
from django.contrib.auth.models import User

class CorporateSignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()

        try:
            domain = email.split('@')[1]
        except IndexError:
            raise forms.ValidationError("Please enter a valid email address")
        
        if domain != "nationaldentex.com":
            raise forms.ValidationError("Access Denied. This site is only for individuals part of the National Dentex Association.")
        
        if User.objects.filter(email = email).exists():
            raise forms.ValidationError("A user with this email already currently exists")
        
        return email