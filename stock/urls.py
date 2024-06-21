from django.urls import path

from . import views
urlpatterns = [
    path("", views.create_page,name="tanimlar"),
    path("tanimlar/", views.create_page,name="tanimlar"),
    path("birim_olustur",views.create_unit,name="birim_olustur"),
    path("birim_sil/<int:unit_id>/",views.delete_unit,name="birim_sil"),
    path("cari_olustur/",views.create_seller,name="cari_olustur"),
    path("urun_olustur/",views.create_product,name="urun_olustur"),
    path("kategori_olustur/",views.create_category,name="kategori_olustur"),
    path("fatura_gir/",views.add_bill,name="fatura_olustur"),
]