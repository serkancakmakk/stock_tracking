from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, Product, Seller, Unit

from .forms import CategoryForm, ProductForm, SellerForm, UnitForm

def create_page(request):
    products = Product.objects.all()
    unit_form = UnitForm()
    category_form = CategoryForm()
    seller_form = SellerForm()
    units = Unit.objects.all()
    sellers = Seller.objects.all()
    categories = Category.objects.all()
    product_form = ProductForm()
    # Get a list of existing seller names
    existing_seller_names = [seller.name for seller in sellers]
    existing_category_names = [category.name for category in categories]


    context = {
        'products':products,
        'existing_category_names':existing_category_names,
        'categories':categories,
        'product_form':product_form,
        'category_form':category_form,
        'sellers': sellers,
        'seller_form': seller_form,
        'units': units,
        'unit_form': unit_form,
        'existing_seller_names': existing_seller_names,
    }
    return render(request, 'create_page.html', context)
from django.contrib import messages
def create_unit(request):
    if not request.method =="POST":
        messages.add_message(request, messages.INFO, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    unit_name = request.POST.get("unit_name")
    print(unit_name)
    if unit_name == '':
        messages.add_message(request, messages.INFO, "Birim Adı Boş Olamaz")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    if Unit.objects.filter(unit_name=unit_name).exists():
            messages.add_message(request, messages.INFO, "Birim Adı Zaten Kayıtlı")
            return redirect(request.META.get('HTTP_REFERER', '/'))
    Unit.objects.create(
        unit_name = unit_name
    )
    messages.add_message(request, messages.SUCCESS, "Kayıt Gerçekleşti")
    return redirect(request.META.get('HTTP_REFERER', '/'))
def delete_unit(request, unit_id):
    if request.method != "POST":
        messages.add_message(request, messages.INFO, "Silme İşlemi Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        unit = Unit.objects.get(id=unit_id)
    except Unit.DoesNotExist:
        messages.add_message(request, messages.ERROR, "Unit bulunamadı")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if Product.objects.filter(unit=unit).exists():
        messages.add_message(request, messages.WARNING, "Bu birim bir ürüne bağlı olduğu için silinemez")
    else:
        unit.delete()
        messages.add_message(request, messages.SUCCESS, "Birim başarıyla silindi")

    return redirect(request.META.get('HTTP_REFERER', '/'))
def create_seller(request):
    if not request.method =="POST":
        messages.add_message(request, messages.INFO, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    seller_name = request.POST.get("seller_name")
    print(seller_name)
    seller_address = request.POST.get("seller_address")
    print(seller_address)
    Seller.objects.create(
        name=seller_name,
        address = seller_address
    )
    messages.add_message(request, messages.SUCCESS, "Cari Oluşturuldu")
    return redirect(request.META.get('HTTP_REFERER', '/'))
def create_category(request):
    if not request.method =="POST":
        messages.add_message(request, messages.INFO, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    category_name = request.POST.get("category_name")
    Category.objects.create(
        name = category_name
    )
    messages.add_message(request, messages.SUCCESS, "Kategori Oluşturuldu")
    return redirect(request.META.get('HTTP_REFERER', '/'))
def create_product(request):
    if request.method != "POST":
        messages.add_message(request, messages.INFO, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    product_name = request.POST.get("product_name")
    product_code = request.POST.get("product_code")
    product_unit = request.POST.get("product_unit")
    product_category = request.POST.get("product_category")
    
    # Debugging prints
    print(f'Product Name: {product_name}')
    print(f'Product Code: {product_code}')
    print(f'Product Unit: {product_unit}')
    print(f'Product Category: {product_category}')
    
    if not product_unit:
        messages.add_message(request, messages.ERROR, "Ürün Birimi Boş Geçilemez.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        unit = get_object_or_404(Unit, id=product_unit)
    except ValueError:
        messages.add_message(request, messages.ERROR, "Geçersiz Ürün Birimi ID.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    except Unit.DoesNotExist:
        messages.add_message(request, messages.ERROR, "Ürün Birimi Bulunamadı.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    print('UNIT:', unit)
    
    try:
        category = Category.objects.get(id=product_category)
    except Category.DoesNotExist:
        messages.add_message(request, messages.ERROR, "Kategori Bulunamadı.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    Product.objects.create(
        name=product_name,
        code=product_code,
        unit=unit,
        category=category,
    )
    
    messages.add_message(request, messages.SUCCESS, "Ürün Kaydedildi")
    return redirect(request.META.get('HTTP_REFERER', '/'))