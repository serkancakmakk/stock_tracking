from datetime import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Bill, BillItem, Category, OutgoingReasons, Product, Seller, StockTransactions, Unit

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
def create_outgoing_reasons_page(request):
    reasons = OutgoingReasons.objects.all()
    context = {
        'reasons':reasons,
    }
    return render(request,'definitions/define_outgoing.html',context)
def create_outgoing_reasons(request):
    if not request.method == "POST":
        messages.add_message(request, messages.INFO, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    outgoing_reasons_name = request.POST.get("outgoing_reason")
    exists_reason = OutgoingReasons.objects.get(name=outgoing_reasons_name)
    if exists_reason:
        messages.add_message(request, messages.INFO, "Aynı İsimde Bir Çıkış Nedeni Bulunuyor")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    cikis_nedeni = OutgoingReasons.objects.create(
        name = outgoing_reasons_name,
    )
    cikis_nedeni.save()
    messages.add_message(request, messages.SUCCESS, f"{cikis_nedeni.name} adlı stok çıkış nedeni oluşturuldu")
    return redirect(request.META.get('HTTP_REFERER', '/'))
def change_active_status(request, id):
    selected_reason = get_object_or_404(OutgoingReasons, id=id)
    selected_reason.is_active = not selected_reason.is_active
    selected_reason.save()
    
    messages.add_message(request, messages.SUCCESS, f"Status of '{selected_reason.name}' changed to {'Active' if selected_reason.is_active else 'Inactive'}")
    return redirect(request.META.get('HTTP_REFERER', '/'))
def create_seller(request):
    if request.method != "POST":
        sellers = Seller.objects.all()
        context = {
            'sellers': sellers,
        }
        return render(request, 'definitions/define_seller.html', context)
    
    seller_name = request.POST.get("seller_name")
    seller_address = request.POST.get("seller_address")
    
    Seller.objects.create(
        name=seller_name,
        address=seller_address
    )
    

    messages.success(request, "Cari Oluşturuldu")
    
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
def product_add_page(request):
    units = Unit.objects.all()
    categories = Category.objects.all()
    products = Product.objects.all()
    
    context = {
        'categories': categories,
        'units': units,
        'products': products
    }
    
    return render(request, 'definitions/define_product.html', context)
def create_product(request):

    if not request.method == "POST":
        messages.add_message(request, messages.ERROR, "Ürün Birimi Boş Geçilemez.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    products = Product.objects.all()
    for product in products:
        print(product)
    product_name = request.POST.get("product_name")
    product_code = request.POST.get("product_code")
    product_unit = request.POST.get("product_unit")
    product_category = request.POST.get("product_category")
    product_is_critical = request.POST.get("critical_product") == "on"
    critical_stock_level = request.POST.get("critical_stock_level")
    prevent_stock_negative = request.POST.get("prevent_stock_negative") == "on"
    print(f'Product Name: {product_name}')
    print(f'Product Code: {product_code}')
    print(f'Product Unit: {product_unit}')
    print(f'Critical Product: {product_is_critical}')
    print(f'Critical Stock Level: {critical_stock_level}')
    print(f'Prevent Stock Negative: {prevent_stock_negative}')
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
    if critical_stock_level == '':
        critical_stock_level = 0
    Product.objects.create(
        name=product_name,
        code=product_code,
        unit=unit,
        category=category,
        is_critical=product_is_critical,
        critical_stock_level=critical_stock_level,
        prevent_stock_negative=prevent_stock_negative,
    )

    messages.add_message(request, messages.SUCCESS, "Ürün Kaydedildi")
    return redirect(request.META.get('HTTP_REFERER', '/'))
from decimal import Decimal
from decimal import Decimal, InvalidOperation
def add_bill(request):
    sellers = Seller.objects.all()
    products = Product.objects.all()

    if request.method == "POST":
        try:
            bill_number = request.POST.get("bill_number")
            bill_expiry_date = request.POST.get("bill_expiry_date")
            bill_seller_id = request.POST.get("bill_seller")
            bill_item_product_id = request.POST.get("bill_item_product")
            bill_item_quantity = Decimal(request.POST.get("bill_item_quantity", '0'))
            bill_item_price = Decimal(request.POST.get("bill_item_price", '0'))
            bill_item_discount_1 = Decimal(request.POST.get("bill_item_discount_1", '0'))
            bill_item_discount_2 = Decimal(request.POST.get("bill_item_discount_2", '0'))
            bill_item_discount_3 = Decimal(request.POST.get("bill_item_discount_3", '0'))
            bill_item_vat = Decimal(request.POST.get("bill_item_vat", '0'))

            bill_seller = get_object_or_404(Seller, id=bill_seller_id)
            bill = Bill.objects.create(
                number=bill_number,
                expiry_date=bill_expiry_date,
                seller=bill_seller
            )

            product = get_object_or_404(Product, id=bill_item_product_id)
            BillItem.objects.create(
                bill=bill,
                product=product,
                quantity=bill_item_quantity,
                price=bill_item_price,
                discount_1=bill_item_discount_1,
                discount_2=bill_item_discount_2,
                discount_3=bill_item_discount_3,
                vat=bill_item_vat
            )
            bill.total_amount = bill_item_quantity * bill_item_price
            total_amount_vat = (bill.total_amount / 100 * bill_item_vat)
            final_price_1 = bill.total_amount + total_amount_vat
            final_price_12 = final_price_1 - (final_price_1 / 100 * bill_item_discount_1)
            final_price_2 = final_price_12 - (final_price_12 / 100 * bill_item_discount_2)
            final_price_3 = final_price_2 - (final_price_2 / 100 * bill_item_discount_3)
            bill.total_amount = final_price_3

            bill.save()

            stock, created = StockTransactions.objects.get_or_create(
                product=product,
                incoming_bill=bill,
                defaults={
                    'incoming_quantity': bill_item_quantity,
                    'processing_time': timezone.now(),
                }
            )
            if not created:
                stock.incoming_quantity += bill_item_quantity
                stock.save()

            messages.success(request, "Fatura ve Kalemler Başarıyla Oluşturuldu")
            return redirect('fatura_detay', bill_number=bill.number)

        except (Seller.DoesNotExist, Product.DoesNotExist) as e:
            messages.error(request, "Fatura Oluşturulamadı. Satıcı veya Ürün bulunamadı.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        except InvalidOperation as e:
            messages.error(request, f"Veri hatası: {str(e)}")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        except Exception as e:
            messages.error(request, f"Fatura Oluşturulamadı. Hata: {str(e)}")
            return redirect(request.META.get('HTTP_REFERER', '/'))

    context = {
        'products': products,
        'sellers': sellers,
    }
    return render(request, 'add_bill.html', context)
def bill_details(request, bill_number):
    products = Product.objects.all()
    bill = get_object_or_404(Bill, number=bill_number)
    bill_items = BillItem.objects.filter(bill=bill)
    print(bill_items)

    context = {
        'products':products,
        'bill': bill,
        'bill_items': bill_items,
    }
    return render(request, 'bill_details.html', context)
def bills(request):
    bills = Bill.objects.all()
    context = {
        'bills':bills,
    }
    return render(request,'bills.html',context)

def add_billitem(request, bill_id):
    if request.method != "POST":
        messages.error(request, "Kalem oluşturulamadı. POST isteği bekleniyor.")
        return JsonResponse({'error': 'POST method expected.'}, status=400)

    bill = get_object_or_404(Bill, id=bill_id)
    bill_item_product_id = request.POST.get("bill_item_product")
    product = get_object_or_404(Product, id=bill_item_product_id)

    try:

        bill_item_quantity = Decimal(request.POST.get("bill_item_quantity", '0').replace(',', '.'))
        bill_item_price = Decimal(request.POST.get("bill_item_price", '0').replace(',', '.'))
        bill_item_discount_1 = Decimal(request.POST.get("bill_item_discount_1", '0').replace(',', '.'))
        bill_item_discount_2 = Decimal(request.POST.get("bill_item_discount_2", '0').replace(',', '.'))
        bill_item_discount_3 = Decimal(request.POST.get("bill_item_discount_3", '0').replace(',', '.'))
        bill_item_vat = Decimal(request.POST.get("bill_item_vat", '0').replace(',', '.'))
    except InvalidOperation:
        messages.error(request, "Geçersiz sayı formatı. Lütfen doğru formatta sayı giriniz.")
        return JsonResponse({'error': 'Invalid number format.'}, status=400)

    try:

        item_total = bill_item_quantity * bill_item_price

        bill_item = BillItem.objects.create(
            bill=bill,
            product=product,
            quantity=bill_item_quantity,
            price=bill_item_price,
            discount_1=bill_item_discount_1,
            discount_2=bill_item_discount_2,
            discount_3=bill_item_discount_3,
            vat=bill_item_vat
        )


        stock, created = CurrentStock.objects.get_or_create(
            product=product,
            defaults={
                'current_stock': bill_item_quantity,
                'incoming_bill': bill
            }
        )

        if not created:
            stock.current_stock += bill_item_quantity
            stock.incoming_bill = bill 
        stock.save()


        bill.total_amount += item_total


        bill.save()


        response_data = {
            "bill_item_product": product.name,
            "bill_item_quantity": f"{bill_item_quantity:.2f}",
            "bill_item_price": f"{bill_item_price:.2f}",
            "bill_item_discount_1": f"{bill_item_discount_1:.2f}",
            "bill_item_discount_2": f"{bill_item_discount_2:.2f}",
            "bill_item_discount_3": f"{bill_item_discount_3:.2f}",
            "bill_item_vat": f"{bill_item_vat:.2f}",
            "new_total_amount": f"{bill.total_amount:.2f}",
        }

        return JsonResponse(response_data)

    except Exception as e:
        messages.error(request, f"Kalem oluşturulamadı: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
from datetime import datetime
def stock_status(request):
    stock_transactions = StockTransactions.objects.select_related('product', 'incoming_bill', 'outgoing_reasons').all()

    incoming_quantities = {}
    outgoing_quantities = {}

    for stock in stock_transactions:
        incoming_quantity = stock.incoming_quantity or 0
        outgoing_quantity = stock.outgoing_quantity or 0

        # Gelen miktarları toplama
        if stock.product_id in incoming_quantities:
            incoming_quantities[stock.product_id] += incoming_quantity
        else:
            incoming_quantities[stock.product_id] = incoming_quantity

        # Giden miktarları toplama
        if stock.product_id in outgoing_quantities:
            outgoing_quantities[stock.product_id] += outgoing_quantity
        else:
            outgoing_quantities[stock.product_id] = outgoing_quantity

    products = Product.objects.all()
    product_data = []

    for product in products:
        incoming_quantity = incoming_quantities.get(product.id, 0)
        outgoing_quantity = outgoing_quantities.get(product.id, 0)
        current_stock = incoming_quantity - outgoing_quantity

        product_data.append({
            'name': product.name,
            'total_incoming': incoming_quantity,
            'total_outgoing': outgoing_quantity,
            'current_stock': current_stock
        })

    today = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    context = {
        'products': product_data,
        'today': today,
    }

    return render(request, 'stock_status_report.html', context)
from django.utils import timezone
def incoming_outgoing_reports(request):
    products = Product.objects.all()
    stock_transactions = StockTransactions.objects.all()
    context = {
        'stock_transactions':stock_transactions,
        'products':products,
    }
    return render(request,'reports/incoming_outgoing_reports.html',context)
def process_stock_outgoing(request):
    products = Product.objects.all()
    outgoing_reasons = OutgoingReasons.objects.all()

    if request.method != "POST":
        context = {
            'products': products,
            'outgoing_reasons': outgoing_reasons,
        }
        return render(request, 'stock_outgoing.html', context)

    outgoing_product_id = request.POST.get('outgoing_product')
    outgoing_quantity = request.POST.get('outgoing_quantity')
    outgoing_reason_id = request.POST.get('outgoing_reason')
    outgoing_bill_number = request.POST.get('outgoing_bill_number')

    if not (outgoing_product_id and outgoing_quantity and outgoing_reason_id and outgoing_bill_number):
        messages.add_message(request, messages.ERROR, "All fields are required.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        if StockTransactions.objects.filter(outgoing_bill=outgoing_bill_number).exists():
            messages.error(request, 'Bill number already exists.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        outgoing_product = Product.objects.get(id=outgoing_product_id)
        outgoing_reason = OutgoingReasons.objects.get(id=outgoing_reason_id)

        stock_outgoing = StockTransactions.objects.create(
            product=outgoing_product,
            outgoing_quantity=Decimal(outgoing_quantity),
            outgoing_reasons=outgoing_reason,
            outgoing_bill=outgoing_bill_number,  
            processing_time=timezone.now(),
        )
        stock_outgoing.save()
        messages.success(request, 'Stock outgoing processed successfully.')
    except Product.DoesNotExist:
        messages.error(request, 'Product does not exist.')
    except OutgoingReasons.DoesNotExist:
        messages.error(request, 'Outgoing reason does not exist.')
    except InvalidOperation as e:
        messages.error(request, f"Data error: {str(e)}")
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        print(e)

    return redirect(request.META.get('HTTP_REFERER', '/'))