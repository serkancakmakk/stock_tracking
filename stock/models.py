from django.db import models
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid
class Company(models.Model):
    code = models.IntegerField(null=False, blank=False)
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    other_info = models.TextField()
    contract_start_date = models.DateTimeField(auto_now_add=True)
    contract_end_date = models.DateTimeField()
    create_user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_companies')
class User(AbstractUser):
    company = models.ForeignKey(Company,on_delete=models.DO_NOTHING)
    company_code = models.IntegerField()
    phone = models.CharField(max_length=255, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True,
        help_text='Bu kullanıcının ait olduğu gruplar. Bir kullanıcı, ait olduğu her grubun tüm izinlerini alacaktır.',
        verbose_name='Gruplar',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True,
        help_text='Bu kullanıcı için belirli izinler.',
        verbose_name='Kullanıcı izinleri',
    )

   
# class Yetki(models.Model):
#     # Kullanıcıya özel izinler
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='yetkiler')
#     # ssoft kullanıcı yetkileri
#         # ekleme yetkileri
#     # add_company
#     # add_user
#     #     # düzenleme yetkileri
#     # edit_company
#     # edit_user
#         # erisim yetkileri
    
class Parameter(models.Model):
    COST_CHOICES = [
        ('fifo', 'FIFO'),
        ('lifo', 'LIFO'),
        ('average_cost', 'Ortalama Maliyet'),
        ('specific_identification', 'Belirli Tanımlama'),
        ('standard_costing', 'Standart Maliyetleme'),
        ('moving_average', 'Hareketli Ortalama'),
        ('weighted_average', 'Ağırlıklı Ortalama'),
        ('replacement_cost', 'Yenileme Maliyeti'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    cost_calculation = models.CharField(
        max_length=50,
        choices=COST_CHOICES,
        default='fifo'
    )

    def __str__(self):
        return f'{self.company} - {self.get_cost_calculation_display()}'

    
class Seller(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    receivable = models.DecimalField(max_digits=10, decimal_places=5,null=True,blank=True)
    debt = models.DecimalField(max_digits=10, decimal_places=5,null=True,blank=True)
    status = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=10, decimal_places=5,null=True,blank=True,default=0)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.name
class Category(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.name
class Unit(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    unit_name = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.unit_name
class Product(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    code = models.IntegerField()
    name = models.CharField(max_length=255)
    unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    average_cost = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    current_stock = models.DecimalField(max_digits=10, decimal_places=3, default=0)
    is_critical = models.BooleanField(default=False)
    prevent_stock_negative = models.BooleanField(default=False)
    critical_stock_level = models.IntegerField(default=0)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class Bill(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    number = models.CharField(max_length=255,null=False,blank=False)
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=5, null=True, blank=True)
    seller = models.ForeignKey(Seller,on_delete=models.DO_NOTHING)
    expiry_date = models.DateField(null=False,blank=False)
    created_date = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return f"Bill {self.id} - {self.date}"

class BillItem(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=3)
    price = models.DecimalField(max_digits=10, decimal_places=3)
    discount_1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    discount_2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    discount_3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    vat = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True, default=0.00)
    is_delete = models.BooleanField(default=False)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.product.unit}"
class OutgoingReasons(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
class OutgoingBill(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    number = models.CharField(max_length=255,null=False,blank=False)
    product = models.ForeignKey(Product,on_delete=models.DO_NOTHING)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    processing_time = models.DateTimeField(auto_now_add=True)
    outgoing_reason = models.ForeignKey(OutgoingReasons,on_delete=models.DO_NOTHING,null=True,blank=True)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.number
class StockTransactions(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.DO_NOTHING)  # Ürün adı veya açıklaması
    outgoing_quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    incoming_quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    processing_time = models.DateTimeField(auto_now_add=True)  # İşlem zamanı
    outgoing_bill = models.ForeignKey(OutgoingBill,on_delete=models.DO_NOTHING,null=True,blank=True)  # Çıkış faturası
    outgoing_reasons = models.ForeignKey(OutgoingReasons,on_delete=models.DO_NOTHING,null=True,blank=True)
    incoming_bill = models.ForeignKey(Bill,on_delete=models.DO_NOTHING,null=True,blank=True)  # Giriş faturası
    current_stock = models.IntegerField()
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.product
