from __future__ import annotations

from django import forms

from .models import Announcement


class AnnouncementForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        help_text="Comma separated tags",
        widget=forms.TextInput(attrs={"placeholder": "synthwave, livestream, merch"}),
    )

    class Meta:
        model = Announcement
        fields = [
            "title",
            "summary",
            "content",
            "category",
            "tags",
            "author_display",
            "is_pinned",
        ]
        widgets = {
            "summary": forms.Textarea(attrs={"rows": 3}),
            "content": forms.Textarea(attrs={"rows": 6}),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if self.instance.pk and isinstance(self.instance.tags, list):
            self.initial["tags"] = ", ".join(self.instance.tags)

    def clean_tags(self) -> list[str]:
        raw = self.cleaned_data.get("tags", "")
        if isinstance(raw, list):
            return raw
        return [tag.strip() for tag in raw.split(",") if tag.strip()]
