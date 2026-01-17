from __future__ import annotations

import logging

from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView

logger = logging.getLogger("core")


class LoginView(FormView):
    template_name = "core/login.html"
    form_class = AuthenticationForm
    success_url = reverse_lazy("core:dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form: AuthenticationForm):
        user = form.get_user()
        login(self.request, user)
        logger.info("Пользователь %s вошел в систему", user.username)
        return super().form_valid(form)


class LogoutView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            username = request.user.username
            logout(request)
            logger.info("Пользователь %s вышел из системы", username)
        return redirect("core:login")


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "core/dashboard.html"
    login_url = reverse_lazy("core:login")
