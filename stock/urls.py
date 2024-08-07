from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.urls import path, re_path
urlpatterns = [
    path('login/', views.user_login, name='login'),
    path("dashboard/<int:code>", views.dashboard,name="dashboard"),
    # path("<int:code>", views.dashboard,name="dashboard"),
    # path("tanimlar/", views.create_page,name="tanimlar"),
    path("cari_tanimla/<int:code>", views.create_seller,name="cari_tanimla"),
    path("kategori_tanimla/<int:code>", views.create_category_page,name="kategori_tanimla"),
    path("kategori_durum_degistir/<int:id>", views.change_category_status,name="kategori_durum_degistir"),
    path("urun_tanimla/<int:code>", views.create_product,name="urun_tanimla"),
    path("cikis_tanimlama_sayfasi/<int:code>", views.create_outgoing_reasons_page,name="cikis_tanimlama_sayfasi"),
    path('cikis_sebebini_degistir/<int:id>/', views.change_active_status, name='cikis_sebebini_degistir'),
    path("birim_olustur/<int:code>",views.create_unit_page,name="birim_olustur"),
    path("birim_tanimla/<int:code>",views.create_unit,name="birim_tanimla"),
    path("birim_sil/<int:unit_id>/",views.delete_unit,name="birim_sil"),
    path("cari_olustur/<int:code>",views.create_seller,name="cari_olustur"),
    path("urun_olustur/<int:code>",views.product_add_page,name="urun_olustur"),
    path("urun_olusturma_sayfasi/",views.product_add_page,name="urun_olusturma_sayfasi"),
    path("kategori_olustur/<int:code>",views.create_category,name="kategori_olustur"),
    path("cikis_nedeni_olustur/<int:code>",views.create_outgoing_reasons,name="cikis_nedeni_olustur"),
    path("fatura_gir/<int:code>",views.add_bill,name="fatura_olustur"),
    path("faturalar/<int:code>",views.bills,name="faturalar"),
    path('fatura_detay/<str:bill_number>', views.bill_details, name='fatura_detay'),
    path('kalem_ekle/<int:bill_id>',views.add_billitem,name="kalem_ekle"),
    path('stok_durumu/<int:code>/',views.stock_status,name="stok_durumu"),
    path('stok_cikisi_yap/<int:code>',views.process_stock_outgoing,name="stok_cikisi_yap"),
    path('stok_giris_cikislari/<int:code>/',views.incoming_outgoing_reports,name="stok_giris_cikislari"),
    path('kategoriye_göre_stoklar/<int:code>/',views.stock_by_category,name="kategoriye_göre_stoklar"),
    path('import_excel/', views.import_excel, name='import_excel'),
    path('download_excel/', views.download_excel, name='download_excel'),
    path('birim_durumunu_degistir/<int:unit_id>', views.change_unit_status, name='birim_durumunu_degistir'),
    path('stok_hareketleri/<int:code>', views.stock_transactions, name='stok_hareketleri'),
    path('ürün_bilgileri/<int:code>/', views.product_info, name='ürün_bilgileri'),
    path('vade_tarihi_gelen_faturalar/<int:code>/<str:expiry_date>/', views.due_date_reports, name='vade_tarihi_gelen_faturalar'),
    path('fatura_ödemesini_geri_al/<int:id>', views.unpaid_bill, name='fatura_ödemesini_geri_al'),
    path('delete_bill/<int:bill_id>/', views.delete_bill, name='delete_bill'),
    path('silinen_faturalar/', views.deleted_bills, name='silinen_faturalar'),
    path('stok_farki/<int:code>', views.stock_difference_report, name='stok_farki'),
    path('satici_sayfasi/<int:id>/<int:code>',views.seller_detail,name="satici_sayfasi"),
    path('ödeme_yap/<int:id>',views.payment,name="ödeme_yap"),
    path('cikis_faturalari',views.outgoing_bills,name="cikis_faturalari"),
    path('yeni_firma_tanimla/<int:code>/', views.create_company, name='yeni_firma_tanimla'),
    path('firmalar/<int:company_code>',views.companies,name="firmalar"),
    path('kullanici_ekle/<int:code>',views.register,name="kullanici_ekle"),
    path('parametre/<int:code>', views.parameter, name="parametre"),
    path('parametre_degistir/<int:company_code>/', views.edit_parameter, name='parametre_degistir'),
    path('logout', views.logout, name='logout'),
    # path('calculate_average_cost/', views.calculate_average_cost_view, name='calculate_average_cost'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)