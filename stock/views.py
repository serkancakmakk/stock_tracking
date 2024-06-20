from django.shortcuts import redirect, render

from .models import Product, Seller, Unit

from .forms import SellerForm, UnitForm

def create_page(request):
    unit_form = UnitForm()
    seller_form = SellerForm()
    units = Unit.objects.all()
    sellers = Seller.objects.all()
    
    # Get a list of existing seller names
    existing_seller_names = [seller.name for seller in sellers]

    context = {
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