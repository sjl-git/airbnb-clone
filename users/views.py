from django.contrib.auth import authenticate, login, logout
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect, reverse
from django.views.generic import View, FormView, DetailView, UpdateView
from django.contrib.auth.views import PasswordChangeView
from . import forms, models, mixins


class LoginView(mixins.LoggedOutOnlyView, FormView):

    template_name = "users/login.html"
    # success_url = reverse_lazy("core:home")
    form_class = forms.LoginForm

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        return super().form_valid(form)

    def get_success_url(self):
        next_arg = self.request.GET.get("next")
        if next_arg is not None:
            return next_arg
        else:
            return reverse("core:home")


def log_out(request):
    logout(request)
    return redirect(reverse("core:home"))


class SignUpView(FormView):
    template_name = "users/signup.html"
    success_url = reverse_lazy("core:home")
    form_class = forms.SignUpForm

    def form_valid(self, form):
        form.save()
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(self.request, username=email, password=password)
        if user is not None:
            login(self.request, user)
        user.verify_email()
        return super().form_valid(form)


def complete_verification(request, key):
    try:
        user = models.User.objects.get(email_secret=key)
        user.email_verified = True
        user.email_secret = ""
        user.save()
    except models.User.DoesNotExist:
        pass
    return redirect(reverse("core:home"))


class UserProfileView(DetailView):
    model = models.User
    context_object_name = "user_obj"


class UpdateProfileView(mixins.LoggedInOnlyView, UpdateView):
    model = models.User
    template_name = "users/update-profile.html"
    fields = (
        "first_name",
        "last_name",
        "avatar",
        "gender",
        "bio",
        "birthdate",
        "language",
        "currency",
    )

    def get_object(self, queryset=None):
        return self.request.user

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["first_name"].widget.attrs = {"placeholder": "first_name"}
        form.fields["last_name"].widget.attrs = {"placeholder": "last_name"}
        form.fields["avatar"].widget.attrs = {"placeholder": "avatar"}
        form.fields["gender"].widget.attrs = {"placeholder": "gender"}
        form.fields["bio"].widget.attrs = {"placeholder": "bio"}
        form.fields["birthdate"].widget.attrs = {"placeholder": "birthdate"}
        form.fields["language"].widget.attrs = {"placeholder": "language"}
        form.fields["currency"].widget.attrs = {"placeholder": "currency"}

        return form


class ChangePasswordView(mixins.LoggedInOnlyView, PasswordChangeView):
    template_name = "users/update-password.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        form.fields["old_password"].widget.attrs = {"placeholder": "old password"}
        form.fields["new_password1"].widget.attrs = {"placeholder": "new password"}
        form.fields["new_password2"].widget.attrs = {
            "placeholder": "new password confirmation"
        }
        return form

    def get_success_url(self):
        return self.request.user.get_absolute_url()
