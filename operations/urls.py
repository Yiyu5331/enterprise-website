from django.urls import path

from . import views

app_name = "operations"

urlpatterns = [
    path("two-factor/setup/", views.two_factor_setup, name="two-factor-setup"),
    path("two-factor/verify/", views.two_factor_verify, name="two-factor-verify"),
]
