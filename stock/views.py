from datetime import timedelta, timezone
import random
from django.db import IntegrityError
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import date

from django.shortcuts import render
from .models import Company, Parameter, Product, StockTransactions
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

from .forms import CategoryForm, CompanyForm, ParameterForm, ProductForm, SellerForm, UnitForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.crypto import get_random_string
def companies(request):
    if not request.session['company_code'] == 1:
        messages.error(request, 'Bu Yetkiye Sahip Değilsiniz.')
        return redirect('dashboard',request.session['company_code'])
    request.session['company_code'] = 1
    companies = Company.objects.all()
    context = {
        'companies':companies,
    }
    return render(request,'companies.html',context)
def generate_unique_code():
    """Generate a unique 9-digit code."""
    return str(random.randint(100000000, 999999999))
def parameter(request, code):
    company = get_object_or_404(Company, code=code)
    parameters = Parameter.objects.filter(company=company)

    # İlk parametreyi al veya yeni bir tane oluştur
    if parameters.exists():
        parameter = parameters.first()
    else:
        parameter = Parameter(company=company)

    if request.method == 'POST':
        form = ParameterForm(request.POST, instance=parameter)
        if form.is_valid():
            form.save()
            return redirect('parameter', code=code)  # Kendi view'ınıza göre güncelleyin
    else:
        form = ParameterForm(instance=parameter)

    context = {
        'form': form,
        'company': company,
    }
    return render(request, 'parameter.html', context)
def edit_parameter(request, company_code, parameter_id):
    company = get_object_or_404(Company, code=company_code)
    parameter, created = Parameter.objects.get_or_create(id=parameter_id, company=company)

    if request.method == 'POST':
        form = ParameterForm(request.POST, instance=parameter)
        if form.is_valid():
            form.save()
            return redirect('company_parameters', company_code=company_code)
    else:
        form = ParameterForm(instance=parameter)

    return render(request, 'edit_parameter.html', {'company': company, 'form': form})
def create_company(request,code):
    company = get_object_or_404(Company,code=code)
    if not company.code == 1:
        messages.error(request, 'Bu Yetkiye Sahip Değilsiniz.')
        return redirect('company_list')
    if request.user.company_code != 1:
        messages.error(request, 'Bu Yetkiye Sahip Değilsiniz.')
        return redirect('company_list')
    
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            # Yeni şirket oluştur
            company = form.save(commit=False)
            # Şirket kodunu oluştur ve ayarla
            company.code = generate_unique_code()
            # Şirketi veritabanına kaydet
            company.save()
            
            # Şirket için varsayılan parametre oluştur
            default_parameter = Parameter(
                company=company,
                fifo=True  # Varsayılan değer
            )
            default_parameter.save()
            
            return redirect('company_list')  # Başarılı bir şekilde kaydedildikten sonra yönlendirin
    else:
        form = CompanyForm()
    
    return render(request, 'definitions/define_company.html', {'form': form,
                                                               'company':company,})

def generate_unique_code():
    # 9 haneli benzersiz bir kod oluştur
    return get_random_string(length=9, allowed_chars='1234567890')
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
def seller_detail(request, id ,code):
    company = get_object_or_404(Company,code=code)
    seller = get_object_or_404(Seller, id=id,company=company)
    seller_bills = Bill.objects.filter(seller=seller,company=company).order_by('-date')

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
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        company_code = request.POST.get('company_code')

        company = get_object_or_404(Company, code=company_code)
        user = authenticate(request, username=username, password=password)

        if user is not None:
            print(user)
            # Kullanıcının bu firmaya ait olup olmadığını kontrol et
            if user.company == company or (user.company.code == 1 and user.username == "ssoft"):
                login(request, user)
                request.session['company_code'] = company.code
                return redirect('dashboard', request.session['company_code'])  # Girişten sonra yönlendirilmek istenen sayfa
            else:
                messages.error(request, "Bu kullanıcı bu firmaya ait değil.")
        else:
            messages.error(request, "Geçersiz kullanıcı adı veya şifre.")
    
    return render(request, 'login.html')
def dashboard(request, code):
    try:
        company = get_object_or_404(Company, code=code)
    except:
        messages.error(request, 'Böyle bir şirket yok')
        return redirect('dashboard', request.session['company_code'])  # Girişten sonra yönlendirilmek istenen sayfa

    products = Product.objects.filter(company=company)
    products_count = products.count()
    sellers = Seller.objects.filter(company=company)
    bill_count = Bill.objects.filter(company=company).count()
    outgoing_count = OutgoingBill.objects.filter(company=company).count()
    last_bill = Bill.objects.filter(company=company).last()

    # Stokları en düşük olan 5 ürünü al
    products_with_min_stock = Product.objects.filter(company=company).order_by('current_stock')[:5]
    product_names = [product.name for product in products_with_min_stock]
    product_stocks = [product.current_stock for product in products_with_min_stock]

    # Her kategoride kaç ürün var
    categories = Category.objects.filter(company=company)
    category_names = [category.name for category in categories]
    category_counts = [category.product_set.count() for category in categories]

    context = {
        'company': company,
        'sellers': sellers,
        'last_bill': last_bill,
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
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            selected_company = form.cleaned_data.get('company').first()  # İlk şirketi al
            if selected_company:
                user.company_code = selected_company.code  # Şirket kodunu ayarla
            user.save()
            form.save_m2m()  # Many-to-many ilişkilerini kaydeder
            login(request, user)
            return redirect('home')  # Başarı sayfasına veya kullanıcının profil sayfasına yönlendirme yapabilirsiniz
    else:
        form = CustomUserCreationForm()
    return render(request, 'definitions/define_user.html', {'form': form})
def stock_by_category(request, code):
    # Şirketi al
    company = get_object_or_404(Company, code=code)
    
    # Kullanıcının kullanıcı adı, şirket kodu ve tag'i kontrol et
    user_is_ssoft = request.user.username == 'ssoft'
    user_is_company_owner = request.user.company.code == company.code
    # user_is_support_tag = request.user.tag == 'Destek'
    user_company_code_is_one = request.user.company.code == 1

    if not user_is_ssoft and not (user_is_company_owner or (user_company_code_is_one)): #user_is_support_tag eklennicek
        messages.info(request, 'Kendi firmanıza yönlendirildiniz.')
        return redirect('dashboard', request.user.company.code)
    
    # Kategoriler ve ürünleri al
    categories = Category.objects.filter(company=company)
    products_by_category = {category: Product.objects.filter(category=category, company=company) for category in categories}
    
    # Context oluştur
    context = {
        'company': company,
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
def change_unit_status(request, unit_id):
    if request.method != "POST":
        messages.add_message(request, messages.INFO, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    unit = get_object_or_404(Unit, id=unit_id)

    # Kullanıcının ait olduğu şirketi al
    user_company = request.user.company

    # Unit'in ait olduğu şirketi kontrol et
    if unit.company != user_company:
        messages.add_message(request, messages.ERROR, "Bu birime işlem yapma yetkiniz yok.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Unit'in aktiflik durumunu değiştir
    if unit.is_active:
        unit.is_active = False
    else:
        unit.is_active = True
    
    unit.save()
    messages.add_message(request, messages.SUCCESS, "İşlem başarıyla gerçekleştirildi.")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))
def import_excel(request):
    categories = Category.objects.all()
    context = {
        'categories': categories
    }
    return render(request, 'import_excel.html', context)
from django.contrib import messages
def create_unit_page(request,code):
    company = get_object_or_404(Company,code=code)
    units = Unit.objects.filter(company=company)
    context = {
        'company':company,
        'units':units,
    }
    return render(request,'definitions/define_unit.html',context)
def create_unit(request,code):
    if request.method != "POST":
        messages.info(request, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    unit_name = request.POST.get("unit_name")
    if not unit_name:
        messages.info(request, "Birim Adı Boş Olamaz")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    
    company = get_object_or_404(Company, code=code)

    if request.user.company != company:
        messages.error(request, "Bu şirkette işlem yapamazsınız")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if Unit.objects.filter(unit_name=unit_name, company=company).exists():
        messages.info(request, "Birim Adı Zaten Kayıtlı")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    Unit.objects.create(company=company, unit_name=unit_name)
    messages.success(request, "Kayıt Gerçekleşti")
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
def create_outgoing_reasons_page(request,code):
    try:
        company=get_object_or_404(Company,code=code)
    except:
        messages.add_message(request, messages.ERROR, "Firma bulunamadı")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    reasons = OutgoingReasons.objects.filter(company=company)
    context = {
        'company':company,
        'reasons':reasons,
    }
    return render(request,'definitions/define_outgoing.html',context)
from django.core.exceptions import ObjectDoesNotExist
def create_outgoing_reasons(request, code):
    if request.method != "POST":
        messages.info(request, "İşlem Gerçekleşmedi")
        return redirect('cikis_tanimlama_sayfasi',request.user.company.code)  # 'your_redirect_url' yerine uygun bir URL adı koyun

    outgoing_reasons_name = request.POST.get("outgoing_reason")
    
    company = get_object_or_404(Company, code=code)
    
    # Çıkış nedeninin mevcut olup olmadığını kontrol et
    if OutgoingReasons.objects.filter(name=outgoing_reasons_name, company=company).exists():
        messages.info(request, "Aynı İsimde Bir Çıkış Nedeni Bulunuyor")
        return redirect('cikis_tanimlama_sayfasi',request.user.company.code)  # 'your_redirect_url' yerine uygun bir URL adı koyun
    
    # Yeni çıkış nedenini oluştur
    cikis_nedeni = OutgoingReasons.objects.create(
        company=company,
        name=outgoing_reasons_name
    )
    
    messages.success(request, f"{cikis_nedeni.name} adlı stok çıkış nedeni oluşturuldu")
    return redirect('cikis_tanimlama_sayfasi',request.user.company.code)  # 'your_redirect_url' yerine uygun bir URL adı koyun
def change_active_status(request, id):
    selected_reason = get_object_or_404(OutgoingReasons, id=id)
    selected_reason.is_active = not selected_reason.is_active
    selected_reason.save()
    
    messages.add_message(request, messages.SUCCESS, f"'{selected_reason.name}' çıkış nedeni {'Aktif' if selected_reason.is_active else 'Pasif'}")
    return redirect(request.META.get('HTTP_REFERER', '/'))
def create_seller(request, code):
    company = get_object_or_404(Company, code=code)
    
    if request.method != "POST":
        sellers = Seller.objects.all()
        context = {
            'sellers': sellers,
            'company': company
        }
        return render(request, 'definitions/define_seller.html', context)
    
    seller_name = request.POST.get("seller_name")
    seller_address = request.POST.get("seller_address")
    
    Seller.objects.create(
        company=company,
        name=seller_name,
        address=seller_address
    )
    
    messages.success(request, "Cari Oluşturuldu")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))
def create_category_page(request,code):
    company = get_object_or_404(Company,code=code)
    categories = Category.objects.all()
    context = {
        'company':company,
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


def create_category(request, code):
    if request.method != "POST":
        messages.info(request, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    company = get_object_or_404(Company, code=code)

    # Kullanıcının şirkete ait olup olmadığını kontrol et ve özel kullanıcıya izin ver
    if request.user.company != company and not (request.user.company.code == 1 and request.user.username == "ssoft"):
        messages.error(request, "Bu şirkette işlem yapamazsınız")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    category_name = request.POST.get("category_name")

    if not category_name:
        messages.warning(request, "Kategori ismi boş olamaz")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if Category.objects.filter(name=category_name, company=company).exists():
        messages.warning(request, "Bu isimde bir kategori zaten mevcut")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    Category.objects.create(company=company, name=category_name)
    messages.success(request, "Kategori Oluşturuldu")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))
def product_add_page(request,code):
    company = get_object_or_404(Company,code=code)
    units = Unit.objects.filter(company=company)
    categories = Category.objects.filter(company=company)
    products = Product.objects.filter(company=company)
    
    context = {
        'company':company,
        'categories': categories,
        'units': units,
        'products': products
    }
    
    return render(request, 'definitions/define_product.html', context)
def create_product(request,code):

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
    company = get_object_or_404(Company,code=code)
    Product.objects.create(
        company=company,
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
def add_bill(request,code):
    company = get_object_or_404(Company,code=code)
    print('Bulunan Şirket')
    sellers = Seller.objects.all()
    products = Product.objects.all()

    if request.method != "POST":
        context = {
            'company':company,
            'products': products,
            'sellers': sellers,
        }
        return render(request, 'add_bill.html', context)

    try:
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

        # Gerekli alanların kontrolü
        if not bill_number:
            raise ValueError("Fatura numarası gerekli.")
        if not bill_expiry_date:
            raise ValueError("Fatura son kullanma tarihi gerekli.")
        if not bill_seller_id:
            raise ValueError("Satıcı seçimi gerekli.")
        if not bill_item_product_id:
            raise ValueError("Ürün seçimi gerekli.")

        # Dönüşümler ve doğrulamalar
        bill_seller_id = int(bill_seller_id)
        bill_item_product_id = int(bill_item_product_id)
        bill_item_quantity = Decimal(bill_item_quantity)
        bill_item_price = Decimal(bill_item_price)
        bill_item_discount_1 = Decimal(bill_item_discount_1)
        bill_item_discount_2 = Decimal(bill_item_discount_2)
        bill_item_discount_3 = Decimal(bill_item_discount_3)
        bill_item_vat = Decimal(bill_item_vat)

        # Satıcı ve ürünü al
        bill_seller = get_object_or_404(Seller, id=bill_seller_id)
        product = get_object_or_404(Product, id=bill_item_product_id)

        # Fatura oluştur
        bill = Bill.objects.create(
            company=company,
            number=bill_number,
            expiry_date=bill_expiry_date,
            seller=bill_seller
        )

        # Fatura kalemi oluştur
        bill_item = BillItem.objects.create(
            company=company,
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

        # Faturaya toplam tutarı kaydet
        bill.total_amount = final_price.quantize(Decimal('0.000'), rounding=ROUND_DOWN)
        bill.save()

        # Ürünün mevcut stokunu güncelle
        product.current_stock += bill_item_quantity
        product.save()

        # Stok işlemi oluştur veya güncelle
        stock, created = StockTransactions.objects.get_or_create(
            product=product,
            company=company,
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


        
from itertools import groupby
from operator import itemgetter
from django.shortcuts import render
from .models import OutgoingBill
def outgoing_bills(request):
    selected_reasons = request.GET.getlist('reasons')
    all_reasons = OutgoingReasons.objects.all()
    
    if selected_reasons:
        bills = OutgoingBill.objects.filter(outgoing_reasons__id__in=selected_reasons)
    else:
        bills = OutgoingBill.objects.all()
    
    context = {
        'bills': bills,
        'all_reasons': all_reasons,
        'selected_reasons': [int(reason) for reason in selected_reasons],
    }
    return render(request, 'reports/outgoing_bills.html', context)
def product_info(request,code):
    company = get_object_or_404(Company,code=code)
    products = Product.objects.filter(company=company)
    context = {
        'company':company,
        'products':products,
    }
    return render(request,'reports/product_info.html',context)
def bill_details(request, bill_number):
    products = Product.objects.all()
    
    try:
        bill = get_object_or_404(Bill, number=bill_number)
        bill_items = BillItem.objects.filter(bill=bill)
    except Http404:
        stock_transaction = get_object_or_404(OutgoingBill, number=bill_number)
        bill_items = None  
        
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

def bills(request,code):
    company = get_object_or_404(Company,code=code)
    bills = Bill.objects.filter(company=company)
    bills_by_seller = defaultdict(list)
    
    for bill in bills:
        bills_by_seller[bill.seller].append(bill)
    
    context = {
        'company':company,
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
def stock_difference_report(request,code):
    # Tüm ürünleri al
    company = get_object_or_404(Company,code=code)
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
        'company':company,
        'today': timezone.now(),
        'products': product_reports,
    }
    return render(request, 'reports/stock_difference_report.html', context)
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db.models import Sum
from .models import Company, Product, StockTransactions

def stock_status(request, code):
    company = get_object_or_404(Company, code=code)
    
    # Sadece geçerli şirketin stok hareketlerini al
    stock_transactions = StockTransactions.objects.filter(product__company=company).select_related('product', 'incoming_bill', 'outgoing_reasons')

    # Stok hareketlerini ürün bazında gruplayarak miktarları topla
    incoming_quantities = stock_transactions.values('product_id').annotate(total_incoming=Sum('incoming_quantity')).order_by()
    outgoing_quantities = stock_transactions.values('product_id').annotate(total_outgoing=Sum('outgoing_quantity')).order_by()

    # Ürünleri ve stok bilgilerini al
    products = Product.objects.filter(company=company)
    product_data = []

    incoming_dict = {item['product_id']: item['total_incoming'] for item in incoming_quantities}
    outgoing_dict = {item['product_id']: item['total_outgoing'] for item in outgoing_quantities}

    for product in products:
        product_data.append({
            'id': product.id,
            'name': product.name,
            'total_incoming': incoming_dict.get(product.id, 0),
            'total_outgoing': outgoing_dict.get(product.id, 0),
            'current_stock': product.current_stock
        })

    today = timezone.now().strftime("%Y-%m-%d %H:%M:%S")

    context = {
        'company':company,
        'products': product_data,
        'today': today,
    }

    return render(request, 'stock_status_report.html', context)


def incoming_outgoing_reports(request,code):
    products = Product.objects.all()
    company = get_object_or_404(Company,code=code)
    if request.method != "POST":
        # Get today's date
        today = date.today()

        # Filter stock_transactions for today
        stock_transactions = StockTransactions.objects.filter(
            processing_time__date=today
        )
        table = StockTransactionsTable(stock_transactions)

        context = {
            'company':company,
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

def due_date_reports(request, code, expiry_date=None):
    company = get_object_or_404(Company, code=code)
    today = datetime.now()

    if request.method == 'POST':
        expiry_date = request.POST.get('expiry_date')
        return redirect('vade_tarihi_gelen_faturalar', code=code, expiry_date=expiry_date)
    
    # Filter Bill objects based on the expiry date
    reports_bill = Bill.objects.filter(expiry_date=expiry_date, is_paid=False, company=company)
    paid_bills = Bill.objects.filter(expiry_date=expiry_date, is_paid=True, company=company)
    
    # Pass the filtered Bill objects to the context
    context = {
        'company': company,
        'today': today,
        'expiry_date': expiry_date,
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
def stock_transactions(request, code):
    company = get_object_or_404(Company, code=code)
    products = Product.objects.filter(company=company)
    
    if request.method == "POST":
        selected_product = request.POST.get('selected_product')
        
        # Check if a valid product is selected
        if not selected_product:
            messages.error(request, 'Ürün Seçilmedi')
            return redirect('stok_hareketleri', code=code)
        
        product = get_object_or_404(Product, id=selected_product, company=company)
        stock_transactions = get_stock_transactions(product.id)
        
        context = {
            'company':company,
            'products': products,
            'product': product,
            'stock_transactions': stock_transactions,
        }
    else:
        context = {
            'company':company,
            'products': products,
        }
    
    return render(request, 'reports/product_transactions.html', context)

def process_stock_outgoing(request,code):
    company = get_object_or_404(Company,code=code)
    products = Product.objects.filter(company=company)
    outgoing_reasons = OutgoingReasons.objects.filter(company=company)
    
    if request.method != "POST":
        context = {
            'company':company,
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
        outgoing_product.company = company
        outgoing_product.save()
        print('Çıkan Tutar',outgoing_quantity)
        outgoing_bill = OutgoingBill.objects.create(
            company=company,
            number=outgoing_bill_number,
            product=outgoing_product,
            quantity=outgoing_quantity,
            outgoing_reason=outgoing_reason,
            processing_time=timezone.now(),
        )
        
        stock_outgoing = StockTransactions.objects.create(
            company=company,
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