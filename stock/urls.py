from django.urls import path

from . import views
urlpatterns = [
    path("tanimlar", views.create_page,name="tanimlar"),
]