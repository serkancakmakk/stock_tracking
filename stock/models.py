from django.db import models
class Seller(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    receivable = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    debt = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    status = models.BooleanField(default=True)
    def __str__(self):
        return self.name
class Category(models.Model):
    name = models.CharField(max_length=255)
    def __str__(self):
        return self.name
class Unit(models.Model):
    unit_name = models.CharField(max_length=10)
    def __str__(self):
        return self.unit_name
class Product(models.Model):
    code = models.IntegerField()
    name = models.CharField(max_length=255)
    unit = models.ForeignKey(Unit,on_delete=models.DO_NOTHING)  # max_length biraz artırıldı
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    current_stock = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    is_critical = models.BooleanField(default=False)
    prevent_stock_negative = models.BooleanField(default=False)
    critical_stock_level = models.IntegerField(default=0)
    def __str__(self):
        return self.name

class Bill(models.Model):
    number = models.CharField(max_length=255,null=False,blank=False)
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    seller = models.ForeignKey(Seller,on_delete=models.DO_NOTHING)
    expiry_date = models.DateField(null=False,blank=False)
    created_date = models.DateField(auto_now_add=True)
    # created_at = models.ForeignKey(user)
    def __str__(self):
        return f"Bill {self.id} - {self.date}"

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    price = models.DecimalField(max_digits=10, decimal_places=3)
    discount_1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    discount_2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    discount_3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    vat = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, default=0.00)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.product.unit}"
class OutgoingReasons(models.Model):
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
class StockTransactions(models.Model):
    product = models.ForeignKey(Product,on_delete=models.DO_NOTHING)  # Ürün adı veya açıklaması
    outgoing_quantity = models.IntegerField(null=True,blank=True)  # Çıkış miktarı
    incoming_quantity = models.IntegerField(null=True,blank=True)  # Giriş miktarı
    processing_time = models.DateTimeField(auto_now_add=True)  # İşlem zamanı
    outgoing_bill = models.CharField(max_length=255,null = False,blank=False)  # Çıkış faturası
    outgoing_reasons = models.ForeignKey(OutgoingReasons,on_delete=models.DO_NOTHING,null=True,blank=True)
    incoming_bill = models.ForeignKey(Bill,on_delete=models.DO_NOTHING,null=True,blank=True)  # Giriş faturası

    def __str__(self):
        return self.product