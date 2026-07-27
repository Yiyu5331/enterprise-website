from django.urls import path

from .api import contacts, deprecated_alias, inquiries

app_name = "main"

urlpatterns = [
    path("inquiries/", deprecated_alias(inquiries), name="create-inquiry"),
    path("contacts/", deprecated_alias(contacts), name="create-contact"),
]
