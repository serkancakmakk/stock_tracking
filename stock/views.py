from datetime import timedelta, timezone
import random
from django.db import IntegrityError
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import date

from django.shortcuts import render
from .models import Company, Inventory, Parameter, Product, StockTransactions, User
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

from .forms import CategoryForm, CompanyForm, ParameterForm, ProductForm, SellerForm, UnitForm, UserEditForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.crypto import get_random_string
def companies(request,company_code):
    company = get_object_or_404(Company,code=company_code)
    print(request.user.username)
    if not request.user.username == 'ssoft' and request.user.company.code == 1:
        messages.error(request, 'Bu Sayfaya Ulaşamazsınız.')
        return redirect('dashboard', company.code)
    companies = Company.objects.all()

    context = {
        'company':company,
        'companies':companies,
    }
    return render(request,'companies.html',context)
def generate_unique_code():
    """Generate a unique 9-digit code."""
    return str(random.randint(100000000, 999999999))
def parameter(request, code):
    company = get_object_or_404(Company, code=code)
    parameters = Parameter.objects.filter(company=company)
    has_permission, redirect_response = check_user_permissions(request, company)
    if not has_permission:
        return redirect_response
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
def master_create_company(request):
        # Belirtilen değerlerle yeni bir Company kaydı oluştur
        user = User.objects.first()  # Burada, ID'si 1 olan kullanıcıyı alıyoruz, kendi kullanıcı seçiminize göre ayarlayın
        contract_end_date = timezone.now() + timezone.timedelta(days=365)

        Company.objects.create(
            code=1,
            name='Company 1',
            owner='Owner 1',
            address='Address 1',
            phone='111-111-1111',
            city='City 1',
            country='Country 1',
            email='email1@example.com',
            other_info='Other info 1',
            contract_end_date=contract_end_date,
            create_user=user
        )
        return redirect('success_url')  # Başarı URL'si kendi URL'nize göre ayarlayın


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
            company.create_user = request.user
            company.save()
            
            # Şirket için varsayılan parametre oluştur
            # default_parameter = Parameter(
            #     company=company,
            #     fifo=True  # Varsayılan değer
            # )
            # default_parameter.save()
            
            return redirect('firmalar')  # Başarılı bir şekilde kaydedildikten sonra yönlendirin
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
        'company':company,
        'seller': seller,
        'seller_bills': seller_bills,
    }

    return render(request, 'seller_page.html', context)
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
def user_edit(request, code, uuid4):
    company = get_object_or_404(Company, code=code)
    has_permission, redirect_response = check_user_permissions(request, company)
    
    if not has_permission:
        return redirect_response

    user = get_object_or_404(User, unique_id=uuid4)
    if not request.method == 'POST':
        form = UserEditForm(instance=user)
    form = UserEditForm(request.POST, instance=user)
    
    if form.is_valid():
        user = form.save(commit=False)
        user.is_active = 'is_active' in request.POST
        user.save()
        # Başarılı bir şekilde kaydedildiğinde yönlendirme ekleyin
        messages.success(request,'Güncelleme Başarılı')
        return redirect(request.META.get('HTTP_REFERER', '/'))  # success_url'yi kendi başarılı yönlendirme URL'nizle değiştirin
    print(form.errors)
    return render(request, 'user_page/user_detail.html', {'form': form, 'company': company})
def user_login(request):
    if request.method != "POST":
        return render(request, 'login.html')

    username = request.POST.get('username')
    password = request.POST.get('password')
    company_code = request.POST.get('company_code')
    company = get_object_or_404(Company, code=company_code)
    
    try:
        user = User.objects.get(username=username, company=company)
    except User.DoesNotExist:
        messages.error(request, "Geçersiz kullanıcı adı.")
        return render(request, 'login.html')
    
    if not user.check_password(password):
        messages.error(request, "Geçersiz şifre.")
        return render(request, 'login.html')
    
    if user.company != company and not (user.company.code == 1 and user.username == "ssoft"):
        messages.error(request, "Bu kullanıcı bu firmaya ait değil.")
        return render(request, 'login.html')
    
    # Kullanıcıya ait yetkilerin olup olmadığını kontrol et ve yoksa oluştur
    permission, created = Permission.objects.get_or_create(user=user)
    if created:
        # Yeni oluşturulan yetkiler için varsayılan değerler atayabilirsiniz
        permission.add_company = False
        permission.add_user = False
        permission.save()
    
    login(request, user)
    request.session['company_code'] = company.code
    return redirect('dashboard', request.session['company_code'])  # Girişten sonra yönlendirilmek istenen sayfa
def user_detail(request,code,uuid4):
    company = get_object_or_404(Company,code=code)
    user =  get_object_or_404(User,unique_id=uuid4)
    context = {
        'company':company,
        'user':user,
    }
    return render(request,'user_page/user_detail.html',context)
from django.contrib.auth.decorators import login_required

# @login_required
def dashboard(request, code):
    company = get_object_or_404(Company, code=code)
    
    # kullanıcı izinleri kontrol et
    has_permission, redirect_response = check_user_permissions(request, company)
    if not has_permission:
        return redirect_response
    
    # Fetch dashboard data
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

    # If the company code is 1, include all companies
    if company.code == 1:
        companies = Company.objects.all()
        context['companies'] = companies

    return render(request, 'dashboard.html', context)
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .models import Permission

def check_user_permissions(request, company):
    user_is_ssoft = request.user.username == 'ssoft'
    user_is_company_owner = request.user.company.code == company.code
    # user_is_support_tag = request.user.tag == 'Destek'
    user_company_code_is_one = request.user.company.code == 1

    # Master kullanıcı her zaman erişebilir
    if user_is_ssoft:
        return True, None

    # Şirket kodu 1 olan kullanıcılar her firmada işlem yapabilir
    if user_company_code_is_one:
        return True, None
    
    # Kullanıcı kendi firmasına erişebilmeli
    if user_is_company_owner:
        return True, None

    # Kullanıcı yetkili değilse kendi dashboardına yönlendir
    messages.info(request, 'Kendi firmanıza yönlendirildiniz.')
    return False, redirect('dashboard', request.user.company.code)
def register(request, code):
    company = get_object_or_404(Company, code=code)
    users = User.objects.filter(company=company)
    print('Bulunan Şirket:', company)
    
    # Kullanıcı izinlerini kontrol et
    has_permission, redirect_response = check_user_permissions(request, company)
    if not has_permission:
        return redirect_response
    
    if not request.method == 'POST':
        form = CustomUserCreationForm(company=company)
        context = {
            'form': form,
            'users': users,
            'company': company,
        }
        return render(request, 'definitions/define_user.html', context)

    form = CustomUserCreationForm(request.POST, company=company)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        
        # Aynı kullanıcı adıyla bu şirkette kullanıcı olup olmadığını kontrol et
        if User.objects.filter(username=username, company=company).exists():
            messages.error(request, "Bu kullanıcı adı bu şirkette zaten mevcut.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        user = form.save(commit=False)
        user.company = company
        user.company_code = company.code
        user.save()
        Permission.objects.create(user=user) # yetki modeline kullanıcıyı ekle
        form.save_m2m()  # Many-to-many ilişkilerini kaydet
        
        login(request, user)
        return redirect('home')  # Ana sayfaya yönlendir
    
    
def stock_by_category(request, code):
    # Şirketi al
    company = get_object_or_404(Company, code=code)
    
    # Kullanıcı yetkilerini kontrol et
    if not check_user_permissions(request, company):
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

def change_unit_status(request, unit_id):
    if request.method != "POST":
        messages.add_message(request, messages.INFO, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    unit = get_object_or_404(Unit, id=unit_id)

    # Unit'in ait olduğu şirketi al
    company = unit.company

    # Kullanıcı yetkilerini kontrol et
    if not check_user_permissions(request, company):
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Unit'in aktiflik durumunu değiştir
    unit.is_active = not unit.is_active
    unit.save()
    
    messages.add_message(request, messages.SUCCESS, "İşlem başarıyla gerçekleştirildi.")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))
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
def create_unit(request, code):
    if request.method != "POST":
        messages.info(request, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    unit_name = request.POST.get("unit_name")
    if not unit_name:
        messages.info(request, "Birim Adı Boş Olamaz")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    company = get_object_or_404(Company, code=code)

    # Kullanıcı yetkilerini kontrol et
    if not check_user_permissions(request, company):
        return redirect('dashboard', request.user.company.code)

    if Unit.objects.filter(unit_name=unit_name, company=company).exists():
        messages.info(request, "Birim Adı Zaten Kayıtlı")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    Unit.objects.create(company=company, unit_name=unit_name,is_create=request.user)
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
        name=outgoing_reasons_name,
        is_create=request.user
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
        address=seller_address,
        is_create = request.user
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
    
    Category.objects.create(company=company, name=category_name,is_create=request.user)
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
def create_product(request, code):
    if request.method != "POST":
        messages.add_message(request, messages.ERROR, "Ürün Birimi Boş Geçilemez.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    product_name = request.POST.get("product_name")
    product_code = request.POST.get("product_code")
    product_unit = request.POST.get("product_unit")
    product_category = request.POST.get("product_category")
    product_is_inventory = request.POST.get("is_inventory") == "on"
    barcode_1 = request.POST.get("barcode_1")
    barcode_2 = request.POST.get("barcode_2")
    barcode_3 = request.POST.get("barcode_3")
    serial_number = request.POST.get("serial_number")
    prevent_stock_negative = request.POST.get("prevent_stock_negative") == "on"

    print(f'Product Name: {product_name}')
    print(f'Product Code: {product_code}')
    print(f'Product Unit: {product_unit}')
    print(f'Is Inventory: {product_is_inventory}')
    print(f'Barcode 1: {barcode_1}')
    print(f'Barcode 2: {barcode_2}')
    print(f'Barcode 3: {barcode_3}')
    print(f'Serial Number: {serial_number}')
    print(f'Prevent Stock Negative: {prevent_stock_negative}')
    print(f'Product Category: {product_category}')

    if not product_unit:
        messages.add_message(request, messages.ERROR, "Ürün Birimi Boş Geçilemez.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        unit = get_object_or_404(Unit, id=product_unit)
    except (ValueError, Unit.DoesNotExist):
        messages.add_message(request, messages.ERROR, "Geçersiz veya Bulunamayan Ürün Birimi.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    print('UNIT:', unit)

    try:
        category = Category.objects.get(id=product_category)
    except Category.DoesNotExist:
        messages.add_message(request, messages.ERROR, "Kategori Bulunamadı.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    company = get_object_or_404(Company, code=code)

    new_product = Product.objects.create(
        company=company,
        name=product_name,
        code=product_code,
        unit=unit,
        category=category,
        is_inventory=product_is_inventory,
        prevent_stock_negative=prevent_stock_negative,
        is_create=request.user
    )

    if product_is_inventory:
        if barcode_1:
            new_product.barcode_1 = barcode_1
        if barcode_2:
            new_product.barcode_2 = barcode_2
        if barcode_3:
            new_product.barcode_3 = barcode_3
        if serial_number:
            new_product.serial_number = serial_number

    new_product.save()

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
def add_bill(request, code):
    company = get_object_or_404(Company, code=code)
    sellers = Seller.objects.all()
    products = Product.objects.all()

    if request.method != "POST":
        context = {
            'company': company,
            'products': products,
            'sellers': sellers,
        }
        return render(request, 'add_bill.html', context)

    try:
        # POST verilerini al
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
        serial_number = request.POST.get("serial_number", None)
        barcode_1 = request.POST.get("barcode_1", None)
        barcode_2 = request.POST.get("barcode_2", None)
        barcode_3 = request.POST.get("barcode_3", None)
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
            seller=bill_seller,
            is_create=request.user,
            total_amount=Decimal('0.00')  # Initialize to zero
        )

        # Toplam tutarı hesapla
        total_amount = bill_item_quantity * bill_item_price
        discounted_amount = total_amount
        for discount in [bill_item_discount_1, bill_item_discount_2, bill_item_discount_3]:
            discounted_amount -= discounted_amount * (discount / Decimal(100))

        # KDV'yi hesapla
        vat_amount = discounted_amount * (bill_item_vat / Decimal(100))
        row_total = discounted_amount + vat_amount

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
            vat=bill_item_vat,
            row_total=row_total.quantize(Decimal('0.00')),  # Ensure proper decimal format
            is_create=request.user,
        )
        
        # Faturaya toplam tutarı kaydet
        bill.total_amount += row_total  # Ensure total_amount is initialized as Decimal
        bill.save()
        Inventory.objects.create(
                company=company,
                bill=bill,
                product = product,
                name = product.name,
                code = product.code,
                unit = product.unit,
                serial_number = serial_number,
                barcode_1=barcode_1,
                barcode_2=barcode_2,
                barcode_3=barcode_3

            )
        # Ürünün mevcut stokunu güncelle
        product.current_stock += bill_item_quantity
        product.save()

        # Stok işlemi oluştur veya güncelle
        stock, created = StockTransactions.objects.get_or_create(
            product=product,
            company=company,
            incoming_bill=bill,
            is_create=request.user,
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
        if bill_seller.receivable is None:
            bill_seller.receivable = Decimal('0.00')
        bill_seller.receivable += bill.total_amount
        bill_seller.save()

        messages.success(request, "Fatura ve Kalemler Başarıyla Oluşturuldu")
        return redirect('fatura_detay', code=company.code, bill_number=bill.number)

    except (Seller.DoesNotExist, Product.DoesNotExist):
        messages.error(request, "Fatura Oluşturulamadı. Satıcı veya Ürün bulunamadı.")
    except InvalidOperation as e:
        messages.error(request, f"Veri hatası: {str(e)}")
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"Fatura Oluşturulamadı. Hata: {str(e)}")
    
    # Hata durumunda aynı formu tekrar göster
    context = {
        'company': company,
        'products': products,
        'sellers': sellers,
    }
    return render(request, 'add_bill.html', context)
        
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
def bill_details(request,code, bill_number):
    company = get_object_or_404(Company,code=code)
    products = Product.objects.filter(company=company)
    
    try:
        bill = get_object_or_404(Bill,company=company, number=bill_number)
        bill_items = BillItem.objects.filter(company=company,bill=bill)
    except Http404:
        stock_transaction = get_object_or_404(OutgoingBill,company=company, number=bill_number)
        bill_items = None  
        
        context = {
            'company':company,
            'products': products,
            'stock_transaction': stock_transaction,
            'bill_items': bill_items,
        }
        return render(request, 'bill_details.html', context)

    context = {
        'company':company,
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
    bill_company = bill.company
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

        serial_number = request.POST.get("serial_number", None)
        barcode_1 = request.POST.get("barcode_1", None)
        barcode_2 = request.POST.get("barcode_2", None)
        barcode_3 = request.POST.get("barcode_3", None)

    except InvalidOperation:
        return JsonResponse({'error': 'Invalid number format.'}, status=400)

    try:
        with transaction.atomic():
            # Calculate row total (apply discounts first)
            item_total = bill_item_quantity * bill_item_price
            discounted_amount = item_total

            for discount in [bill_item_discount_1, bill_item_discount_2, bill_item_discount_3]:
                discounted_amount -= discounted_amount * (discount / Decimal(100))
            
            # Calculate VAT
            vat_amount = discounted_amount * (bill_item_vat / Decimal(100))
            row_total = discounted_amount + vat_amount

            # Create BillItem
            bill_item = BillItem.objects.create(
                bill=bill,
                company=bill_company,
                product=product,
                quantity=bill_item_quantity,
                price=bill_item_price,
                discount_1=bill_item_discount_1,
                discount_2=bill_item_discount_2,
                discount_3=bill_item_discount_3,
                vat=bill_item_vat,
                is_create=request.user,
                row_total=row_total.quantize(Decimal('0.00')),  # Ensure proper decimal format
            )

            # Update Product's current stock
            Product.objects.filter(id=product.id).update(current_stock=F('current_stock') + bill_item_quantity)

            # Update Bill's total amount
            bill.total_amount += row_total
            bill.save()

            # Create Inventory item if serial number is provided
            if serial_number:
                Inventory.objects.create(
                    company=bill_company,
                    bill=bill,
                    product=product,
                    name=product.name,
                    code=product.code,
                    unit=product.unit,
                    serial_number=serial_number,
                    barcode_1=barcode_1,
                    barcode_2=barcode_2,
                    barcode_3=barcode_3
                )

        return JsonResponse({
            "bill_item_product": product.name,
            "bill_item_quantity": f"{bill_item_quantity:.2f}",
            "bill_item_price": f"{bill_item_price:.2f}",
            "bill_item_discount_1": f"{bill_item_discount_1:.2f}",
            "bill_item_discount_2": f"{bill_item_discount_2:.2f}",
            "bill_item_discount_3": f"{bill_item_discount_3:.2f}",
            "bill_item_vat": f"{bill_item_vat:.2f}",
            "row_total": f"{row_total:.2f}",
            "new_total_amount": f"{bill.total_amount:.2f}",
            "is_inventory": serial_number is not None
        })

    except IntegrityError as e:
        return JsonResponse({'error': str(e)}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
from datetime import datetime
def inventory(request,code):
    company = get_object_or_404(Company,code=code)
    outgoing_reasons = OutgoingReasons.objects.filter(company=company)
    inventories = Inventory.objects.filter(company=company)
    context = {
        'outgoing_reasons':outgoing_reasons,
        'company':company,
        'inventories':inventories,
    }
    return render(request,'inventory.html',context)
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Company, OutgoingReasons, Inventory, OutgoingBill, StockTransactions

def outgoing_inventory(request, code):
    company = get_object_or_404(Company, code=code)
    serial_number = request.POST.get('serial_number')
    outgoing_reason_id = request.POST.get('outgoing_reason')
    
    # Outgoing reason'ı al
    outgoing_reason = OutgoingReasons.objects.filter(company=company, id=outgoing_reason_id).first()
    if not outgoing_reason:
        messages.info(request, 'Geçerli bir çıkış nedeni bulunamadı.')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    # Inventory item'ı al
    inventory_item = Inventory.objects.filter(company=company, serial_number=serial_number).first()
    if not inventory_item:
        messages.info(request, 'Seri numarası eşleşen ürün yok.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # inventory_outgoing_bill değerini oluştur
    inventory_outgoing_bill_number = request.POST.get('inventory_outgoing_bill_number', '')
    if not inventory_outgoing_bill_number:
        inventory_outgoing_bill_number = f"ENV-{company.code}-{serial_number}"

    try:
        # Çıkış faturası oluştur
        outgoing_bill = OutgoingBill.objects.create(
            company=company,
            number=inventory_outgoing_bill_number,
            product=inventory_item.product,
            quantity=1,
            processing_time=timezone.now(),
            outgoing_reason=outgoing_reason,
            is_create = request.user
        )

        # Stok işlemi oluştur
        StockTransactions.objects.create(
            company=company,
            product=inventory_item.product,
            outgoing_bill=outgoing_bill,
            outgoing_quantity=1,
            incoming_quantity=0,
            current_stock =0, 
            outgoing_reasons=outgoing_reason,
            is_create = request.user
        )
        inventory_item.is_released=True
        inventory_item.save()
        messages.success(request, 'Ürün başarıyla çıkış yapıldı.')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    except Exception as e:
        messages.error(request, f'Bir hata oluştu: {str(e)}')
        print(e)
        return redirect(request.META.get('HTTP_REFERER', '/'))

def stock_difference_report(request,code):
    # Tüm ürünleri al
    company = get_object_or_404(Company,code=code)
    products = Product.objects.filter(company=company)

    # Her ürün için giren ve çıkan miktarları hesapla
    product_reports = []
    for product in products:
        total_incoming = StockTransactions.objects.filter(product=product,company=company).aggregate(Sum('incoming_quantity'))['incoming_quantity__sum'] or 0
        total_outgoing = StockTransactions.objects.filter(product=product,company=company).aggregate(Sum('outgoing_quantity'))['outgoing_quantity__sum'] or 0
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


def incoming_outgoing_reports(request, code):
    company = get_object_or_404(Company, code=code)
    products = Product.objects.filter(company=company)

    today = date.today()
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else today
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else today

    # Make sure end_date is at the end of the day
    end_date = datetime.combine(end_date, datetime.max.time())

    stock_transactions = StockTransactions.objects.filter(
        processing_time__range=(start_date, end_date), company=company
    )
    table = StockTransactionsTable(stock_transactions)

    context = {
        'company': company,
        'table': table,
        'products': products,
        'start_date': start_date,
        'end_date': end_date,
    }

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
def get_inventory_products(request):
    product_id = request.GET.get('product_id')
    inventory_products = Inventory.objects.filter(product_id=product_id)
    data = list(inventory_products.values('id', 'serial_number'))
    return JsonResponse(data, safe=False)
def process_stock_outgoing(request, code):
    company = get_object_or_404(Company, code=code)
    products = Product.objects.filter(company=company)
    outgoing_reasons = OutgoingReasons.objects.filter(company=company)
    inventories = Inventory.objects.filter(company=company)
    if request.method != "POST":
        context = {
            'inventories':inventories,
            'company': company,
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
        with transaction.atomic():
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

            # Retrieve the company's cost calculation method
            parameter = Parameter.objects.get(company=company)
            cost_calculation_method = parameter.cost_calculation

            # Calculate total amount based on the cost calculation method
            if cost_calculation_method == 'fifo':
                # FIFO calculation
                bill_items = BillItem.objects.filter(product=outgoing_product, is_delete=False).order_by('bill__date')
            elif cost_calculation_method == 'lifo':
                # LIFO calculation
                bill_items = BillItem.objects.filter(product=outgoing_product, is_delete=False).order_by('-bill__date')
            else:
                # Default to average cost calculation
                bill_items = BillItem.objects.filter(product=outgoing_product, is_delete=False)

            total_cost = Decimal('0.00')
            total_quantity = Decimal('0.00')

            for item in bill_items:
                item_quantity = item.quantity
                item_cost = item.price * (1 - item.discount_1 / 100) * (1 - item.discount_2 / 100) * (1 - item.discount_3 / 100) * (1 + item.vat / 100)
                total_cost += item_quantity * item_cost
                total_quantity += item_quantity

            average_cost = total_cost / total_quantity if total_quantity > 0 else Decimal('0.00')
            outgoing_total_amount = average_cost * outgoing_quantity

            outgoing_product.current_stock -= outgoing_quantity
            outgoing_product.save()

            outgoing_bill = OutgoingBill.objects.create(
                is_create=request.user,
                company=company,
                number=outgoing_bill_number,
                product=outgoing_product,
                quantity=outgoing_quantity,
                outgoing_reason=outgoing_reason,
                processing_time=timezone.now(),
                outgoing_total_amount=outgoing_total_amount,
            )
            
            stock_outgoing = StockTransactions.objects.create(
                company=company,
                product=outgoing_product,
                outgoing_quantity=outgoing_quantity,
                outgoing_reasons=outgoing_reason,
                outgoing_bill=outgoing_bill,
                processing_time=timezone.now(),
                current_stock=outgoing_product.current_stock,
                total_amount = outgoing_total_amount,
                is_create=request.user
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
def low_stock_reports(request, code):
    company = get_object_or_404(Company, code=code)
    low_stock_products = Product.objects.filter(company=company, current_stock__lt=F('critical_stock_level'))
    context = {
        'company': company,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'reports/low_stock_products.html', context)
from django.contrib.auth import logout as auth_logout
def logout(request):
    auth_logout(request)
    return redirect('login')
