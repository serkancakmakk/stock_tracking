# myapp/context_processors.py
from .models import Product
from django.db.models import F
def low_stock_count(request):
    # Filter products where the current stock is less than the critical stock level
    low_stock_products = Product.objects.filter(current_stock__lt=F('critical_stock_level'))
    low_stock_count = low_stock_products.count()

    # Return the results in the context
    return {
        'low_stock_products': low_stock_products,
        'low_stock_count': low_stock_count,
    }