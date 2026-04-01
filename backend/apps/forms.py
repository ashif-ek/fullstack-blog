from django import forms
from .models import User
from django.contrib.auth.hashers import make_password


class RegisterForm(forms.ModelForm):
    """
    Handles new user signup. Uses a ModelForm for direct User creation.
    Password is hashed here before saving to keep the database secure.
    """

    password = forms.CharField(
        widget=forms.PasswordInput,  # hides typed characters
        help_text="Enter a strong password"
    )

    class Meta:
        model = User
        fields = ['email', 'password']

    def save(self, commit=True):
        """
        Override save so the password never goes into the DB in plain text.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """
    Basic login form. Only collects raw credentials; it does not verify them here.
    The view handles authentication.
    """

    email = forms.EmailField(help_text="Enter your registered email")

    password = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Enter your password"
    )
