from django.conf import settings
from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid
import os
class Company(models.Model):
    code = models.IntegerField(null=False, blank=False)
    name = models.CharField(max_length=255)
    owner = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=False)
    other_info = models.TextField()
    contract_start_date = models.DateTimeField(auto_now_add=True)
    contract_end_date = models.DateTimeField()
    create_user = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_companies')
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'Company'
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
    is_inventory = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.company} - {self.get_cost_calculation_display()}'
    class Meta:
        db_table = 'Parameter'


def get_upload_to(instance, filename):
    company_code = instance.company.code  # veya instance.user.company.code
    filename = os.path.basename(filename)
    directory = os.path.join('companies', str(company_code))

    # Dosyanın yükleneceği tam yolu oluşturun
    full_path = os.path.join(settings.MEDIA_ROOT, directory)

    # Eğer dizin mevcut değilse oluşturun
    if not os.path.exists(full_path):
        os.makedirs(full_path)

    return os.path.join(directory, filename)
class User(AbstractUser):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING)
    username = models.CharField(max_length=255, null=False, blank=False, unique=False)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True,blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'unique_id'  # USERNAME_FIELD'ı değiştir
    TAG_CHOICES = [
        ('Kurucu','Kurucu'),
        ('Yönetici', 'Yönetici'),
        ('Yetkili', 'Yetkili'),
        ('Destek', 'Destek'),
        ('Kullanıcı', 'Kullanıcı'),
    ]

    tag = models.CharField(max_length=15, choices=TAG_CHOICES, null=True, blank=True,default='Kullanıcı')
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    rating = models.PositiveIntegerField(null=True,blank=True)
    support_given = models.PositiveIntegerField(null=True,blank=True)
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

    class Meta:
        unique_together = ('username', 'company')  # username ve company birlikte benzersiz

    class Meta:
        db_table = 'User'
     
class Permission(models.Model):
    # Kullanıcıya özel izinler
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='permissions')
    # support user perm
    add_company = models.BooleanField(default=False)
    list_company = models.BooleanField(default=False)
    set_agreement_date = models.BooleanField(default=False)
    set_company_status = models.BooleanField(default=False)
    access_to_bugs = models.BooleanField(default=False)

    add_user = models.BooleanField(default=False)
    add_bill = models.BooleanField(default=False)
    
    add_inventory = models.BooleanField(default=False)
    add_parameter = models.BooleanField(default=False)
    # define perm
    add_product = models.BooleanField(default=False)
    add_category = models.BooleanField(default=False)
    add_seller = models.BooleanField(default=False)
    add_outgoing = models.BooleanField(default=False)
    add_unit = models.BooleanField(default=False)
    add_user = models.BooleanField(default=False)
    # update perm
    update_unit = models.BooleanField(default=False),
    update_seller = models.BooleanField(default=False),
    update_user = models.BooleanField(default=False)
    update_category = models.BooleanField(default=False)

    #delete perm
    delete_unit = models.BooleanField(default=False)
    delete_product = models.BooleanField(default=False)
    delete_outgoing_reason = models.BooleanField(default=False)
    # access perm
    access_to_reports = models.BooleanField(default=False)
    # paid unpaid
    paid_unpaid_bill = models.BooleanField(default=False)
    payment_seller = models.BooleanField(default=False)


    class Meta:
        db_table = 'Permission'
    def save(self, *args, **kwargs):
        if self.user.company.code != 1:
            # Firma kodu 1 değilse belirli yetkileri devre dışı bırak
            self.add_company = False
            self.list_company = False
            self.set_agreement_date = False
            self.set_company_status = False
            # Diğer yetkileri de buraya ekleyebilirsiniz
        super(Permission, self).save(*args, **kwargs)   
class Seller(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=255,null=True,blank=True) 
    email = models.EmailField(max_length=255,null=True,blank=True)
    receivable = models.DecimalField(max_digits=10, decimal_places=5,null=True,blank=True,default=0)
    debt = models.DecimalField(max_digits=10, decimal_places=5,null=True,blank=True,default=0)
    status = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=10, decimal_places=5,null=True,blank=True,default=0)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'Seller'
class Category(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'Category'
class Unit(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    unit_name = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return self.unit_name
    class Meta:
        db_table = 'Unit'
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
    is_inventory = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    class Meta:
        db_table = 'Product'
class Bill(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    number = models.CharField(max_length=255,null=False,blank=False)
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=255, decimal_places=5, null=True, blank=True)
    seller = models.ForeignKey(Seller,on_delete=models.DO_NOTHING)
    expiry_date = models.DateField(null=False,blank=False)
    created_date = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return f"Bill {self.id} - {self.date}"
    class Meta:
        db_table = 'Bill'
class Inventory(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    code = models.IntegerField()
    unit = models.ForeignKey(Unit, on_delete=models.DO_NOTHING)
    serial_number = models.CharField(max_length=255, null=True, blank=True)
    barcode_1 = models.CharField(max_length=255, null=True, blank=True)
    barcode_2 = models.CharField(max_length=255, null=True, blank=True)
    barcode_3 = models.CharField(max_length=255, null=True, blank=True)
    is_released = models.BooleanField(default=False)
    def __str__(self):
        return self.serial_number if self.serial_number else f"Inventory for {self.product.name}"
    class Meta:
        db_table = 'Inventory'
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
    is_inventory = models.BooleanField(default = False)
    serial_number = models.CharField(max_length=255, null=True, blank=True)
    barcode_1 = models.CharField(max_length=255, null=True, blank=True)
    barcode_2 = models.CharField(max_length=255, null=True, blank=True)
    barcode_3 = models.CharField(max_length=255, null=True, blank=True)

    row_total = models.DecimalField(max_digits=255, decimal_places=3, null=True, blank=True, default=0.00)
    processing_time = models.DateTimeField(auto_now_add=True, verbose_name='İşlem Zamanı')  # Bu satırı ekleyin
    def __str__(self):
        return f"{self.product.name} - {self.quantity} {self.product.unit}"
    class Meta:
        db_table = 'BillItem'
class OutgoingReasons(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    is_delete = models.BooleanField(default=False)
    class Meta:
        db_table = 'OutgoingReasons'
class OutgoingBill(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    number = models.CharField(max_length=255,null=False,blank=False)
    product = models.ForeignKey(Product,on_delete=models.DO_NOTHING)
    quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    processing_time = models.DateTimeField(auto_now_add=True)
    outgoing_reason = models.ForeignKey(OutgoingReasons,on_delete=models.DO_NOTHING,null=True,blank=True)
    outgoing_total_amount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, default=0.00)
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    # envanter için oluşturulan modeller
    is_inventory = models.BooleanField(default = False)
    serial_number = models.CharField(max_length=255,null=True,blank=True)
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="outgoing_bills", null=True, blank=True)
    def __str__(self):
        return self.number
    class Meta:
        db_table = 'OutgoingBill'
class StockTransactions(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.DO_NOTHING,verbose_name='Ürün')  # Ürün adı veya açıklaması
    outgoing_quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True,verbose_name='Çıkan Miktar')
    incoming_quantity = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True,verbose_name='Giren Miktar')
    processing_time = models.DateTimeField(auto_now_add=True,verbose_name='İşlem Zamanı')  # İşlem zamanı
    outgoing_bill = models.ForeignKey(OutgoingBill,on_delete=models.DO_NOTHING,null=True,blank=True,verbose_name='Çıkış Faturası')  # Çıkış faturası
    outgoing_reasons = models.ForeignKey(OutgoingReasons,on_delete=models.DO_NOTHING,null=True,blank=True)
    incoming_bill = models.ForeignKey(Bill,on_delete=models.DO_NOTHING,null=True,blank=True,verbose_name='Giriş Faturası')  # Giriş faturası
    current_stock = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True,verbose_name='Toplam Tutar')
    is_create = models.ForeignKey(User,on_delete=models.CASCADE)
    is_delete = models.BooleanField(default=False)
    def __str__(self):
        return self.product
    class Meta:
        db_table = 'StockTransactions'

class ChatRoom(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.BooleanField(default=True) # oda durumu
    supportive = models.ForeignKey(User, on_delete=models.CASCADE,related_name="support_team_user",null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0,null=True,blank=True)
    class Meta:
        db_table = 'ChatRoom'
class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'Message'
class ErrorMessage(models.Model):
    reporting_company = models.ForeignKey(Company, on_delete=models.DO_NOTHING,)
    reporting_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    error_title = models.CharField(max_length=200)
    error_description = models.TextField()
    error_screenshot = models.ImageField(upload_to='error_screenshots/',null=True,blank=True)
    error_status = models.BooleanField(default=False) # false okunmadı true okundu
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        # Override save method to set upload_to path dynamically
        if self.error_screenshot:
            self.error_screenshot.name = f"{self.reporting_company.code}/{self.reporting_user.unique_id}/{self.error_screenshot.name}"
        super().save(*args, **kwargs)