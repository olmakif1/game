from __future__ import annotations

from django import forms


class ModeratorApplicationForm(forms.Form):
    display_name = forms.CharField(label="Display name", max_length=80)
    channel_handle = forms.CharField(label="Discord handle", max_length=64)
    timezone = forms.CharField(label="Timezone", max_length=48)
    contribution_focus = forms.ChoiceField(
        choices=[
            ("events", "Event coordination"),
            ("community", "Community support"),
            ("creative", "Creative/content"),
            ("tech", "Tech & automation"),
        ]
    )
    message = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}), label="Why do you want to help?")
