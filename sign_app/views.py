from __future__ import annotations

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView

from .forms import ModeratorApplicationForm


class ModeratorApplicationView(FormView):
    template_name = "sign/application.html"
    form_class = ModeratorApplicationForm
    success_url = reverse_lazy("sign:apply")

    def form_valid(self, form: ModeratorApplicationForm):  # type: ignore[override]
        messages.success(
            self.request,
            "Application received! We'll reach out via Discord once reviewed.",
        )
        return super().form_valid(form)
