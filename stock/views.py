from django.shortcuts import render

from .forms import UnitForm

def create_page(request):
    unit_form = UnitForm
    context = {
        'unit_form':unit_form,
    }
    return render(request,'create_page.html',context)
