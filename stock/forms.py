from django import forms
from .models import Category, Product, Bill, BillItem, Seller, Unit
class SellerForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name', 'address']
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
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