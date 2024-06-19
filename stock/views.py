from django.shortcuts import redirect, render

from .models import Unit

from .forms import UnitForm

def create_page(request):
    unit_form = UnitForm
    units = Unit.objects.all()
    context = {
        'units':units,
        'unit_form':unit_form,
    }
    return render(request,'create_page.html',context)
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
