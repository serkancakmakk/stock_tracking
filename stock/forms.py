from django import forms
from .models import Category, Company, Parameter, Product, Bill, BillItem, Seller, Unit
class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name', 'address']
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
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
class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(max_length=255, required=False)
    surname = forms.CharField(max_length=255, required=False)
    phone = forms.CharField(max_length=255, required=False)
    address = forms.CharField(max_length=255, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'name', 'surname', 'phone', 'address')
class ParameterForm(forms.ModelForm):
    class Meta:
        model = Parameter
        fields = ['cost_calculation']