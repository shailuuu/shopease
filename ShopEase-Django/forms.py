from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Address

class RegisterForm(UserCreationForm):
    full_name = forms.CharField(max_length=150)
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ('full_name', 'username', 'email', 'password1', 'password2')
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email__iexact=email).exists(): raise forms.ValidationError('An account with this email already exists.')
        return email
    def save(self, commit=True):
        user = super().save(commit=False); user.email = self.cleaned_data['email']; user.first_name = self.cleaned_data['full_name']
        if commit: user.save()
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Username or email')
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User; fields = ('first_name', 'last_name', 'email')

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('name', 'email', 'mobile', 'address', 'city', 'state', 'pincode')
        widgets = {'address': forms.Textarea(attrs={'rows': 3})}
