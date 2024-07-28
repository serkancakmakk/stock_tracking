# myapp/context_processors.py
from .models import Company, Product
from django.db.models import F
# core/context_processors.py

from django.db.models import F
from stock.models import Product, Company  # İmport yollarını projenizin yapısına göre ayarlayın

def low_stock_count(request):
    # URL'den şirket kodunu al
    company_code = request.resolver_match.kwargs.get('code')

    # şirket geçerli mi ?
    if not company_code:
        return {}

    # Şirketi bul
    company = Company.objects.filter(code=company_code).first()

    if not company:
        return {}

    # Kritik stok seviyesinden düşük olan ürünleri filtrele
    low_stock_products = Product.objects.filter(company=company, current_stock__lt=F('critical_stock_level'))
    low_stock_count = low_stock_products.count()

    return {
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
    }

from datetime import datetime

def today_date(request):
    today = datetime.now().strftime('%Y-%m-%d')
    return {'today': today}