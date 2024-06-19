from django.urls import path

from . import views
urlpatterns = [
    path("tanimlar", views.create_page,name="tanimlar"),
    path("birim_olustur",views.create_unit,name="birim_olustur"),
]