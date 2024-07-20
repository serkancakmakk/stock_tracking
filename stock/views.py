from datetime import timedelta, timezone
from django.db import IntegrityError
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import date

from django.shortcuts import render
from .models import Product, StockTransactions
from .tables import StockTransactionsTable
from datetime import datetime, date

from django.shortcuts import render
from .models import Product, StockTransactions
from .tables import StockTransactionsTable
from datetime import datetime, date

# views.py

from django.shortcuts import render
from .models import Product, StockTransactions
from .tables import StockTransactionsTable
from datetime import datetime, date

from .models import Bill, BillItem, Category, OutgoingBill, OutgoingReasons, Product, Seller, StockTransactions, Unit

from .forms import CategoryForm, ProductForm, SellerForm, UnitForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
def payment_bill(request,id):
    pass
def payment(request, id):
    seller = get_object_or_404(Seller, id=id)
    
    if request.method == 'POST':
        payment_amount = request.POST.get("payment_amount")
        try:
            if payment_amount:
                payment_amount_decimal = Decimal(payment_amount)
                if payment_amount_decimal > 0:  # Check if payment is positive
                    seller.receivable += payment_amount_decimal
                    seller.balance = seller.debt - seller.receivable
                    seller.save()
                    messages.success(request, 'Payment successfully added.')
                else:
                    messages.error(request, 'Payment amount must be a positive number.')
            else:
                messages.error(request, 'Payment amount cannot be empty.')
        except InvalidOperation:
            messages.error(request, 'Invalid payment amount format.')

        # Redirect to seller detail page in all cases after processing
        return redirect('satici_sayfasi', id=id)

    # Render the payment form for GET requests
    return render(request, 'payment_form.html', {'seller': seller})
def seller_detail(request, id):
    seller = get_object_or_404(Seller, id=id)
    seller_bills = Bill.objects.filter(seller=seller).order_by('-date')

    # Sayfalama için Paginator objesi oluştur
    paginator = Paginator(seller_bills, 10)  # Sayfa başına 10 öğe

    page_number = request.GET.get('page')
    try:
        seller_bills = paginator.page(page_number)
    except PageNotAnInteger:
        # Sayfa numarası bir tamsayı değilse, ilk sayfayı göster
        seller_bills = paginator.page(1)
    except EmptyPage:
        # Sayfa numarası geçerli değilse, son sayfayı göster
        seller_bills = paginator.page(paginator.num_pages)

    context = {
        'seller': seller,
        'seller_bills': seller_bills,
    }

    return render(request, 'seller_page.html', context)
def dashboard(request):
    products = Product.objects.all()
    products_count = products.count()
    sellers = Seller.objects.all()
    bill_count = Bill.objects.count()
    outgoing_count = OutgoingBill.objects.count()
    last_bill = Bill.objects.all().last()
    # Stokları en düşük olan 5 ürünü al
    products_with_min_stock = Product.objects.order_by('current_stock')[:5]
    product_names = [product.name for product in products_with_min_stock]
    product_stocks = [product.current_stock for product in products_with_min_stock]

    # Her kategoride kaç ürün var
    categories = Category.objects.all()
    category_names = [category.name for category in categories]
    category_counts = [category.product_set.count() for category in categories]
    print(category_counts)
    context = {
        'sellers':sellers,
        'last_bill':last_bill,
        'outgoing_count': outgoing_count,
        'bill_count': bill_count,
        'products_count': products_count,
        'products': products,
        'product_names': product_names,
        'product_stocks': product_stocks,
        'category_names': category_names,
        'category_counts': category_counts,
    }

    return render(request, 'dashboard.html', context)
def stock_by_category(request):
    categories = Category.objects.all()
    products_by_category = {category: Product.objects.filter(category=category) for category in categories}
    context = {
        'products_by_category': products_by_category
    }
    return render(request, 'reports/stock_by_category.html', context)
import openpyxl
from django.http import HttpResponse
from django.urls import path, reverse
def download_excel(request):
    # Bellekte bir çalışma kitabı oluşturun
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ürün Verileri"

    # Tüm kategorileri alın
    categories = Category.objects.all()

    # Kategori ID'leri ve isimlerini üst satırlara ekleyin
    ws.append(["Kategori ID'leri ve İsimleri"])
    for category in categories:
        ws.append([f"ID: {category.id} - İsim: {category.name}"])
    ws.append([])  # Boş bir satır ekleyin

    # Üstte 6 satır boşluk bırakın
    for _ in range(4):  # 4 satır, çünkü 2 satır zaten kategori için kullanıldı
        ws.append([])

    # Başlıkları 7. satırdan itibaren ekleyin
    headers = ["Ürün Adı", "Ürün Kodu", "Birim", "Kategori ID", "Kritik Stok Seviyesi", "Mevcut Stok", "Negatif Stoku Önle"]
    ws.append(headers)

    # Yanıt başlıklarını ayarlayın
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=urun_sablonu.xlsx'

    # Çalışma kitabını yanıt olarak kaydedin
    wb.save(response)

    return response
def change_unit_status(request,unit_id):
    if not request.method == "POST":
        messages.add_message(request, messages.INFO, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    unit = get_object_or_404(Unit,id=unit_id)
    if unit.is_active == True:
        unit.is_active = False
        unit.save()
    else:
        unit.is_active = True
        unit.save()
    messages.add_message(request, messages.SUCCESS, "İşlem Gerçekleşmedi")
    return redirect(request.META.get('HTTP_REFERER', '/'))
def import_excel(request):
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'import_excel.html', context)
from django.contrib import messages
def create_unit_page(request):
    units = Unit.objects.all()
    context = {
        'units':units,
    }
    return render(request,'definitions/define_unit.html',context)
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
from django.core.exceptions import ObjectDoesNotExist
def create_outgoing_reasons(request):
    if request.method != "POST":
        messages.add_message(request, messages.INFO, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    outgoing_reasons_name = request.POST.get("outgoing_reason")
    
    # Check if the outgoing reason already exists
    try:
        exists_reason = OutgoingReasons.objects.get(name=outgoing_reasons_name)
        messages.add_message(request, messages.INFO, "Aynı İsimde Bir Çıkış Nedeni Bulunuyor")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    except ObjectDoesNotExist:
        pass  # This means the reason does not exist, so we can proceed to create it
    
    # Create the new outgoing reason
    cikis_nedeni = OutgoingReasons.objects.create(name=outgoing_reasons_name)
    cikis_nedeni.save()
    
    messages.add_message(request, messages.SUCCESS, f"{cikis_nedeni.name} adlı stok çıkış nedeni oluşturuldu")
    return redirect(request.META.get('HTTP_REFERER', '/'))
def change_active_status(request, id):
    selected_reason = get_object_or_404(OutgoingReasons, id=id)
    selected_reason.is_active = not selected_reason.is_active
    selected_reason.save()
    
    messages.add_message(request, messages.SUCCESS, f"'{selected_reason.name}' çıkış nedeni {'Aktif' if selected_reason.is_active else 'Pasif'}")
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
def create_category_page(request):
    categories = Category.objects.all()
    context = {
        'categories':categories,
    }
    return render(request,'definitions/define_category.html',context)
def change_category_status(request,id):
    if not request.method == "POST":
        messages.add_message(request, messages.INFO, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    category = get_object_or_404(Category,id=id)
    if category.is_active == True:
        category.is_active = False
    else:
        category.is_active = True
    category.save()
    messages.add_message(request, messages.SUCCESS, f"{category.name} Durumu Değiştirildi")
    return redirect(request.META.get('HTTP_REFERER', '/'))

def create_category(request):
    if request.method != "POST":
        messages.add_message(request, messages.INFO, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    category_name = request.POST.get("category_name")
    if Category.objects.filter(name=category_name).exists():
        messages.add_message(request, messages.WARNING, "Bu isimde bir kategori zaten mevcut")
    else:
        Category.objects.create(name=category_name)
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
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Seller, Product, Bill, BillItem, StockTransactions
from decimal import Decimal, ROUND_DOWN
def add_bill(request):
    sellers = Seller.objects.all()
    products = Product.objects.all()

    if request.method == "POST":
        try:
            # Form verilerini al
            bill_number = request.POST.get("bill_number")
            bill_expiry_date = request.POST.get("bill_expiry_date")
            bill_seller_id = request.POST.get("bill_seller")
            bill_item_product_id = request.POST.get("bill_item_product")
            bill_item_quantity = request.POST.get("bill_item_quantity", '0').replace(',', '.')
            bill_item_price = request.POST.get("bill_item_price", '0').replace(',', '.')
            bill_item_discount_1 = request.POST.get("bill_item_discount_1", '0').replace(',', '.')
            bill_item_discount_2 = request.POST.get("bill_item_discount_2", '0').replace(',', '.')
            bill_item_discount_3 = request.POST.get("bill_item_discount_3", '0').replace(',', '.')
            bill_item_vat = request.POST.get("bill_item_vat", '0').replace(',', '.')
            
            if not bill_number:
                raise ValueError("Fatura numarası gerekli.")
            if not bill_expiry_date:
                raise ValueError("Fatura son kullanma tarihi gerekli.")
            if not bill_seller_id:
                raise ValueError("Satıcı seçimi gerekli.")
            if not bill_item_product_id:
                raise ValueError("Ürün seçimi gerekli.")

            bill_seller_id = int(bill_seller_id)
            bill_item_product_id = int(bill_item_product_id)
            bill_item_quantity = Decimal(bill_item_quantity)
            bill_item_price = Decimal(bill_item_price)
            bill_item_discount_1 = Decimal(bill_item_discount_1)
            bill_item_discount_2 = Decimal(bill_item_discount_2)
            bill_item_discount_3 = Decimal(bill_item_discount_3)
            bill_item_vat = Decimal(bill_item_vat)

            # Satıcıyı ve faturayı al veya oluştur
            bill_seller = get_object_or_404(Seller, id=bill_seller_id)
            bill = Bill.objects.create(
                number=bill_number,
                expiry_date=bill_expiry_date,
                seller=bill_seller
            )
            
            # Ürünü ve fatura kalemini al veya oluştur
            product = get_object_or_404(Product, id=bill_item_product_id)
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

            # İndirimler ve KDV ile toplam tutarı hesapla
            total_amount = bill_item_quantity * bill_item_price
            final_price = total_amount
            for discount in [bill_item_discount_1, bill_item_discount_2, bill_item_discount_3]:
                final_price -= final_price * (discount / Decimal(100))

            # Fatura nesnesine toplam tutarı kaydet
            bill.total_amount = final_price.quantize(Decimal('0.000'), rounding=ROUND_DOWN)
            bill.save()

            # Ürünün mevcut stokunu güncelle
            product.current_stock += bill_item_quantity
            product.save()

            # Stok işlemi oluştur veya güncelle
            stock, created = StockTransactions.objects.get_or_create(
                product=product,
                incoming_bill=bill,
                defaults={
                    'incoming_quantity': bill_item_quantity,
                    'processing_time': timezone.now(),
                    'current_stock': product.current_stock
                }
            )
            if not created:
                stock.incoming_quantity += bill_item_quantity
                stock.save()

            # Satıcının alacaklısını güncelle
            bill_seller.receivable = Decimal(bill_seller.receivable or '0') + bill.total_amount
            bill_seller.save()

            messages.success(request, "Fatura ve Kalemler Başarıyla Oluşturuldu")
            return redirect('fatura_detay', bill_number=bill.number)

        except (Seller.DoesNotExist, Product.DoesNotExist):
            messages.error(request, "Fatura Oluşturulamadı. Satıcı veya Ürün bulunamadı.")
        except InvalidOperation as e:
            messages.error(request, f"Veri hatası: {str(e)}")
        except ValueError as e:
            messages.error(request, str(e))
        except Exception as e:
            messages.error(request, f"Fatura Oluşturulamadı. Hata: {str(e)}")

        return redirect(request.META.get('HTTP_REFERER', '/'))

    context = {
        'products': products,
        'sellers': sellers,
    }
    return render(request, 'add_bill.html', context)

def product_info(request):
    products = Product.objects.all()
    context = {
        'products':products,
    }
    return render(request,'reports/product_info.html',context)
def bill_details(request, bill_number):
    products = Product.objects.all()
    
    try:
        # First try to get the Bill object with the given bill_number
        bill = get_object_or_404(Bill, number=bill_number)
        bill_items = BillItem.objects.filter(bill=bill)
    except Http404:
        # If Bill with bill_number is not found, try to get StockTransactions with the bill_number
        stock_transaction = get_object_or_404(OutgoingBill, number=bill_number)
        bill_items = None  # Adjust as per your requirement for StockTransactions
        
        context = {
            'products': products,
            'stock_transaction': stock_transaction,
            'bill_items': bill_items,
        }
        return render(request, 'bill_details.html', context)

    context = {
        'products': products,
        'bill': bill,
        'bill_items': bill_items,
    }
    return render(request, 'bill_details.html', context)
from collections import defaultdict

def bills(request):
    bills = Bill.objects.all()
    bills_by_seller = defaultdict(list)
    
    for bill in bills:
        bills_by_seller[bill.seller].append(bill)
    
    context = {
        'bills_by_seller': dict(bills_by_seller),
    }
    return render(request, 'bills.html', context)
from django.db import transaction, IntegrityError
from django.db import transaction
from django.db.models import Sum, F
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from decimal import Decimal
from .models import BillItem, Product, Bill
def delete_bill(request, bill_id):
    if request.method != "POST":
        messages.error(request, 'Bu istekler kabul edilmez.')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    bill = get_object_or_404(Bill, id=bill_id)
    
    # Bill'i silinmiş olarak işaretle
    bill.is_delete = True
    bill.save()
    
    # İlgili BillItem'leri al ve stok miktarlarını güncelle
    bill_items = BillItem.objects.filter(bill=bill)
    for bill_item in bill_items:
        stock_transactions = StockTransactions.objects.filter(product=bill_item.product, incoming_bill=bill)
        for transaction in stock_transactions:
            if transaction.incoming_quantity:
                transaction.product.current_stock -= bill_item.quantity
                transaction.incoming_quantity -= bill_item.quantity
            transaction.save()
        
        # BillItem'i silinmiş olarak işaretle
        bill_item.is_delete = True
        bill_item.save()

    # Başarı mesajı göster
    messages.success(request, 'Fatura başarıyla silindi olarak işaretlendi.')
    
    # Kullanıcıyı belirli bir sayfaya yönlendir
    return redirect('your-desired-view-name')  # yönlendirilmek istenen view'in adını kullanın
    
def deleted_bills(request):
    deleted_bills = Bill.objects.filter(is_delete=True)
    bill_items = {bill.id: BillItem.objects.filter(bill=bill, is_delete=True) for bill in deleted_bills}
    context = {
        'deleted_bills': deleted_bills,
        'bill_items': bill_items,
    }
    return render(request, 'deleted_bills.html', context)
def add_billitem(request, bill_id):
    if request.method != "POST":
        return JsonResponse({'error': 'POST method expected.'}, status=400)

    bill = get_object_or_404(Bill, id=bill_id)
    if bill.is_paid:
            return JsonResponse({'error': 'Bu fatura ödenmiş ve yeni kalem eklenemez!'}, status=400)
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
        return JsonResponse({'error': 'Invalid number format.'}, status=400)

    try:
        with transaction.atomic():
            item_total = bill_item_quantity * bill_item_price

            # BillItem oluştur
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

            # Product'un mevcut stoğunu güncelle
            Product.objects.filter(id=product.id).update(current_stock=F('current_stock') + bill_item_quantity)

            # Fatura toplam tutarını güncelle
            bill.total_amount += item_total
            bill.save()

        return JsonResponse({
            "bill_item_product": product.name,
            "bill_item_quantity": f"{bill_item_quantity:.2f}",
            "bill_item_price": f"{bill_item_price:.2f}",
            "bill_item_discount_1": f"{bill_item_discount_1:.2f}",
            "bill_item_discount_2": f"{bill_item_discount_2:.2f}",
            "bill_item_discount_3": f"{bill_item_discount_3:.2f}",
            "bill_item_vat": f"{bill_item_vat:.2f}",
            "new_total_amount": f"{bill.total_amount:.2f}",
        })

    except IntegrityError as e:
        return JsonResponse({'error': str(e)}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
from datetime import datetime
def stock_difference_report(request):
    # Tüm ürünleri al
    products = Product.objects.all()

    # Her ürün için giren ve çıkan miktarları hesapla
    product_reports = []
    for product in products:
        total_incoming = StockTransactions.objects.filter(product=product).aggregate(Sum('incoming_quantity'))['incoming_quantity__sum'] or 0
        total_outgoing = StockTransactions.objects.filter(product=product).aggregate(Sum('outgoing_quantity'))['outgoing_quantity__sum'] or 0
        real_stock = total_incoming - total_outgoing
        visible_stock = product.current_stock
        product_reports.append({
            'name': product.name,
            'total_incoming': total_incoming,
            'total_outgoing': total_outgoing,
            'real_stock': real_stock,
            'current_stock': product.current_stock,
            'visible_stock':visible_stock,   # Product modelindeki current_stock'u rapora ekle
        })
         # visible_stock listesine current_stock değerini ekle

    # Raporu template'e gönder
    context = {
        'today': timezone.now(),
        'products': product_reports,
    }
    return render(request, 'reports/stock_difference_report.html', context)
def stock_status(request):
    
    stock_transactions = StockTransactions.objects.select_related('product', 'incoming_bill', 'outgoing_reasons').all()

    incoming_quantities = {}
    outgoing_quantities = {}

    for stock in stock_transactions:
        incoming_quantity = stock.incoming_quantity or 0
        outgoing_quantity = stock.outgoing_quantity or 0

        # Accumulate incoming quantities
        if stock.product_id in incoming_quantities:
            incoming_quantities[stock.product_id] += incoming_quantity
        else:
            incoming_quantities[stock.product_id] = incoming_quantity

        # Accumulate outgoing quantities
        if stock.product_id in outgoing_quantities:
            outgoing_quantities[stock.product_id] += outgoing_quantity
        else:
            outgoing_quantities[stock.product_id] = outgoing_quantity

    products = Product.objects.all()
    product_data = []

    for product in products:
        incoming_quantity = incoming_quantities.get(product.id, 0)
        outgoing_quantity = outgoing_quantities.get(product.id, 0)
        current_stock = product.current_stock

        product_data.append({
            'id': product.id,
            'name': product.name,
            'total_incoming': incoming_quantity,
            'total_outgoing': outgoing_quantity,
            'current_stock': current_stock
        })

    today = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

    context = {
        'products': product_data,
        'today': today,
    }

    return render(request, 'stock_status_report.html', context)

def incoming_outgoing_reports(request):
    products = Product.objects.all()

    if request.method != "POST":
        # Get today's date
        today = date.today()

        # Filter stock_transactions for today
        stock_transactions = StockTransactions.objects.filter(
            processing_time__date=today
        )
        table = StockTransactionsTable(stock_transactions)

        context = {
            'table': table,
            'products': products,
            'start_date': today,
            'end_date': today,
        }

        return render(request, 'reports/incoming_outgoing_reports.html', context)

    # Get start_date and end_date from POST request
    start_date_str = request.POST.get("start_date")
    end_date_str = request.POST.get("end_date")

    # Use today's date if either start_date or end_date is empty
    today = date.today()
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else today
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else today

    # Make sure end_date is at the end of the day
    end_date = datetime.combine(end_date, datetime.max.time())

    stock_transactions = StockTransactions.objects.filter(
        processing_time__range=(start_date, end_date)
    )
    table = StockTransactionsTable(stock_transactions)

    context = {
        'table': table,
        'products': products,
        'start_date': start_date,
        'end_date': end_date,
    }
    print('Bitiş Tarihi',end_date)
    return render(request, 'reports/incoming_outgoing_reports.html', context)

def get_stock_transactions(product_id):
    return StockTransactions.objects.filter(product=product_id).order_by('-processing_time')

def due_date_reports(request):

    
    expiry_date = request.POST.get('expiry_date') or request.GET.get('expiry_date')
    today = datetime.now()
    print('Bugün ',today)
    print(expiry_date)
    # Filter Bill objects based on the expiry date
    reports_bill = Bill.objects.filter(expiry_date=expiry_date, is_paid=False)
    paid_bills = Bill.objects.filter(expiry_date=expiry_date, is_paid=True)
    print("Reports Bill:", reports_bill, paid_bills)

    # Pass the filtered Bill objects to the context
    context = {
        'today':today,
        'expiry_date':expiry_date,
        'paid_bills': paid_bills,
        'reports_bill': reports_bill,
    }
    return render(request, 'reports/expiry_date_reports.html', context)

def paid_bill(request, id):
    if not request.method == "POST":
        messages.error(request, 'Ürün Seçilmedi')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    bill = get_object_or_404(Bill, id=id)
    expiry_date = bill.expiry_date  # Get the expiry date before saving
    bill.is_paid = True
    bill.save()
    messages.success(request, 'Fatura Ödendi')
    return redirect(f'{reverse("vade_tarihi_gelen_faturalar")}?expiry_date={expiry_date}')

def unpaid_bill(request, id):
    if not request.method == "POST":
        messages.error(request, 'Ürün Seçilmedi')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    bill = get_object_or_404(Bill, id=id)
    expiry_date = bill.expiry_date  # Get the expiry date before saving
    bill.is_paid = False
    bill.save()
    messages.success(request, 'Fatura Ödemesi Geri Alındı')
    return redirect(f'{reverse("vade_tarihi_gelen_faturalar")}?expiry_date={expiry_date}')
def stock_transactions(request):
    products = Product.objects.all()
    if request.method == "POST":
        selected_product = request.POST.get('selected_product')
        if not selected_product:
            messages.error(request, 'Ürün Seçilmedi')
            return redirect('stok_hareketleri')
        
        product = get_object_or_404(Product, id=selected_product)
        stock_transactions = get_stock_transactions(product.id)
        
        context = {
            'products': products,
            'product': product,
            'stock_transactions': stock_transactions,
        }
    else:
        context = {
            'products': products,
        }
    
    return render(request, 'reports/product_transactions.html', context)

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
        if StockTransactions.objects.filter(outgoing_bill__number=outgoing_bill_number).exists():
            messages.error(request, 'Bill number already exists.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        outgoing_product = Product.objects.get(id=outgoing_product_id)
        outgoing_reason = OutgoingReasons.objects.get(id=outgoing_reason_id)

        # Ensure outgoing_quantity is a valid Decimal and handle the conversion
        outgoing_quantity = Decimal(outgoing_quantity)
        
        # Check if stock can go negative
        if outgoing_product.prevent_stock_negative and outgoing_product.current_stock < outgoing_quantity:
            messages.error(request, 'Bu üründe stok eksiye (-) düşemez.')
            return redirect(request.META.get('HTTP_REFERER', '/'))

        outgoing_product.current_stock -= outgoing_quantity
        outgoing_product.save()
        print('Çıkan Tutar',outgoing_quantity)
        outgoing_bill = OutgoingBill.objects.create(
            number=outgoing_bill_number,
            product=outgoing_product,
            quantity=outgoing_quantity,
            outgoing_reason=outgoing_reason,
            processing_time=timezone.now(),
        )
        
        stock_outgoing = StockTransactions.objects.create(
            product=outgoing_product,
            outgoing_quantity=outgoing_quantity,
            outgoing_reasons=outgoing_reason,
            outgoing_bill=outgoing_bill,
            processing_time=timezone.now(),
            current_stock=outgoing_product.current_stock,
        )
        
        messages.success(request, 'Stok Çıkışı Yapıldı')
    except Product.DoesNotExist:
        messages.error(request, 'Ürün Bulunamadı')
    except OutgoingReasons.DoesNotExist:
        messages.error(request, 'Çıkış Sebebi Bulunamadı')
    except InvalidOperation as e:
        messages.error(request, f"Bilinmeyen miktar: {str(e)}")
    except Exception as e:
        messages.error(request, f'Bir Hata Oluştu: {str(e)}')
        print(e)

    return redirect(request.META.get('HTTP_REFERER', '/'))