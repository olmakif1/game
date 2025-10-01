from __future__ import annotations

from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import FanSignupForm


class FanSignupView(CreateView):
    template_name = "account/signup.html"
    form_class = FanSignupForm
    success_url = reverse_lazy("login")

    def form_valid(self, form: FanSignupForm):  # type: ignore[override]
        response = super().form_valid(form)
        messages.success(self.request, "Crew access requested. You can now log in and join the broadcast team.")
        return response
