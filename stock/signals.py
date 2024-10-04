# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from django.db import transaction
# from django.db.models import Sum, F
# from decimal import Decimal
# from .models import BillItem, ChatRoom, Parameter, Product, Seller, User
# from django.db import transaction
# from django.db.models import Sum, F, DecimalField, ExpressionWrapper
# from decimal import Decimal
# from .models import BillItem, Product, Company
# import os
# from django.core.files.storage import default_storage


# @receiver(post_save, sender=User)
# # def create_directory_for_uploaded_files(sender, instance, **kwargs):
# #     if instance.image:
# #         # Get the directory where the file will be uploaded
# #         directory = os.path.dirname(instance.image.name)
# #         # Create the directory if it does not exist
# #         if not default_storage.exists(directory):
# #             default_storage.makedirs(directory)
# @receiver(post_save, sender=BillItem)
# def update_product_average_cost(sender, instance, created, **kwargs):
#     if created:
#         try:
#             with transaction.atomic():
#                 # Ürünü al
#                 product = instance.product
#                 company = product.company

#                 # Şirketin parametrelerini al
#                 parameter = Parameter.objects.get(company=company)
#                 # FIFO, LIFO, or average cost, etc.
#                 stock_issue_method = parameter.cost_calculation
#                 print('Stok Hesaplama Parametresi', stock_issue_method)
#                 if stock_issue_method == 'fifo':
#                     # FIFO maliyet hesaplama mantığı
#                     bill_items = BillItem.objects.filter(
#                         product=product, is_delete=False).order_by('bill__date')

#                     # FIFO hesaplamaya başla
#                     total_cost = Decimal('0.00')
#                     total_quantity = Decimal('0.00')

#                     for item in bill_items:
#                         item_quantity = item.quantity
#                         item_cost = item.price * (1 - item.discount_1 / 100) * (
#                             1 - item.discount_2 / 100) * (1 - item.discount_3 / 100) * (1 + item.vat / 100)

#                         total_cost += item_quantity * item_cost
#                         total_quantity += item_quantity

#                     average_cost = total_cost / \
#                         total_quantity if total_quantity > 0 else Decimal(
#                             '0.00')

#                 elif stock_issue_method == 'lifo':
#                     # LIFO maliyet hesaplama mantığı
#                     bill_items = BillItem.objects.filter(
#                         product=product, is_delete=False).order_by('-bill__date')

#                     # LIFO hesaplamaya başla
#                     total_cost = Decimal('0.00')
#                     total_quantity = Decimal('0.00')

#                     for item in bill_items:
#                         item_quantity = item.quantity
#                         item_cost = item.price * (1 - item.discount_1 / 100) * (
#                             1 - item.discount_2 / 100) * (1 - item.discount_3 / 100) * (1 + item.vat / 100)

#                         total_cost += item_quantity * item_cost
#                         total_quantity += item_quantity

#                     average_cost = total_cost / \
#                         total_quantity if total_quantity > 0 else Decimal(
#                             '0.00')

#                 else:  # Average Cost and other methods
#                     # Ortalama maliyet hesaplama mantığı

#                     # Ortalama maliyet hesaplamaya başla
#                     total_cost = BillItem.objects.filter(product=product, is_delete=False).aggregate(
#                         total_cost=Sum(
#                             ExpressionWrapper(
#                                 F('quantity') * F('price') * (1 - F('discount_1') / 100) * (
#                                     1 - F('discount_2') / 100) * (1 - F('discount_3') / 100) * (1 + F('vat') / 100),
#                                 output_field=DecimalField()
#                             )
#                         )
#                     )['total_cost'] or Decimal('0.00')

#                     total_quantity = BillItem.objects.filter(product=product, is_delete=False).aggregate(
#                         total_quantity=Sum('quantity')
#                     )['total_quantity'] or Decimal('0.00')

#                     average_cost = total_cost / \
#                         total_quantity if total_quantity > 0 else Decimal(
#                             '0.00')

#                 # Eğer ürünün ortalama maliyeti değiştiyse güncelle
#                 if product.average_cost != average_cost:
#                     product.average_cost = average_cost
#                     product.critical_stock_level = 10  # Örnek bir değer atandı
#                     product.save()

#                     # Veritabanı işleminin gerçekleştiğini doğrulama
#                     updated_product = Product.objects.get(id=product.id)
#                     print(
#                         f'Product {updated_product.id} updated: average_cost={updated_product.average_cost}, critical_stock_level={updated_product.critical_stock_level}')

#                     # Hata ayıklama mesajı
#                     print('Ürün için ortalama maliyet güncellendi:',
#                           instance.product.name, instance.product.average_cost)

#         except Exception as e:
#             print(f'Hata oluştu: {e}')

# # @receiver(post_save, sender=Seller)
# # def update_seller_balance(sender, instance, created, **kwargs):
# #     # Balance hesaplaması
# #     instance.balance = instance.receivable - instance.debt
# #     instance.save()


# def notify_users():
#     channel_layer = get_channel_layer()
#     async_to_sync(channel_layer.group_send)(
#         "company_1_group",
#         {
#             "type": "chat_message",
#             "message": {
#                 "type": "info",
#                 "content": "Yeni bir destek odası oluşturuldu!"
#             }
#         }
#     )


# @receiver(post_save, sender=ChatRoom)
# def notify_company_one_users(sender, instance, created, **kwargs):
#     if created:
#         # Destek odası oluşturuldu
#         # Firma kodu 1 olan kullanıcıları bilgilendirme işlemini buraya ekleyin
#         notify_users()
