# myapp/context_processors.py
from .models import ChatRoom, Company, Product
from django.db.models import F
# core/context_processors.py

from django.db.models import F
from .models import Product, Company  # İmport yollarını projenizin yapısına göre ayarlayın
def waiting_for_support(request):
    waiting_for_support_count = ChatRoom.objects.filter(status=False).count()
    return {'waiting_for_support': waiting_for_support_count}
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
    low_stock_products = Product.objects.filter(company=company,is_critical = True, current_stock__lt=F('critical_stock_level'))
    low_stock_count = low_stock_products.count()

    return {
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
    }

from datetime import datetime

def today_date(request):
    today = datetime.now().strftime('%Y-%m-%d')
    return {'today': today}
from .models import Permission
# def user_permissions(request):
#     if request.user.is_authenticated:
#         try:
#             permissions = Permission.objects.get(user=request.user)
#             permission = {
#                 'add_company': permissions.add_company,
#                 'add_user': permissions.add_user,
#                 'add_bill': permissions.add_bill,
#                 'add_outgoing': permissions.add_outgoing,
#                 'add_inventory': permissions.add_inventory,
#                 'add_parameter': permissions.add_parameter,
#                 #define perm
#                 'add_product':permissions.add_product,
#                 'add_category':permissions.add_category,
#                 'add_seller':permissions.add_seller,
#                 'add_outgoing':permissions.add_outgoing,
#                 'add_unit':permissions.add_unit,
#                 'add_user':permissions.add_user,
#                 #update perm
#                 'update_unit':permissions.update_unit,
#             }
#         except Permission.DoesNotExist:
#             permission = {}
#     else:
#         permission = {}

#     return {'user_permissions': permission}