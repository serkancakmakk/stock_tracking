from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.db.models import Sum, F
from decimal import Decimal
from .models import BillItem, Product, Seller

@receiver(post_save, sender=BillItem)
def update_product_average_cost(sender, instance, created, **kwargs):
    if created:
        try:
            with transaction.atomic():
                # Ürünü al ve ortalama maliyeti hesapla
                product = instance.product

                total_cost = BillItem.objects.filter(product=product,is_delete=False).aggregate(
                    total_cost=Sum(
                        F('quantity') * F('price') * (1 - F('discount_1') / 100) * (1 - F('discount_2') / 100) * (1 - F('discount_3') / 100) * (1 + F('vat') / 100)
                    )
                )['total_cost'] or Decimal('0.00')

                total_quantity = BillItem.objects.filter(product=product,is_delete=False).aggregate(
                    total_quantity=Sum('quantity')
                )['total_quantity'] or Decimal('0.00')

                average_cost = total_cost / total_quantity if total_quantity > 0 else Decimal('0.00')

                # Eğer ürünün ortalama maliyeti değiştiyse güncelle
                if product.average_cost != average_cost:
                    product.average_cost = average_cost
                    product.critical_stock_level = 10  # Örnek bir değer atandı
                    product.save()

                    # Veritabanı işleminin gerçekleştiğini doğrulama
                    updated_product = Product.objects.get(id=product.id)
                    print(f'Product {updated_product.id} updated: average_cost={updated_product.average_cost}, critical_stock_level={updated_product.critical_stock_level}')

                    # Hata ayıklama mesajı
                    print('Ürün için ortalama maliyet güncellendi:', instance.product.id)

        except Exception as e:
            print(f'Hata oluştu: {e}')
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Bill, BillItem, StockTransactions
# @receiver(post_save, sender=Seller)
# def update_seller_balance(sender, instance, created, **kwargs):
#     # Balance hesaplaması
#     instance.balance = instance.receivable - instance.debt
#     instance.save()