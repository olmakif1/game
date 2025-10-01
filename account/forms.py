from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class FanSignupForm(UserCreationForm):
    display_name = forms.CharField(max_length=80, help_text="This name appears on moderator posts.")
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "display_name", "email")

    def save(self, commit: bool = True) -> User:
        user: User = super().save(commit=False)
        user.first_name = self.cleaned_data.get("display_name", "")
        user.email = self.cleaned_data.get("email", "")
        if commit:
            user.save()
        return user
