from django import forms
from .models import Category, Company, ErrorMessage, OutgoingReasons, Parameter, Product, Bill, BillItem, Seller, Unit
class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name', 'address']
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','is_active']
class UnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_name']
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['code', 'name', 'unit', 'category']

class BillForm(forms.ModelForm):
    class Meta:
        model = Bill
        fields = ['total_amount']

class BillItemForm(forms.ModelForm):
    class Meta:
        model = BillItem
        fields = ['bill', 'product', 'quantity', 'price']
class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name','owner','address', 'phone', 'city', 'country', 'email', 'other_info','contract_end_date']
        # forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.core.exceptions import ValidationError
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','phone','password1','password2','address','email','tag']


    def __init__(self, *args, **kwargs):
        self.company = kwargs.pop('company', None)  # `company`'yi formdan al
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if self.company and User.objects.filter(username=username, company=self.company).exists():
            raise ValidationError("Bu kullanıcı adı bu şirkette zaten mevcut.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            self.add_error('password2', "Şifreler eşleşmiyor.")

        return cleaned_data
class ParameterForm(forms.ModelForm):
    class Meta:
        model = Parameter
        fields = ['cost_calculation']
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','phone','email','address','is_active','profile_image','tag']
from .models import Permission
class PermissionForm(forms.ModelForm):
    class Meta:
        model = Permission
        fields = ['add_company', 'add_user','add_bill','add_inventory','add_parameter','access_to_reports',
                  #define
                'add_product','add_category','add_seller','add_outgoing','add_unit','add_user','delete_unit',
                'update_user',
                'set_agreement_date',
                'list_company',
                'set_company_status',]
class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name', 'address','email','phone','receivable', 'debt','balance']
class ProductForm (forms.ModelForm):
    class Meta:
        model = Product
        fields =['code','name','unit','category','is_critical','prevent_stock_negative','critical_stock_level','is_inventory']
    
class ProductUpdateForm(forms.ModelForm):
    class Meta:
        model = Product
        fields =['code','name','unit','category','is_critical','prevent_stock_negative','critical_stock_level','is_inventory']
class OutgoingUpdateForm(forms.ModelForm):
    class Meta:
        model = OutgoingReasons
        fields = ['name','is_active']

class UpdateUnitForm(forms.ModelForm):
    class Meta:
        model = Unit
        fields = ['unit_name', 'is_active']
class ReportBugForm(forms.ModelForm):
    class Meta:
        model = ErrorMessage
        fields = ['error_title','error_description','error_screenshot']
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label="Eski Şifre",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    new_password1 = forms.CharField(
        label="Yeni Şifre",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )
    new_password2 = forms.CharField(
        label="Yeni Şifreyi Doğrula",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get("new_password1")
        new_password2 = cleaned_data.get("new_password2")

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("Şifreler uyuşmuyor.")
        return cleaned_data