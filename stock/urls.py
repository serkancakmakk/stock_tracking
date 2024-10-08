from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.urls import path
urlpatterns = [
    path('', views.user_login, name='login'),
    path('login/', views.user_login, name='login'),
    path("dashboard/<int:code>", views.dashboard,name="dashboard"),
    # path("<int:code>", views.dashboard,name="dashboard"),
    # path("tanimlar/", views.create_page,name="tanimlar"),
    path("cari_tanimla/<int:code>", views.create_seller,name="cari_tanimla"),
    # path("cari_durum_degistir/<int:code>/<int:seller_id>",views.change_seller_status,name="cari_durum_degistir"),
    path("kategori_tanimla/<int:code>", views.create_category_page,name="kategori_tanimla"),
    path("kategori_durum_degistir/<int:code>/<int:id>/", views.change_category_status,name="kategori_durum_degistir"),
    path("urun_tanimla/<int:code>", views.create_product,name="urun_tanimla"),
    path("cikis_tanimlama_sayfasi/<int:code>", views.create_outgoing_reasons_page,name="cikis_tanimlama_sayfasi"),
    # path('cikis_sebebini_degistir/<int:id>/', views.change_active_status, name='cikis_sebebini_degistir'),
    path("birim_olustur/<int:code>",views.create_unit_page,name="birim_olustur"),
    path("birim_tanimla/<int:code>",views.create_unit,name="birim_tanimla"),
    path("birim_sil/<int:unit_id>/<int:code>",views.delete_unit,name="birim_sil"),
    
    path("urun_olustur/<int:code>",views.product_add_page,name="urun_olustur"),
    path("urun_olusturma_sayfasi/",views.product_add_page,name="urun_olusturma_sayfasi"),
    path("urun_sil/<int:company_code>/<int:product_id>",views.delete_product,name="urun_sil"),
    path("kategori_olustur/<int:code>",views.create_category,name="kategori_olustur"),
    path("cikis_nedeni_olustur/<int:code>",views.create_outgoing_reasons,name="cikis_nedeni_olustur"),
    # faturalar
    path("fatura_gir/<int:code>",views.add_bill,name="fatura_olustur"),
    path("faturalar/<int:code>/",views.bills,name="faturalar"),
    path('fatura_detay/<str:bill_number>/<int:company_code>/', views.bill_details, name='fatura_detay'),
    path('outgoing_bill_details/<str:bill_number>/<int:company_code>/', views.outgoing_bill_details, name='outgoing_bill_details'),
    # faturalar
    path('kalem_ekle/<int:bill_id>',views.add_billitem,name="kalem_ekle"),
    path('stok_durumu/<int:code>/',views.stock_status,name="stok_durumu"),
    path('stok_cikisi_yap/<int:code>',views.process_stock_outgoing,name="stok_cikisi_yap"),
    path('stok_giris_cikislari/<int:code>/',views.incoming_outgoing_reports,name="stok_giris_cikislari"),
    path('kategoriye_göre_stoklar/<int:code>/',views.stock_by_category,name="kategoriye_göre_stoklar"),
    path('birimi_guncelle/<int:company_code>/<int:unit_id>/', views.update_unit, name='birimi_guncelle'),
    # stok raportları
    path('kritik_stok_raporu/<int:company_code>', views.critical_stock_level, name='kritik_stok_raporu'),
    path('stok_hareketleri/<int:code>', views.stock_transactions, name='stok_hareketleri'),
    path('ürün_bilgileri/<int:code>/', views.product_info, name='ürün_bilgileri'),
    path('vade_tarihi_gelen_faturalar/<int:code>/<str:expiry_date>/', views.due_date_reports, name='vade_tarihi_gelen_faturalar'),
    path('delete_bill/<str:bill_number>/<int:company_code>', views.delete_bill, name='delete_bill'),
    path('silinen_faturalar/', views.deleted_bills, name='silinen_faturalar'),
    path('stok_farki/<int:code>', views.stock_difference_report, name='stok_farki'),
    path('satici_sayfasi/<int:id>/<int:code>',views.seller_detail,name="satici_sayfasi"),
    path('ödeme_yap/<int:id>/<int:company_code>',views.payment,name="ödeme_yap"),
    path('cikis_faturalari/<int:company_code>',views.outgoing_bills,name="cikis_faturalari"),
    path('yeni_firma_tanimla/<int:code>/', views.create_company, name='yeni_firma_tanimla'),
    path('firmalar/<int:company_code>',views.companies,name="firmalar"),
    path('kullanici_ekle/<int:code>',views.register,name="kullanici_ekle"),
    path('parametre/<int:code>', views.parameter, name="parametre"),
    path('parametre_degistir/<int:company_code>/', views.edit_parameter, name='parametre_degistir'),
    path('logout', views.logout, name='logout'),
    # path('master', views.master_create_company, name='master'),
    path('düsük_stok_uyarısı/<int:code>', views.low_stock_reports, name='düsük_stok_uyarısı'),
    path('envanter/<int:code>', views.inventory, name='envanter'),
    path('kullanilan_envanterler/<int:company_code>',views.issued_inventories,name='kullanilan_envanterler'),
    path('get_inventory_products/', views.get_inventory_products, name='get_inventory_products'),
    path('envanter_cikis/<int:code>', views.outgoing_inventory, name='envanter_cikis'),
    path('kullanici_detayi/<int:code>/<uuid:uuid4>/', views.user_detail, name='kullanici_detayi'),
    path('kullanici_guncelle/<int:code>/<uuid:uuid4>/', views.user_edit, name='kullanici_guncelle'),
    path('kullanici_yetkilendir/<int:code>/<uuid:uuid4>/',views.edit_permissions,name="kullanici_yetkilendir"),
    # path('destek_odasi/<int:code>',views.get_support,name="destek_odasi"),
    path('destek/<str:code>/', views.destek_view, name='destek'),
    path('chat/<str:room_name>/<str:code>/', views.room, name='room'),
    path('give_support/', views.give_support, name='give_support'),
    path('end_chat/<str:room_name>',views.end_chat,name='desteği_bitir'),
    path('destek_odalari/<int:code>',views.check_chat_room,name="destek_odalari"),
    path('oda_detay/<str:room_name>/<int:code>',views.room_detail,name="oda_detay"),
    path('set-notifications/', views.set_notifications, name='set_notifications'),
    path('silinen_ögeler/<int:company_code>', views.deleted_items, name='silinen_ögeler'),
    path('cikis_nedenini_sil/<int:code>/<int:reason_id>',views.delete_outgoing_reason,name="cikis_nedenini_sil"),
    path('cikis_nedenini_güncelle/<int:code>/<int:reason_id>',views.update_outgoing_reason,name="cikis_nedenini_güncelle"),
    
    path('kategori-guncelle/<int:company_code>/<int:category_id>/', views.kategori_guncelle, name='kategori_guncelle'),
    # - # - # - # - # - # - # - # - # - # - # - # - # - #
    # Seller (Cari) related paths
    path("cariler/yeni/<int:code>/", views.create_seller, name="cari_olustur"),  # Create seller
    path("cariler/guncelle/<int:company_code>/<int:seller_id>/", views.update_seller, name="cari_guncelle"),  # Update seller
    path("cariler/sil/<int:company_code>/<int:seller_id>/", views.delete_seller, name="cari_sil"),  # Delete seller

    # - # - # - # - # - # - # - # - # - # - # - # - # - # 
    # path('check-notifications/', views.check_notification_preference, name='check_notifications'),
    # path('calculate_average_cost/', views.calculate_average_cost_view, name='calculate_average_cost'),
    path('delete-item/', views.delete_item, name='delete_item'),
    path('update_product/<int:company_code>/<int:product_id>/', views.update_product, name='update_product'),
    path('check-product-name/', views.check_product_name, name='check_product_name'),
    path('fatura_ödemesi/<int:bill_id>/<int:company_code>',views.toggle_bill_payment_status,name="fatura_ödemesi"),
    path("şirket_durumunu_değiştir/<int:company_code>", views.set_company_status, name="şirket_durumunu_degistir"),
    # Hata Bildir
    # Hata Bildirimi Oluştur
    path("hatalar/", views.report_bug, name="hata_bildir"),  # POST: Yeni bir hata bildirimi oluşturur
    # Hata Bildirimleri Listele
    path("hatalar/<int:company_code>/", views.report_bugs_page, name="hata_bildirimleri"),  # GET: Belirli bir şirket koduna ait hata bildirimlerini listeler
    # Hata Durumunu Güncelle
    path("hatalar/<int:id>/status/", views.read_unread_bug, name="hata_durumunu_degistir"),  # PUT: Belirli bir hata bildirimini günceller
    # Hata Sil
    path("hatalar/<int:id>/", views.delete_bug, name="hata_sil"),  # DELETE: Belirli bir hata bildirimini siler
    path("sifre_degistir/<uuid:uuid>/",views.change_password,name="sifre_degistir")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)