from django.urls import path

from . import views
urlpatterns = [
    path("", views.create_page,name="tanimlar"),
    path("tanimlar/", views.create_page,name="tanimlar"),
    path("cari_tanimla/", views.create_seller,name="cari_tanimla"),
    path("kategori_tanimla/", views.create_category,name="kategori_tanimla"),
    path("urun_tanimla/", views.create_product,name="urun_tanimla"),
    path("cikis_tanimlama_sayfasi/", views.create_outgoing_reasons_page,name="cikis_tanimlama_sayfasi"),
    path('cikis_sebebini_degistir/<int:id>/', views.change_active_status, name='cikis_sebebini_degistir'),
    path("birim_olustur",views.create_unit,name="birim_olustur"),
    path("birim_sil/<int:unit_id>/",views.delete_unit,name="birim_sil"),
    path("cari_olustur/",views.create_seller,name="cari_olustur"),
    path("urun_olustur/",views.product_add_page,name="urun_olustur"),
    path("urun_olusturma_sayfasi/",views.product_add_page,name="urun_olusturma_sayfasi"),
    path("kategori_olustur/",views.create_category,name="kategori_olustur"),
    path("cikis_nedeni_olustur/",views.create_outgoing_reasons,name="cikis_nedeni_olustur"),
    path("fatura_gir/",views.add_bill,name="fatura_olustur"),
    path("faturalar/",views.bills,name="faturalar"),
    path('fatura_detay/<str:bill_number>', views.bill_details, name='fatura_detay'),
    path('kalem_ekle/<int:bill_id>',views.add_billitem,name="kalem_ekle"),
    path('stok_durumu/',views.stock_status,name="stok_durumu"),
    path('stok_cikisi_yap/',views.process_stock_outgoing,name="stok_cikisi_yap"),
    path('stok_giris_cikislari',views.incoming_outgoing_reports,name="stok_giris_cikislari"),

]