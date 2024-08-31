from datetime import timedelta, timezone
import random
import uuid
from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import date

from django.shortcuts import render
from .models import ChatRoom, Company, Inventory, Parameter, Product, StockTransactions, User,Message
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

from .forms import CategoryForm, CompanyForm, ParameterForm, PermissionForm, ProductForm, ProductUpdateForm, SellerForm, UserEditForm
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.utils.crypto import get_random_string


def companies(request, company_code):
    company = get_object_or_404(Company, code=company_code)
    
    # `ssoft` değil ve `list_company` izni yoksa
    if request.user.username != 'ssoft' and not request.user.permissions.list_company:
        messages.error(request, 'Bu Sayfaya Ulaşamazsınız.')
        return redirect('dashboard', company.code)
    
    companies = Company.objects.all()
    
    context = {
        'company': company,
        'companies': companies,
    }
    return render(request, 'companies.html', context)
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


def create_company(request, code):
    # Şirketi al
    company = get_object_or_404(Company, code=code)
    print('Bu kontrole geliyor.')
    # Kullanıcının şirkete erişim izni olup olmadığını kontrol et
   

    if request.method == 'POST':
        if not (request.user.company.code == 1 and request.user.permissions.add_company):
            print('Bu kontrole geliyor.')
            # print(request.user.user_permissions.add_company)
            messages.error(request, 'Bu işlemi yapma yetkiniz yok.')
            return redirect('dashboard', code=request.user.company.code)
    # Formu al ve doğrula
    form = CompanyForm(request.POST)
    if form.is_valid():
        # Yeni şirket oluştur
        new_company = form.save(commit=False)
        new_company.code = generate_unique_code()  # Şirket kodunu oluştur
        new_company.create_user = request.user  # Şirketi oluşturan kullanıcıyı ayarla
        new_company.save()  # Veritabanına kaydet
        
        messages.success(request, 'Yeni şirket başarıyla oluşturuldu.')
        return redirect('firmalar', request.user.company.code)  # Başarılı bir şekilde kaydedildikten sonra yönlendirin
    else:
        # GET isteği için formu oluştur
        form = CompanyForm()
    
    # Şablona verileri gönder
    context = {
        'form': form,
        'company': company,
    }
    return render(request, 'definitions/define_company.html', context)
     

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
    if not request.user.is_authenticated:
        messages.error(request, 'Giriş yapmalısınız.')
        return redirect('login')
    
    company = get_object_or_404(Company, code=code)
    
    has_permission, redirect_response = check_user_permissions(request, company)
    
    if not has_permission:
        return redirect_response

    user = get_object_or_404(User, unique_id=uuid4)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            
            # is_active değeri güncelleniyor
            user.is_active = 'is_active' in request.POST
            
            # Formdan gelen tag değeri kontrol ediliyor
            new_tag = request.POST.get('tag')
            if new_tag:  # Eğer tag değeri varsa, güncelle
                user.tag = new_tag
            
            # Diğer işlemler
            print(user.profile_image)
            
            # Kullanıcıyı kaydet
            user.save()
            
            messages.success(request, 'Güncelleme Başarılı')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UserEditForm(instance=user)
    
    return render(request, 'user_page/user_detail.html', {'form': form, 'company': company})
def edit_permissions(request, code, uuid4):
    if not (request.user.username == 'ssoft' or request.user.company.code == code):
        messages.error(request, 'Sadece kendi firmanız için işlem yapabilirsiniz.')
        return redirect('dashboard', request.user.company.code)

    user = get_object_or_404(User, unique_id=uuid4)
    print(user.id)
    company = get_object_or_404(Company, code=code)
    permission, created = Permission.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        perm_form = PermissionForm(request.POST, instance=permission)
        if perm_form.is_valid():
            perm_form.save()
            messages.success(request, 'Yetkilendirme1 Başarılı')
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            messages.error(request, 'Yetkilendirme sırasında bir hata oluştu.')
    else:
        perm_form = PermissionForm(instance=permission)
    
    return render(request, 'user_page/edit_permissions.html', {
        'perm_form': perm_form,
        'company': company,
        'user': user
    })
from django.db import models

def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        company_code = request.POST.get('company_code')

        # Şirketi al veya 404 döndür
        company = get_object_or_404(Company, code=company_code)

        try:
            # Kullanıcıyı al
            user = User.objects.get(username=username, company=company)
            
            # Kullanıcının aktif olup olmadığını kontrol et
            if not user.is_active:
                messages.error(request, "Kullanıcı aktif değil.")
                return render(request, 'login.html')

            # Şifreyi kontrol et
            if not user.check_password(password):
                messages.error(request, "Geçersiz şifre.")
                return render(request, 'login.html')

            # Kullanıcının doğru şirketle ilişkilendirilmiş olup olmadığını kontrol et
            if user.company != company:
                messages.error(request, "Bu kullanıcı bu firmaya ait değil.")
                return render(request, 'login.html')

            # Kullanıcıya ait yetkilerin olup olmadığını kontrol et ve yoksa oluştur
            permission, created = Permission.objects.get_or_create(user=user)

            # Eğer kullanıcı ssoft ise, tüm boolean izinlerini True yap
            if user.username == 'ssoft':
                for field in Permission._meta.get_fields():
                    if isinstance(field, models.BooleanField):
                        setattr(permission, field.name, True)
                permission.save()

            # Giriş işlemini gerçekleştir
            login(request, user)
            request.session['company_code'] = company.code

            # Başarıyla giriş yaptıktan sonra yönlendirme
            return redirect('dashboard', code=company.code)

        except User.DoesNotExist:
            messages.error(request, "Geçersiz kullanıcı adı veya şifre.")
            return render(request, 'login.html')

    return render(request, 'login.html')

def user_detail(request, code, uuid4):
    company = get_object_or_404(Company, code=code)
    user = get_object_or_404(User, unique_id=uuid4)
    
    # Check if the authenticated user is 'sssoft', belongs to the company, or has the required permission
    if not (request.user.username == 'ssoft' or request.user.company == company):
        messages.error(request, 'Sadece kendi firmanız için işlem yapabilirsiniz.')
        return redirect('dashboard', request.user.company.code)
    
    context = {
        'company': company,
        'user': user,
    }
    return render(request, 'user_page/user_detail.html', context)
from django.contrib.auth.decorators import login_required

# @login_required
def dashboard(request, code):
    company = get_object_or_404(Company, code=code)

    # Kullanıcı kimliği doğrulanmamışsa giriş sayfasına yönlendir
    if not request.user.is_authenticated:
        messages.error(request, 'Önce giriş yapmalısınız.')
        return redirect('login')

    # Kullanıcı kendi şirketinde değilse ve şirket kodu 1 değilse kendi şirketine yönlendir
    if request.user.company.code != company.code and request.user.company.code != 1:
        messages.error(request, 'Kendi Şirketinize Yönlendirildiniz.')
        return redirect('dashboard', request.user.company.code)

    # Şirket verilerini al
    products = Product.objects.filter(company=company)
    sellers = Seller.objects.filter(company=company)
    last_bill = Bill.objects.filter(company=company).last()

    context = {
        'company': company,
        'sellers': sellers,
        'last_bill': last_bill,
        'outgoing_count': OutgoingBill.objects.filter(company=company).count(),
        'bill_count': Bill.objects.filter(company=company).count(),
        'products_count': products.count(),
        'products': products,
        'product_names': [],
        'product_stocks': [],
        'category_names': [],
        'category_counts': [],
    }

    # Stokları en düşük olan 5 ürünü al
    products_with_min_stock = products.order_by('current_stock')[:5]
    context['product_names'] = [product.name for product in products_with_min_stock]
    context['product_stocks'] = [product.current_stock for product in products_with_min_stock]

    # Her kategoride kaç ürün var
    categories = Category.objects.filter(company=company)
    context['category_names'] = [category.name for category in categories]
    context['category_counts'] = [category.product_set.count() for category in categories]

    # Eğer şirket kodu 1 ise tüm şirketleri dahil et
    if company.code == 1:
        context['companies'] = Company.objects.all()

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
    
    if request.method == 'POST':
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
            Permission.objects.create(user=user)  # Yetki modeline kullanıcıyı ekle
            form.save_m2m()  # Many-to-many ilişkilerini kaydet
            
            # login(request, user)
            return redirect('home')  # Ana sayfaya yönlendir

    else:
        form = CustomUserCreationForm(company=company)

    context = {
        'form': form,
        'users': users,
        'company': company,
    }
    return render(request, 'definitions/define_user.html', context)
    
    
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

def change_unit_status(request, code, unit_id):
    if request.method != "POST":
        messages.add_message(request, messages.INFO, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    company = get_object_or_404(Company, code=code)
    unit = get_object_or_404(Unit, id=unit_id, company=company)

    # Kullanıcı yetkileri ve şirket kodu kontrolü
    has_permission = (
        (request.user.company == company and request.user.permissions.update_unit) or
        request.user.company.code == 1
    )

    if not has_permission:
        messages.add_message(request, messages.ERROR, "Yetkiniz Yok")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Unit'in aktiflik durumunu değiştir
    unit.is_active = not unit.is_active
    unit.save()
    
    messages.add_message(request, messages.SUCCESS, "İşlem başarıyla gerçekleştirildi.")
    return redirect(request.META.get('HTTP_REFERER', '/'))
def delete_unit(request, unit_id, code):
    company = get_object_or_404(Company, code=code)
    user_company_code = request.user.company.code
    
    # Yalnızca POST istekleriyle işleme izin verilir
    if request.method != "POST":
        messages.add_message(request, messages.INFO, "Silme işlemi gerçekleşmedi.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    # Kullanıcı izinleri kontrol edilir
    has_permission = (
        (user_company_code == company.code or user_company_code == 1) and
        request.user.permissions.delete_unit
    )

    if not has_permission:
        messages.info(request, "Bu işleme yetkiniz yok.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    # Birim bulunur, bulunamazsa hata döner
    try:
        unit = Unit.objects.get(id=unit_id, company=company)
    except Unit.DoesNotExist:
        messages.add_message(request, messages.ERROR, "Birim bulunamadı.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    # Birime bağlı ürün var mı kontrol edilir
    if Product.objects.filter(unit=unit, company=company).exists():
        messages.add_message(request, messages.WARNING, "Bu birim bir ürüne bağlı olduğu için silinemez.")
    else:
        unit.delete()
        messages.add_message(request, messages.SUCCESS, "Birim başarıyla silindi.")
    
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
def check_company_access(request, company_code):
    # Şirketi al veya 404 döndür
    company = get_object_or_404(Company, code=company_code)
    
    if not request.user.is_authenticated:
        messages.error(request, 'Önce giriş yapmalısınız.')
        return redirect('login')

    # Kullanıcı kendi şirketine mi bakıyor?
    if request.user.company.code != company_code and request.user.company.code != 1:
        messages.error(request,'İstek yapılan şirket size ait değil.')
        return redirect('dashboard', request.user.company.code)  # Dashboard sayfasına yönlendir

    return company  # Şirket nesnesini döndür

def create_unit_page(request, code):
    # Şirket doğrulamasını yap
    company = check_company_access(request, code)

    if isinstance(company, HttpResponseRedirect):
        return company

    # Doğrulama başarılıysa, birimleri al
    units = Unit.objects.filter(company=company)
    
    context = {
        'company': company,
        'units': units,
    }

    return render(request, 'definitions/define_unit.html', context)
def create_unit(request, code):
    # Yalnızca POST isteklerine izin verilir
    if request.method != "POST":
        messages.info(request, "İşlem Gerçekleşmedi.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Kullanıcının birim ekleme yetkisi olup olmadığını kontrol et
    if not request.user.permissions.add_unit:
        messages.info(request, "Birim ekleme yetkisine sahip değilsiniz.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    unit_name = request.POST.get("unit_name")
    
    # Birim adı boş olamaz
    if not unit_name:
        messages.info(request, "Birim adı boş olamaz.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    company = get_object_or_404(Company, code=code)

    # Kullanıcı yetkilerini kontrol et
    if not check_user_permissions(request, company):
        return redirect('dashboard', request.user.company.code)

    # Aynı isimde birim olup olmadığını kontrol et
    if Unit.objects.filter(unit_name=unit_name, company=company).exists():
        messages.info(request, "Bu birim adı zaten kayıtlı.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    # Yeni birim oluştur ve başarı mesajı göster
    Unit.objects.create(company=company, unit_name=unit_name, is_create=request.user)
    messages.success(request, "Birim başarıyla eklendi.")
    return redirect(request.META.get('HTTP_REFERER', '/'))


def create_outgoing_reasons_page(request,code):
    company = check_company_access(request, code)

    if isinstance(company, HttpResponseRedirect):
        return company
    reasons = OutgoingReasons.objects.filter(company=company)
    context = {
        'company':company,
        'reasons':reasons,
    }
    return render(request,'definitions/define_outgoing.html',context)
from django.core.exceptions import ObjectDoesNotExist
def create_outgoing_reasons(request, code):
    # Yalnızca POST istekleri kabul edilir
    if request.method != "POST":
        messages.info(request, "İşlem Gerçekleşmedi")
        return redirect('cikis_tanimlama_sayfasi', request.user.company.code)
    
    # Yetkilendirme kontrolü
    if not request.user.permissions.add_unit or request.user.company.code == 1:
        messages.info(request, "Birim ekleme yetkisine sahip değilsiniz.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    outgoing_reasons_name = request.POST.get("outgoing_reason")
    
    # Şirketin var olup olmadığını kontrol et
    company = get_object_or_404(Company, code=code)
    
    # Çıkış nedeninin mevcut olup olmadığını kontrol et
    if OutgoingReasons.objects.filter(name=outgoing_reasons_name, company=company).exists():
        messages.info(request, "Aynı İsimde Bir Çıkış Nedeni Bulunuyor")
        return redirect('cikis_tanimlama_sayfasi', request.user.company.code)
    
    # Yeni çıkış nedenini oluştur
    cikis_nedeni = OutgoingReasons.objects.create(
        company=company,
        name=outgoing_reasons_name,
        is_create=request.user
    )
    
    # Başarı mesajı göster ve yönlendir
    messages.success(request, f"{cikis_nedeni.name} adlı stok çıkış nedeni oluşturuldu")
    return redirect('cikis_tanimlama_sayfasi', request.user.company.code)
def delete_outgoing_reason(request, code, reason_id):
    # Şirket doğrulamasını yap
    company = check_company_access(request, code)

    if isinstance(company, HttpResponseRedirect):
        return company

    # Kullanıcının bu işlemi yapma yetkisini kontrol et
    # if not request.user.permissions.delete_outgoing_reason or request.user.company.code == 1:
    #     messages.error(request, 'Bu işleme yetkiniz bulunmuyor.')
    #     return redirect('cikis_tanimlama_sayfasi', company.code)

    # Çıkış nedenini al veya 404 döndür
    reason = get_object_or_404(OutgoingReasons, id=reason_id, company=company)

    # Çıkış nedeninin bir faturada kullanılıp kullanılmadığını kontrol et
    if OutgoingBill.objects.filter(outgoing_reason=reason,company=company).exists():
        messages.error(request, 'Bu çıkış nedeni bir faturada kullanıldığı için silinemez.')
        return redirect('cikis_tanimlama_sayfasi', company.code)

    # Çıkış nedenini sil
    reason.delete()
    messages.success(request, f'{reason.name} adlı çıkış nedeni başarıyla silindi.')
    return redirect('cikis_tanimlama_sayfasi', company.code)
def update_outgoing_reason(request, code, reason_id):
    # Şirketi doğrula
    company = get_object_or_404(Company, code=code)
    
    # Güncellenecek çıkış nedenini al
    outgoing_reason = get_object_or_404(OutgoingReasons, id=reason_id, company=company)
    
    if request.method == "POST":
        updated_name = request.POST.get("outgoing_reason")
        
        # Eğer aynı isimde başka bir çıkış nedeni varsa, güncellemeyi engelle
        if OutgoingReasons.objects.filter(name=updated_name, company=company).exclude(id=reason_id).exists():
            messages.info(request, "Aynı isimde bir çıkış nedeni zaten var.")
            return redirect('cikis_tanimlama_sayfasi', company.code)
        
        # Çıkış nedenini güncelle
        outgoing_reason.name = updated_name
        outgoing_reason.save()
        
        messages.success(request, f"{outgoing_reason.name} adlı çıkış nedeni güncellendi.")
        return redirect('cikis_tanimlama_sayfasi', company.code)
    
    # Eğer GET isteği ise, mevcut bilgileri formda göster
    context = {
        'company': company,
        'outgoing_reason': outgoing_reason,
    }
    
    return render(request, 'definitions/update_outgoing_reason.html', context)
def change_active_status(request, id):
    selected_reason = get_object_or_404(OutgoingReasons, id=id)
    selected_reason.is_active = not selected_reason.is_active
    selected_reason.save()
    
    messages.add_message(request, messages.SUCCESS, f"'{selected_reason.name}' çıkış nedeni {'Aktif' if selected_reason.is_active else 'Pasif'}")
    return redirect(request.META.get('HTTP_REFERER', '/'))
def change_seller_status(request,code,seller_id):
    company = check_company_access(request, code)

    if isinstance(company, HttpResponseRedirect):
        return company
    if not request.user.permissions.update_seller or request.user.company.code == 1:
        messages.error(request, "Yetkiniz Yok.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    seller = get_object_or_404(Seller,id=seller_id)
    if seller.status == True:
        seller.status = False
    else:
        seller.status = True
    seller.save()
    messages.success(request, "Cari Durumu Güncellendi")
    return redirect(request.META.get('HTTP_REFERER', '/'))
def create_seller(request, code):
    company = check_company_access(request, code)

    if isinstance(company, HttpResponseRedirect):
        return company

    # Kullanıcının izinlerini kontrol et
    if not request.user.permissions.add_seller:
        messages.error(request, "Cari Oluşturma Yetkisine Sahip Değilsiniz.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if request.method == "POST":
        seller_form = SellerForm(request.POST)
        if seller_form.is_valid():
            # Formdan gelen verilerle yeni bir Seller oluştur
            seller = seller_form.save(commit=False)
            seller.company = company
            seller.is_create = request.user
            seller.save()
            messages.success(request, "Cari Oluşturuldu")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            # Form geçerli değilse, hataları kullanıcıya göster
            for field, errors in seller_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        seller_form = SellerForm()

    # GET isteği veya form geçerli değilse formu ve diğer bilgileri render et
    sellers = Seller.objects.filter(company=company)
    context = {
        'form': seller_form,
        'sellers': sellers,
        'company': company
    }
    return render(request, 'definitions/define_seller.html', context)
def update_seller(request, company_code, seller_id):
    company = check_company_access(request, company_code)

    if isinstance(company, HttpResponseRedirect):
        return company
    seller = get_object_or_404(Seller, id=seller_id, company__code=company_code)
    
    if request.method == 'POST':
        seller.name = request.POST.get('name')
        seller.address = request.POST.get('address')
        seller.status = request.POST.get('status') == 'True'
        seller.save()
        messages.success(request, "Cari Durumu Güncellendi")
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})
def delete_seller(request, company_code, seller_id):
    company = check_company_access(request, company_code)

    # Şirket erişimi kontrolü
    if isinstance(company, HttpResponseRedirect):
        return company

    # Satıcıyı bul
    seller = get_object_or_404(Seller, id=seller_id, company=company)

    # Satıcıya ait fatura var mı kontrol et
    if Bill.objects.filter(company=company, seller=seller).exists():
        messages.error(request, "Bu satıcıya ait fatura var, bu yüzden silinemez.")
        return redirect('cari_tanimla',request.user.company.code)

    # Satıcıyı sil
    seller.delete()
    messages.success(request, "Satıcı başarıyla silindi.")
    return redirect('cari_tanimla',request.user.company.code)
def kategori_guncelle(request, company_code, category_id):
    # İlgili kategoriyi ve şirketi alın
    category = get_object_or_404(Category, id=category_id, company__code=company_code)
    
    # Gelen verileri form ile doğrulayın ve işleyin
    form = CategoryForm(request.POST, instance=category)
    if form.is_valid():
        form.save()  # Kategoriyi güncelle
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'errors': form.errors})
def create_category_page(request,code):
    company = check_company_access(request, code)

    if isinstance(company, HttpResponseRedirect):
        return company
    categories = Category.objects.filter(company=company)
    context = {
        'company':company,
        'categories':categories,
    }
    return render(request,'definitions/define_category.html',context)
def generate_room_name():
    return str(uuid.uuid4())

# Oda oluşturma view'i
def destek_view(request, code):
    company = get_object_or_404(Company, code=code)
    room_name = generate_room_name()

    # company.code değeri 1 olan kullanıcıyı bul
    owner = request.user
    # Chat odasını oluştur ve owner alanını ayarla
    room = ChatRoom.objects.create(name=room_name, owner=owner)
    room.status = False
    room.save()    # Kullanıcıyı chat odasına yönlendir
    return redirect('room', room_name=room_name, code=code)
def end_chat(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name)
    if room.supportive == request.user:
        elapsed_time = timezone.now() - room.created_at  # Odanın oluşturulma zamanını kontrol ediyoruz
        remaining_time = timedelta(minutes=1) - elapsed_time
        
        if elapsed_time < timedelta(minutes=1):
            minutes, seconds = divmod(remaining_time.seconds, 60)
            messages.error(request, f'Desteği sonlandırmak için en az 1 dakika beklemelisiniz. Kalan süre: {minutes} dakika {seconds} saniye.')
            print(f'Desteği sonlandırmak için en az 1 dakika beklemelisiniz. Kalan süre: {minutes} dakika {seconds} saniye.')
            return redirect(request.META.get('HTTP_REFERER', '/'))
    # Oda sahibinin odayı hemen kapatabilmesi veya yetkili kullanıcının kapatabilmesi
    if room.owner == request.user:
        room.status = True
        rating = request.POST.get('rating')
        print('Rating Puanı', rating)
        room.save()
        messages.info(request, 'Destek Sonlandırıldı İyi Çalışmalar')
        return redirect('dashboard', request.user.company.code)
    
    # Destek veren kullanıcının en az 1 dakika beklemesi
    
        
    room.status = True
    rating = request.POST.get('rating')
    print('Rating Puanı', rating)
    room.save()
    messages.info(request, 'Destek Sonlandırıldı İyi Çalışmalar')
    return redirect('dashboard', request.user.company.code)
    
    # Diğer durumlarda hata mesajı gönder
    messages.error(request, 'Sadece kendi desteğinizi sonlandırabilirsiniz.')
    return redirect(request.META.get('HTTP_REFERER', '/'))
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def set_notifications(request):
    if request.method == 'POST':
        # İşlem yap
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)
def room_detail(request,room_name,code):
    company = get_object_or_404(Company,code=code)
    room = get_object_or_404(ChatRoom,name = room_name)
    message = Message.objects.filter(room=room)
    context = {
        'company':company,
        'room':room,
        'message':message,
    }
    return render(request,'room_detail.html',context)
def check_chat_room(request,code):
    company = get_object_or_404(Company,code=code)

    if company.code != 1:
        messages.error(request,'Bu alana erişemezsiniz')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    rooms = ChatRoom.objects.all()
    context = {
        'company':company,
        'rooms':rooms
    }
    return render(request,'check_chat_room.html',context)
def room(request, room_name, code):
    company = get_object_or_404(Company, code=code)
    room = get_object_or_404(ChatRoom, name=room_name)
    if request.user.username == 'ssoft':
        return render(request, 'chat_room.html', {
        'room_name': room_name,
        'company': company,
        'room': room,
    })
    if room.status == True:
        messages.info(request, "Kapalı Bir odaya ulaşamazsınız")
        return redirect('dashboard',request.user.company.code)
  
    return render(request, 'chat_room.html', {
        'room_name': room_name,
        'company': company,
        'room': room,
    })
def rating_supporter(request,room_name):
    if not request.method == "POST":
        room = get_object_or_404(ChatRoom,name=room_name)
        room.supportive.rating

def give_support(request):
    room = ChatRoom.objects.filter(status=False).first()
    if room:
        room.supportive = request.user
        room.save()
        return redirect('room', room_name=room.name, code=room.owner.company.code)
   
    else:
        return render(request, 'no_available_rooms.html')
def get_company_or_redirect(request, code, error_message="Şirket Bulunamadı"):
    try:
        return get_object_or_404(Company, code=code)
    except:
        messages.add_message(request, messages.INFO, error_message)
        return redirect(request.META.get('HTTP_REFERER', '/'))
def change_category_status(request,id,code):
    company = check_company_access(request, code)

    if isinstance(company, HttpResponseRedirect):
        return company
    if not request.user.permissions.add_category:
        messages.info(request, "Yetkiniz Bulunmuyor")
        return redirect(request.META.get('HTTP_REFERER', '/'))
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
    
    company = check_company_access(request, code)

    if isinstance(company, HttpResponseRedirect):
        return company
    if request.method != "POST":
        messages.info(request, "İşlem Gerçekleşmedi")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    category_name = request.POST.get("category_name")
    if not request.user.permissions.add_category:
        messages.warning(request, "Yetkiniz Bulunmuyor")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    if not category_name:
        messages.warning(request, "Kategori ismi boş olamaz")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if Category.objects.filter(name=category_name, company=company).exists():
        messages.warning(request, "Bu isimde bir kategori zaten mevcut")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    Category.objects.create(company=company, name=category_name,is_create=request.user)
    messages.success(request, "Kategori Oluşturuldu")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))
@login_required(login_url='/login/')
def product_add_page(request, code):
    company = get_object_or_404(Company, code=code)
    if not (
    request.user.username == 'ssoft' or
    (request.user.tag == 'Destek' and request.user.company.code == 1) or
    request.user.company.code == company.code
    ):
        messages.add_message(request, messages.ERROR, "Sadece kendi firmanızda işlem yapabilirsiniz.")
        return redirect('dashboard',request.user.company.code)
    units = Unit.objects.filter(company=company)
    categories = Category.objects.filter(company=company)
    products = Product.objects.filter(company=company,is_active=True).order_by('name')

    
    context = {
        'company': company,
        'categories': categories,
        'units': units,
        'products': products
    }
    
    return render(request, 'definitions/define_product.html', context)
def create_product(request, code):
    company = get_object_or_404(Company, code=code)
    
    # Kullanıcı yetki kontrolü
    if not (
        request.user.username == 'ssoft' or
        (request.user.tag == 'Destek' and request.user.company.code == 1) or
        request.user.company.code == company.code
    ):
        messages.error(request, "Yetkiniz Bulunmuyor")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    if request.method == "POST":
        form = ProductForm(request.POST)
        
        if form.is_valid():
            product_code = form.cleaned_data['code']
            
            # Ürün kodu kontrolü
            if Product.objects.filter(code=product_code, company=company).exists():
                messages.error(request, "Bu ürün kodu zaten mevcut.")
                return redirect(request.META.get('HTTP_REFERER', '/'))

            new_product = form.save(commit=False)
            new_product.company = company
            new_product.is_create = request.user
            new_product.save()
            
            messages.success(request, "Ürün Kaydedildi")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        else:
            # Formda hata varsa
            messages.error(request, "Formda hatalar var. Lütfen kontrol ediniz.")
            print(form.errors)
            return redirect(request.META.get('HTTP_REFERER', '/'))    
    else:
        form = ProductForm()
        return render(request, 'product/create_product.html', {'form': form})
def update_product(request, company_code, product_id):
    # İlgili ürün ve şirketi kontrol et
    product = get_object_or_404(Product, id=product_id, company__code=company_code)

    # Kullanıcı yetki kontrolü
    if not (
        request.user.username == 'ssoft' or
        (request.user.tag == 'Destek' and request.user.company.code == 1) or
        request.user.company.code == company_code
    ):
        messages.error(request, "Yetkiniz Bulunmuyor")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    if request.method != 'POST':
        form = ProductUpdateForm(instance=product)
        return redirect('urun_olustur', company_code)
    
    form = ProductUpdateForm(request.POST, instance=product)
    if not form.is_valid():
        messages.error(request, 'Ürün güncellenirken bir hata oluştu.')
        return redirect('urun_olustur', company_code)
    
    updated_product_code = form.cleaned_data['code']
    
    # Aynı ürün koduna sahip başka bir ürün var mı kontrol et
    if Product.objects.filter(code=updated_product_code, company__code=company_code).exclude(id=product_id).exists():
        messages.error(request, "Bu ürün kodu zaten mevcut. Lütfen farklı bir ürün kodu giriniz.")
        return redirect('urun_olustur', company_code)
    
    # Ürün güncelleniyor
    form.save()
    messages.success(request, 'Ürün başarıyla güncellendi.')
    return redirect('urun_olustur', company_code)
        
    
        
def delete_product(request,company_code,product_id):
    company = check_company_access(request, company_code)
    if isinstance(company, HttpResponseRedirect):
        return company
    if not request.method == "POST":
        messages.success(request, "İşlem Gerçekleştirilemedi.") # POST İsteklerini Kontrol Et
        return redirect(request.META.get('HTTP_REFERER', '/'))
    if not request.user.permissions.delete_product:
        messages.info(request, "Yetkiniz Bulunmuyor")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    product = get_object_or_404(Product,id=product_id)
    print('Ürün Bulundu',product)
    if product.is_active == True:
        product.is_active = False
    else:
        product.is_active = True
    product.save()
    messages.info(request, "Ürün Silindi") 
    return redirect(request.META.get('HTTP_REFERER', '/')) 
from decimal import Decimal
from decimal import Decimal, InvalidOperation
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Seller, Product, Bill, BillItem, StockTransactions
from decimal import Decimal, ROUND_DOWN
from django.views.decorators.http import require_POST
@require_POST  # Bu dekoratör sadece POST isteklerini kabul eder
def delete_item(request):
    item_id = request.POST.get('item_id')  # POST isteğinden item_id'yi alın
    try:
        # Silinecek öğeyi bulun
        item = BillItem.objects.get(id=item_id)
        
        # İlgili fatura için toplamı güncellemek için gereken fatura objesini alın
        bill = item.bill

        # Öğeyi silin
        item.delete()

        # Faturanın yeni toplamını hesaplayın
        new_total_amount = bill.billitem_set.aggregate(Sum('row_total'))['row_total__sum'] or 0.0

        return JsonResponse({'success': True, 'new_total_amount': new_total_amount})

    except BillItem.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Öğe bulunamadı.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
def add_bill(request, code):
    company = get_object_or_404(Company, code=code)
    sellers = Seller.objects.filter(company=company,status=True) # şirketle alakalı aktif olan satıcıları getir
    products = Product.objects.filter(company=company,is_active=True)# şirketle alakalı aktif olan ürünleri getir

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
            # Satır toplamını hesaplayın (ilk olarak indirimleri uygulayın)
            item_total = bill_item_quantity * bill_item_price
            discounted_amount = item_total

            for discount in [bill_item_discount_1, bill_item_discount_2, bill_item_discount_3]:
                discounted_amount -= discounted_amount * (discount / Decimal(100))
            
            # KDV'yi hesaplayın
            vat_amount = discounted_amount * (bill_item_vat / Decimal(100))
            row_total = discounted_amount + vat_amount

            # BillItem oluştur
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
                row_total=row_total.quantize(Decimal('0.00')),  # Doğru ondalık biçimi sağla
            )

            # Ürünün güncel stok miktarını güncelle
            Product.objects.filter(id=product.id).update(current_stock=F('current_stock') + bill_item_quantity)

            # Faturanın toplam miktarını güncelle
            bill.total_amount += row_total
            bill.save()

            # Seri numarası sağlanmışsa envanter öğesi oluştur
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
            "bill_item_id": bill_item.id,  # Burada ID değerini ekleyin
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
def webrtc(request):
    return render(request, 'webrtc.html')