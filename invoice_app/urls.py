from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("process/", views.process_invoice, name="process_invoice"),
path(
    "refresh/", views.refresh_invoice, name="refresh_invoice"),
]