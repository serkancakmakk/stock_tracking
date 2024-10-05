from datetime import date, timedelta, datetime
from decimal import Decimal, InvalidOperation
import random
import timeit
import uuid
from django.db import IntegrityError, transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import path, reverse
from django.contrib.auth import authenticate, login, update_session_auth_hash, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, F, Q, Count
from django.utils.crypto import get_random_string
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from collections import defaultdict
from .models import (
    Bill, BillItem, Category, ErrorMessage, OutgoingBill, OutgoingReasons, 
    Product, Seller, StockTransactions, Unit, ChatRoom, Company, Inventory, 
    Parameter, User, Message, Permission
)
from .forms import (
    CategoryForm, ChangePasswordForm, CompanyForm, ParameterForm, PermissionForm, 
    ProductForm, ProductUpdateForm, ReportBugForm, SellerForm, UpdateUnitForm, 
    UserEditForm, CustomUserCreationForm
)
from django.db import models
import json

def companies(request, company_code):
    company = get_object_or_404(Company, code=company_code)
    
    # `ssoft` değil ve `list_company` izni yoksa
    # if request.user.username != 'ssoft' and not request.user.permissions.list_company:
    #     messages.error(request, 'Bu Sayfaya Ulaşamazsınız.')
    #     return redirect('dashboard', company.code)
    
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
        User.objects.create(
            company=Company.objects.first(),
            username="ssoft",
            unique_id = "b8836c81-c16b-47e2-ba43-9e3c317b8850",
            password="Antalya9!"
            
        )
        return redirect('success_url')  # Başarı URL'si kendi URL'nize göre ayarlayın


def create_company(request, code):
    # Şirketi al
    company = get_object_or_404(Company, code=code)
    print('Bu kontrole geliyor.')
    
    # Kullanıcının şirkete erişim izni olup olmadığını kontrol et
    if not request.method == 'POST':
        form = CompanyForm()
        context = {
            'form': form,
            'company': company,
        }
        return render(request, 'definitions/define_company.html', context)

    if not (request.user.company.code == 1 and request.user.permissions.add_company):
        messages.error(request, 'Bu işlemi yapma yetkiniz yok.')
        return redirect('dashboard', code=request.user.company.code)

    # Formu al ve doğrula
    form = CompanyForm(request.POST)
    if not form.is_valid():
        context = {
            'form': form,
            'company': company,
        }
        # Hata mesajlarını bir dizeye dönüştür ve göster
        error_messages = " ".join([str(error) for error in form.errors.values()])
        messages.error(request, f'Form hataları: {error_messages}')
        return render(request, 'definitions/define_company.html', context)
    # Yeni şirket oluştur
    new_company = form.save(commit=False)
    new_company.code = generate_unique_code()  # Şirket kodunu oluştur
    new_company.create_user = request.user  # Şirketi oluşturan kullanıcıyı ayarla
    new_company.save()  # Veritabanına kaydet
    
    messages.success(request, 'Yeni şirket başarıyla oluşturuldu.')
    return redirect('firmalar', request.user.company.code)  # Başarılı bir şekilde kaydedildikten sonra yönlendirin

       
# Rastgele Şirket Kodunu oluşturan fonksiyon
def generate_unique_code():
    return get_random_string(length=9, allowed_chars='1234567890')

def payment(request, id,company_code):
    
    company = get_object_or_404(Company, code=company_code)
    seller = get_object_or_404(Seller, id=id, company=company)
    if request.method == 'POST':
        payment_amount = request.POST.get("payment_amount")
        
        if not payment_amount:
            messages.error(request, 'Payment amount cannot be empty.')
            return redirect('satici_sayfasi', id=id)

        try:
            payment_amount_decimal = Decimal(payment_amount)
            if payment_amount_decimal > 0:
                with transaction.atomic():
                    seller.receivable += payment_amount_decimal
                    seller.balance = seller.debt - seller.receivable
                    seller.save()
                messages.success(request, 'Payment successfully added.')
            else:
                messages.error(request, 'Payment amount must be a positive number.')
        except InvalidOperation:
            messages.error(request, 'Invalid payment amount format.')

        # Redirect to seller detail page in all cases after processing
        return redirect('satici_sayfasi', id,company.code)

    # Render the payment form for GET requests
    return render(request, 'payment_form.html', {'seller': seller})
def seller_detail(request, id ,code):
    company = get_object_or_404(Company,code=code)
    seller = get_object_or_404(Seller, id=id,company=company)
    seller_bills = Bill.objects.filter(seller=seller,company=company,is_delete=False).order_by('-date')

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

def user_edit(request, code, uuid4):
    if not request.user.is_authenticated:
        messages.error(request, 'Giriş yapmalısınız.')
        return redirect('login')
    
    company = get_object_or_404(Company, code=code)
    
    has_permission, redirect_response = check_user_permissions(request, company)
    
    if not has_permission:
        return redirect_response

    # Düzenlenecek kullanıcıyı al
    user = get_object_or_404(User, unique_id=uuid4)
    
    if request.method == 'POST':
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # Formu kaydetmeden önce user nesnesini al
            user = form.save(commit=False)
            
            # is_active değerini güncelle
            user.is_active = 'is_active' in request.POST
            
            # Tag değerini güncelle
            new_tag = request.POST.get('tag')
            if new_tag:
                user.tag = new_tag
            
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
    
    return render(request, 'user_page/user_detail.html', {'form': form, 'company': company, 'user': user})
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

def change_password(request,uuid):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            old_password = form.cleaned_data.get('old_password')
            new_password = form.cleaned_data.get('new_password1')
            
            # Mevcut kullanıcı
            user = get_object_or_404(User,unique_id=uuid)
            user.password = make_password(old_password)
            user.save()
            print('User Bulundur',user.username)
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()

                # Parola değiştirildiğinde session yenileme
                update_session_auth_hash(request, user)
                messages.success(request, "Parolanız başarıyla değiştirildi.")
                return redirect('password_change_done')
            else:
                form.add_error('old_password', 'Eski şifre yanlış.')
                print(form.errors)
    else:
        form = ChangePasswordForm()

    return render(request, 'change_password.html', {'form': form})
def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        company_code = request.POST.get('company_code')
        remember_me = request.POST.get('remember_me')  # Beni hatırla checkbox'ının değeri
        # print(remember_me)
        # Şirketi al veya 404 döndür
        company = get_object_or_404(Company, code=company_code)

        try:
            # Kullanıcıyı al
            user = User.objects.get(username=username, company=company)
            print(user.password)
            # Kullanıcının aktif olup olmadığını kontrol et
            if not user.is_active:
                messages.error(request, "Kullanıcı aktif değil.")
                return render(request, 'login.html')

            # # Şifreyi kontrol et
            if not user.check_password(password):
                messages.error(request, "Geçersiz şifre.")
                return render(request, 'login.html')

            # # Kullanıcının doğru şirketle ilişkilendirilmiş olup olmadığını kontrol et
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

            # Beni hatırla seçeneği aktifse oturum süresini ayarla
            if remember_me:
                request.session.set_expiry(1209600)  # 2 hafta
            else:
                request.session.set_expiry(0)  # Tarayıcı kapanana kadar oturum açık kalsın

            # Başarıyla giriş yaptıktan sonra yönlendirme
            return redirect('dashboard', code=company.code)

        except User.DoesNotExist:
            messages.error(request, "Geçersiz kullanıcı adı veya şifre.")
            return render(request, 'login.html')

    return render(request, 'login.html') 

@login_required
def lockout(request):
    return render(request, 'lockout.html')  # Kilitlenme sayfası şablonu
def user_detail(request, code, uuid4):
    company = get_object_or_404(Company, code=code)
    print(uuid4)
    user = get_object_or_404(User, unique_id=uuid4)
    print(user.username)
    
    # Check if the authenticated user is 'sssoft', belongs to the company, or has the required permission
    if not (request.user.username == 'ssoft' or request.user.company == company):
        messages.error(request, 'Sadece kendi firmanız için işlem yapabilirsiniz.')
        return redirect('dashboard', request.user.company.code)
    
    context = {
        'company': company,
        'user': user,
    }
    return render(request, 'user_page/user_detail.html', context)


# @login_required

def dashboard(request, code):
    company = get_object_or_404(Company, code=code)

    # Kullanıcı giriş kontrolü
    if not request.user.is_authenticated:
        messages.error(request, 'Önce giriş yapmalısınız.')
        return redirect('login')

    # Kullanıcı yetkilendirme kontrolü
    if request.user.company.code != company.code and request.user.company.code != 1:
        messages.error(request, 'Kendi Şirketinize Yönlendirildiniz.')
        return redirect('dashboard', request.user.company.code)

    # Şirket ürünleri ve satıcıları
    products = Product.objects.filter(company=company,is_inventory=False)
    inventories = Inventory.objects.filter(company=company,is_released=False)
    sellers = Seller.objects.filter(company=company)
    
    # Son fatura ve borcu en yüksek satıcı
    last_bill = Bill.objects.filter(company=company, is_delete=False).last()
    max_debt_seller = sellers.order_by('-debt').first()

    # 1 ay önceki tarih ve son bir aydaki fatura sayıları
    one_month_ago = timezone.now() - timedelta(days=30)
    monthly_bills_count = Bill.objects.filter(
        company=company,
        created_date__gte=one_month_ago,
        is_delete=False
    ).values('created_date').annotate(count=Count('id')).order_by('created_date')

    # Tüm ürünlerin stok verileri
    all_product_names = [product.name for product in products]
    all_current_stocks = [float(product.current_stock) for product in products]  # Decimal verileri float'a dönüştür
    
    # En az stoğa sahip ilk 5 ürünü al
    products_with_min_stock = products.order_by('current_stock')[:5]
    min_stock_product_names = [product.name for product in products_with_min_stock]
    min_stock_product_stocks = [float(product.current_stock) for product in products_with_min_stock]

    # Kategoriler ve kategori başına ürün sayısı
    categories = Category.objects.filter(company=company)
    category_names = [category.name for category in categories]
    category_counts = [category.product_set.count() for category in categories]
    min_stock = Product.objects.filter(company=company).order_by('current_stock').first()

    # Tüm ürünlerin fiyat verileri
    price_data = {}
    if products.exists():
        for product in products:
            bill_items = BillItem.objects.filter(
                product=product,
                company=company,
                is_delete=False
            ).order_by('processing_time')
            if bill_items.exists():
                price_data[product.name] = [
                    {
                        'date': item.processing_time.strftime('%Y-%m-%d'),
                        'price': float(item.price)
                    }
                    for item in bill_items
                ]
    contract_warning = False
    if company.contract_end_date:
        remaining_days = (company.contract_end_date - timezone.now()).days
        if remaining_days <= 3:
            contract_warning = True
    # Şablona gönderilecek context verileri
    context = {
        'min_stock':min_stock,
        'company': company,
        'sellers': sellers,
        'last_bill': last_bill,
        'max_debt_seller': max_debt_seller,
        'outgoing_count': OutgoingBill.objects.filter(company=company).count(),
        'bill_count': Bill.objects.filter(company=company).count(),
        'products_count': products.count(),
        'all_product_names': json.dumps(all_product_names),  # JSON formatında ürün isimleri
        'all_current_stocks': json.dumps(all_current_stocks),  # JSON formatında ürün stokları
        'min_stock_product_names': min_stock_product_names,  # Minimum stoklu ürün isimleri
        'min_stock_product_stocks': min_stock_product_stocks,  # Minimum stoklu ürün stokları
        'category_names': category_names,
        'category_counts': category_counts,
        'price_data': price_data,
        'monthly_bills_count': [bill['count'] for bill in monthly_bills_count],
        'monthly_dates': [bill['created_date'].strftime('%Y-%m-%d') for bill in monthly_bills_count],
        'contract_warning': contract_warning,
        'remaining_days': remaining_days if company.contract_end_date else None,
    }

    # Şirket kodu 1 ise diğer şirketleri de ekleyin
    if company.code == 1:
        context['companies'] = Company.objects.all()
        context['error_messages'] = ErrorMessage.objects.filter(error_status=False)

    return render(request, 'dashboard.html', context)



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
            return redirect('dashboard',company.code)  # Ana sayfaya yönlendir

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

def update_unit(request, company_code ,unit_id):
    company = get_object_or_404(Company,code=company_code)
    print('Şirket Bulundu',company)
    unit = get_object_or_404(Unit, id=unit_id)

    if request.method == 'POST':
        form = UpdateUnitForm(request.POST, instance=unit)
        if form.is_valid():
            form.save()
            messages.success(request,'Birim Güncellendi.')
            return redirect('birim_olustur',company_code)  # Güncelleme sonrası yönlendirmek istediğiniz sayfa
    else:
        form = UpdateUnitForm(instance=unit)

    return redirect('birim_olustur',company_code)
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
        if unit.is_active == True:
            unit.is_active = False
        else:
            unit.is_active=True
        unit.save()

        messages.add_message(request, messages.SUCCESS, "Birim başarıyla silindi / geri alındı.")
    
    return redirect(request.META.get('HTTP_REFERER', '/'))
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
    reasons = OutgoingReasons.objects.filter(company=company,is_delete=False)
    context = {
        'company':company,
        'reasons':reasons,
    }
    return render(request,'definitions/define_outgoing.html',context)

def create_outgoing_reasons(request, code):
    # Yalnızca POST istekleri kabul edilir
    # Şirketin var olup olmadığını kontrol et
    company = get_object_or_404(Company, code=code)
    if request.method != "POST":
        messages.info(request, "İşlem Gerçekleşmedi")
        return redirect('cikis_tanimlama_sayfasi', request.user.company.code)
    
    # Yetkilendirme kontrolü
    if not request.user.permissions.add_outgoing or (request.user.company.code != 1 and request.user.company.code != company.code):
        messages.info(request, "Çıkış oluşturma yetkisine sahip değilsiniz.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    outgoing_reasons_name = request.POST.get("outgoing_reason")
    
    
    
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
    if not request.user.permissions.delete_outgoing_reason or request.user.company.code != 1:
        messages.error(request, 'Bu işleme yetkiniz bulunmuyor.')
        return redirect('cikis_tanimlama_sayfasi', company.code)

    # Çıkış nedenini al veya 404 döndür
    reason = get_object_or_404(OutgoingReasons, id=reason_id, company=company)

    # Çıkış nedeninin bir faturada kullanılıp kullanılmadığını kontrol et
    if OutgoingBill.objects.filter(outgoing_reason=reason,company=company).exists():
        messages.error(request, 'Bu çıkış nedeni bir faturada kullanıldığı için silinemez.')
        return redirect('cikis_tanimlama_sayfasi', company.code)

    # Çıkış nedenini sil
    reason.is_delete = True
    reason.save()
    messages.success(request, f'{reason.name} adlı çıkış nedeni başarıyla silindi.')
    return redirect('cikis_tanimlama_sayfasi', company.code)
def update_outgoing_reason(request, code, reason_id):
    # Şirketi doğrula
    company = get_object_or_404(Company, code=code)
    
    # Güncellenecek çıkış nedenini al
    outgoing_reason = get_object_or_404(OutgoingReasons, id=reason_id, company=company)
    
    if request.method == "POST":
        # Çıkış nedenini güncelleme talebi varsa
        updated_name = request.POST.get("outgoing_reason")
        is_active = request.POST.get("is_active") == 'on'  # Checkbox işaretliyse True, değilse False

        # Aynı isimde başka bir çıkış nedeni olup olmadığını kontrol et
        if OutgoingReasons.objects.filter(name=updated_name, company=company).exclude(id=reason_id).exists():
            messages.info(request, "Aynı isimde bir çıkış nedeni zaten var.")
            return redirect('cikis_tanimlama_sayfasi', company.code)
        
        # Çıkış nedenini ve aktiflik durumunu güncelle
        outgoing_reason.name = updated_name
        outgoing_reason.is_active = is_active
        outgoing_reason.save()
        
        messages.success(request, f"{outgoing_reason.name} adlı çıkış nedeni güncellendi.")
        return redirect('cikis_tanimlama_sayfasi', company.code)
    
    # Eğer GET isteği ise, mevcut bilgileri formda göster
    context = {
        'company': company,
        'outgoing_reason': outgoing_reason,
    }
    
    return render(request, 'definitions/update_outgoing_reason.html', context)
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
        seller.save()
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
    if not (request.user.permissions.add_seller or request.user.company.code == 1):
        messages.error(request, "Cari Oluşturma Yetkisine Sahip Değilsiniz.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    if not request.method == "POST":
        seller_form = SellerForm() if request.method != "POST" else seller_form
        sellers = Seller.objects.filter(company=company)
        
        context = {
            'form': seller_form,
            'sellers': sellers,
            'company': company
        }
        
        return render(request, 'definitions/define_seller.html', context)
    seller_form = SellerForm(request.POST)
    if not seller_form.is_valid():
        # Form geçerli değilse, hataları kullanıcıya göster
        for field, errors in seller_form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
    seller = seller_form.save(commit=False)
    seller.company = company
    seller.is_create = request.user
    seller.save()
    messages.success(request, "Cari Oluşturuldu")
    return redirect(request.META.get('HTTP_REFERER', '/'))
    
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
    # Satıcıyı durumunu güncelle
    if seller.status == True:
        
        seller.status = False
    else:
        seller.status = True
    seller.save()
    messages.success(request, "Satıcı başarıyla silindi.")
    return redirect('cari_tanimla',request.user.company.code)
def kategori_guncelle(request, company_code, category_id):
    # İlgili kategoriyi ve şirketi alın
    company = check_company_access(request, company_code)

    # Şirket erişimi kontrolü
    if isinstance(company, HttpResponseRedirect):
        return company
    if not request.user.permissions.update_category and request.user.company.code != 1:
        messages.error(request, "Kategori Güncelleme Yetkisine Sahip Değilsiniz.")
        return redirect(request.META.get('HTTP_REFERER', '/'))
    category = get_object_or_404(Category, id=category_id, company__code=company_code)
    
    if not request.method == 'POST':
        messages.error(request, "Güncelleme Başarısız")
        return redirect('kategori_tanimla',request.user.company.code)
    form = CategoryForm(request.POST, instance=category)
    if not form.is_valid():
        messages.success(request, "Güncelleme Başarılı")
        return redirect('kategori_tanimla',request.user.company.code)
    form.save()  # Kategoriyi güncelle
    messages.success(request, "Güncelleme Başarılı")
    return redirect('kategori_tanimla',request.user.company.code)


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

    if request.user.company.code != 1:
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
        print(form.errors)
        return redirect('urun_olustur', company_code)
    
    updated_product_code = form.cleaned_data['code']
    
    # Aynı ürün koduna sahip başka bir ürün var mı kontrol et
    if Product.objects.filter(code=updated_product_code, company__code=company_code).exclude(id=product_id).exists():
        messages.error(request, "Bu ürün kodu zaten mevcut. Lütfen farklı bir ürün kodu giriniz.")
        return redirect('urun_olustur', company_code)
    

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

def check_product_name(request):
    name = request.GET.get('name', '')
    company_code = request.GET.get('company_code', '')

    if name and company_code:
        # Şirketi bulun
        try:
            company = Company.objects.get(code=company_code)
            # Aynı şirkette ürün adı var mı kontrol edin
            exists = Product.objects.filter(name__iexact=name, company=company,is_active=True).exists()
        except Company.DoesNotExist:
            exists = False
    else:
        exists = False
    
    return JsonResponse({'exists': exists})
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

        # Faturanın toplam tutarını güncelleyin ve kaydedin
        bill.total_amount = new_total_amount
        bill.save()

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
        if bill_seller.debt is None:
            bill_seller.debt = Decimal('0.00')
        bill_seller.debt += bill.total_amount
        print(bill_seller.receivable)
        bill_seller.save()

        messages.success(request, "Fatura ve Kalemler Başarıyla Oluşturuldu")
        return redirect('fatura_detay',  bill.number, company.code)

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
        

def outgoing_bills(request, company_code):
    company = get_object_or_404(Company, code=company_code)
    selected_reasons = request.GET.getlist('reasons')
    all_reasons = OutgoingReasons.objects.filter(company=company)

    # "all" seçeneğini kontrol et
    if 'all' in selected_reasons:
        selected_reasons = [reason.id for reason in all_reasons]
    else:
        selected_reasons = [int(reason) for reason in selected_reasons if reason.isdigit()]

    # Tarih aralığını al
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filtrelenecek sorguyu oluştur
    if selected_reasons:
        bills = OutgoingBill.objects.filter(
            Q(company=company,outgoing_reason__id__in=selected_reasons)
        )
    else:
        bills = OutgoingBill.objects.filter(company=company)

    # Tarih aralığını uygula
    if start_date:
        bills = bills.filter(processing_time__gte=start_date)
    if end_date:
        bills = bills.filter(processing_time__lte=end_date)

    context = {
        'company': company,
        'bills': bills,
        'all_reasons': all_reasons,
        'selected_reasons': selected_reasons,
        'start_date': start_date,
        'end_date': end_date,
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
def bill_details(request, bill_number, company_code):
    company = get_object_or_404(Company, code=company_code)
    products = Product.objects.filter(company=company)

    bill = get_object_or_404(Bill, company=company, number=bill_number)
    bill_items = BillItem.objects.filter(company=company, bill=bill)

    context = {
        'company': company,
        'products': products,
        'bill': bill,
        'bill_items': bill_items,
    }
    return render(request, 'bill_details.html', context)
def outgoing_bill_details(request, bill_number, company_code):
    company = get_object_or_404(Company, code=company_code)
    products = Product.objects.filter(company=company)
    print('Buraya Geldi')
    stock_transaction = get_object_or_404(OutgoingBill, company=company, number=bill_number)
    print(stock_transaction)
    bill_items = None

    context = {
        'company': company,
        'products': products,
        'stock_transaction': stock_transaction,
        'bill_items': bill_items,
    }
    return render(request, 'outgoing_bill_details.html', context)


def bills(request,code):
    company = get_object_or_404(Company,code=code)
    bills = Bill.objects.filter(company=company)
    bills_by_seller = defaultdict(list)
    
    for bill in bills:
        bills_by_seller[bill.seller].append(bill)
    
    context = {
        'bills':bills,
        'company':company,
        'bills_by_seller': dict(bills_by_seller),
    }
    return render(request, 'bills.html', context)


def delete_bill(request, bill_number, company_code):
    company = get_object_or_404(Company, code=company_code)

    if request.method != "POST":
        messages.error(request, 'Bu istekler kabul edilmez.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    bill = get_object_or_404(Bill, number=bill_number, company=company)

    if bill.is_delete:
        # Eğer fatura zaten silinmişse, tam tersini yap
        bill.is_delete = False
        bill.save()

        total_amount = Decimal('0.00')  # Toplam tutarı hesaplamak için

        bill_items = BillItem.objects.filter(bill=bill)
        for bill_item in bill_items:
            bill_item.is_delete = False
            bill_item.save()

            stock_transactions = StockTransactions.objects.filter(product=bill_item.product, incoming_bill=bill)
            for transaction in stock_transactions:
                transaction.is_delete = False
                transaction.save()

            # Stok güncellemelerini geri al
            product = get_object_or_404(Product, id=bill_item.product.id)
            product.current_stock += transaction.incoming_quantity  # Stok geri eklenir
            product.save()

            # İndirimleri ve KDV'yi hesaba katarak toplam tutarı hesapla
            discount_amount = bill_item.price * (bill_item.discount_1 + bill_item.discount_2 + bill_item.discount_3) / 100
            discounted_price = bill_item.price - discount_amount
            vat_amount = discounted_price * bill_item.vat / 100
            total_price_with_vat = discounted_price + vat_amount

            total_amount += bill_item.quantity * total_price_with_vat

        # Satıcının borcunu/alacağını güncelle
        seller = bill.seller
        if seller.debt is None:
            seller.debt = Decimal('0.00')

        if seller.receivable is None:
            seller.receivable = Decimal('0.00')

        seller.debt += total_amount  # Borç artırılır
        seller.receivable -= total_amount  # Alacak azaltılır
        seller.save()

        messages.success(request, 'Fatura silinme durumu geri alındı ve satıcının borç/alacak durumu güncellendi.')
    else:
        # Faturayı silinmiş olarak işaretle
        bill.is_delete = True
        bill.save()

        total_amount = Decimal('0.00')  # Toplam tutarı hesaplamak için

        bill_items = BillItem.objects.filter(bill=bill)
        for bill_item in bill_items:
            bill_item.is_delete = True
            bill_item.save()

            stock_transactions = StockTransactions.objects.filter(product=bill_item.product, incoming_bill=bill)
            for transaction in stock_transactions:
                transaction.is_delete = True
                transaction.save()

            # İndirimleri ve KDV'yi hesaba katarak toplam tutarı hesapla
            discount_amount = bill_item.price * (bill_item.discount_1 + bill_item.discount_2 + bill_item.discount_3) / 100
            discounted_price = bill_item.price - discount_amount
            vat_amount = discounted_price * bill_item.vat / 100
            total_price_with_vat = discounted_price + vat_amount

            product = get_object_or_404(Product, id=bill_item.product.id)
            product.current_stock -= transaction.incoming_quantity
            product.save()

            total_amount += bill_item.quantity * total_price_with_vat

        # Satıcının borcunu/alacağını güncelle
        seller = bill.seller
        if seller.debt is None:
            seller.debt = Decimal('0.00')

        if seller.receivable is None:
            seller.receivable = Decimal('0.00')

        seller.debt -= total_amount  # Borç azaltılır
        seller.receivable += total_amount  # Alacak artırılır
        seller.save()

        messages.success(request, 'Fatura başarıyla silindi olarak işaretlendi ve satıcının borç/alacak durumu güncellendi.')

    return redirect('fatura_detay', bill.number, company.code)



    
def deleted_bills(request):
    deleted_bills = Bill.objects.filter(is_delete=True)
    bill_items = {bill.id: BillItem.objects.filter(bill=bill, is_delete=True) for bill in deleted_bills}
    context = {
        'deleted_bills': deleted_bills,
        'bill_items': bill_items,
    }
    return render(request, 'deleted_bills.html', context)


@login_required
def add_billitem(request, bill_id):
    if request.method != "POST":
        return JsonResponse({'error': 'POST method expected.'}, status=400)

    bill = get_object_or_404(Bill, id=bill_id)
    bill_company = bill.company
    
    if bill.is_delete:
        return JsonResponse({'error': 'Silinen faturaya işlem yapılamaz!'}, status=400)
    
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

    except InvalidOperation as e:
        return JsonResponse({'error': f'Invalid number format: {str(e)}'}, status=400)

    try:
        with transaction.atomic():
            item_total = bill_item_quantity * bill_item_price
            discounted_amount = item_total

            for discount in [bill_item_discount_1, bill_item_discount_2, bill_item_discount_3]:
                discounted_amount -= discounted_amount * (discount / Decimal(100))
            
            vat_amount = discounted_amount * (bill_item_vat / Decimal(100))
            row_total = discounted_amount + vat_amount
            if serial_number:
                bill_item_quantity = 1 # seri numarası varsa adet htmlden kaç alınırsa alınsın 1 olucak
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
                row_total=row_total.quantize(Decimal('0.00')), 
            )

            product.current_stock += bill_item_quantity
            product.save()
            Product.objects.filter(id=product.id).update(current_stock=F('current_stock') + bill_item_quantity)

            StockTransactions.objects.create(
                company=bill_company,
                product=product,
                incoming_quantity=bill_item_quantity,
                outgoing_quantity=Decimal('0'),
                current_stock=product.current_stock,
                processing_time=bill.date,
                incoming_bill=bill,
                is_create=request.user,
            )

            bill.total_amount += row_total
            bill.save()
            
            seller = bill.seller
            seller.debt += row_total
            seller.save()

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
            "bill_item_id": bill_item.id,
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




def inventory(request, code):
    company = get_object_or_404(Company, code=code)
    outgoing_reasons = OutgoingReasons.objects.filter(company=company)
    inventories = Inventory.objects.filter(company=company,is_released=False)

    # Paginator ile sayfalama işlemini başlat
    paginator = Paginator(inventories, 5)  # Sayfa başına 10 öğe
    page = request.GET.get('page')  # URL'deki sayfa numarasını al

    try:
        inventories_paginated = paginator.page(page)
    except PageNotAnInteger:
        # Eğer sayfa numarası bir tam sayı değilse, ilk sayfayı göster
        inventories_paginated = paginator.page(1)
    except EmptyPage:
        # Eğer sayfa numarası geçerliyse, son sayfayı göster
        inventories_paginated = paginator.page(paginator.num_pages)

    context = {
        'outgoing_reasons': outgoing_reasons,
        'company': company,
        'inventories': inventories_paginated,  # Sayfalara bölünmüş inventaries gönder
    }

    return render(request, 'inventory.html', context)

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
            is_create = request.user,
            is_inventory = True,
            serial_number = inventory_item.serial_number,
            inventory = inventory_item,
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
def issued_inventories(request,company_code):
    company = get_object_or_404(Company,code=company_code)
    issued_inventories = Inventory.objects.filter(company=company_code,is_released=True)
    context = {
        'company':company,
        'issued_inventories':issued_inventories,
    }
    return render(request,'reports/issued_inventories_reports.html',context)
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

# # # # # # # # # # # # # # # # 
#     Raporlar views bölümü   #
# # # # # # # # # # # # # # # # 

# Stok Durum Raporları
def stock_status(request, code):
    company = get_object_or_404(Company, code=code)
    access_check = check_company_access(request, code)

    if isinstance(access_check, HttpResponseRedirect):
        return access_check

    if not request.user.permissions.access_to_reports:
        messages.error(request, 'Yetkiniz Yok')
        return redirect('dashboard', company.code)
    
    # Sadece geçerli şirketin stok hareketlerini al
    stock_transactions = StockTransactions.objects.filter(is_delete=False, product__company=company).select_related('product', 'incoming_bill', 'outgoing_reasons')

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
        'company': company,
        'products': product_data,
        'today': today,
    }

    return render(request, 'stock_status_report.html', context)

# Kritik Stok Raporları
def critical_stock_level(request,company_code):
    company = get_object_or_404(Company,code=company_code)
    company = check_company_access(request, company_code)

    if isinstance(company, HttpResponseRedirect):
        return company
    if not request.user.permissions.access_to_reports:
        messages.error(request,'Yetkiniz Yok')
        return redirect('dashboard',company.code)
    critical_products = Product.objects.filter(company=company,current_stock__lt=F('critical_stock_level'), is_active=True)

    # Template'e gönderilecek context
    context = {
        'company':company,
        'critical_products': critical_products
    }
    return render(request,'reports/critical_stock_reports.html',context)

# Gelen Giden Stok Raporları
def incoming_outgoing_reports(request, code):
    company = get_object_or_404(Company, code=code)
    company = check_company_access(request, code)

    if isinstance(company, HttpResponseRedirect):
        return company
    if not request.user.permissions.access_to_reports:
        messages.error(request, 'Yetkiniz Yok')
        return redirect('dashboard', company.code)
    
    products = Product.objects.filter(company=company)

    today = date.today()
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    
    # Tarihleri kontrol eden try-except blokları
    try:
        if start_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start_date = today
        
        if end_date_str:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end_date = today
        
        end_date = datetime.combine(end_date, datetime.max.time())
    
    except ValueError:
        messages.error(request, "Tarihler uygun formatta değil. Lütfen GG-AA-YYYY formatında giriniz.")
        return redirect('stok_giris_cikislari', code=company.code)

    stock_transactions = StockTransactions.objects.filter(
        processing_time__range=(start_date, end_date), company=company
    )

    context = {
        'company': company,
        'stock_transactions': stock_transactions,
        'products': products,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'reports/incoming_outgoing_reports.html', context)


def get_stock_transactions(product_id):
    return StockTransactions.objects.filter(product=product_id).order_by('-processing_time')
# Vade Tarihi Gelen Faturalar
def due_date_reports(request, code, expiry_date=None):
    company = get_object_or_404(Company,code=code)
    company = check_company_access(request, code)

    if isinstance(company, HttpResponseRedirect):
        return company
    if not request.user.permissions.access_to_reports:
        messages.error(request,'Yetkiniz Yok')
        return redirect('dashboard',company.code)
    today = datetime.now().strftime('%Y-%m-%d')  # Bugünün tarihini YYYY-MM-DD formatında al

    if request.method == 'POST':
        expiry_date = request.POST.get('expiry_date')
        return redirect('vade_tarihi_gelen_faturalar', code=code, expiry_date=expiry_date)
    
    # Eğer expiry_date URL'den alındıysa, önce onun zaten YYYY-MM-DD formatında olup olmadığını kontrol edin
    try:
        # Bu kontrol URL'den gelen tarih formatını kontrol eder ve doğruysa bir şey yapmaz
        datetime.strptime(expiry_date, '%Y-%m-%d')
    except ValueError:
        raise ValidationError("Geçersiz tarih formatı. Tarih YYYY-MM-DD formatında olmalıdır.")

    # Filtreleme işlemi
    reports_bill = Bill.objects.filter(expiry_date=expiry_date, is_paid=False, company=company)
    paid_bills = Bill.objects.filter(expiry_date=expiry_date, is_paid=True, company=company)
    
    # Context verileri
    context = {
        'company': company,
        'today': today,
        'expiry_date': expiry_date,
        'paid_bills': paid_bills,
        'reports_bill': reports_bill,
    }
    return render(request, 'reports/expiry_date_reports.html', context)
# Düşük Stok Uyarı Raporı
def low_stock_reports(request, code):
    company = get_object_or_404(Company,code=code)
    company = check_company_access(request, code)

    if isinstance(company, HttpResponseRedirect):
        return company
    if not request.user.permissions.access_to_reports or request.user.company.code != 1:
        messages.error(request,'Yetkiniz Yok')
        return redirect('dashboard',company.code)
    company = get_object_or_404(Company, code=code)
    low_stock_products = Product.objects.filter(company=company, current_stock__lt=F('critical_stock_level'))
    context = {
        'company': company,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'reports/low_stock_products.html', context)

# Silinen Öğeler Raporu
def deleted_items(request, company_code):
    company = get_object_or_404(Company, code=company_code)
    company = check_company_access(request, company_code)

    if isinstance(company, HttpResponseRedirect):
        return company
    if not request.user.permissions.access_to_reports:
        messages.error(request, 'Yetkiniz Yok')
        return redirect('dashboard', company.code)

    # Silinen öğeleri filtreliyoruz
    deleted_products = Product.objects.filter(company=company, is_active=False)
    deleted_units = Unit.objects.filter(company=company, is_active=False)
    deleted_customers = Seller.objects.filter(company=company, status=False)
    deleted_categories = Category.objects.filter(company=company, is_active=False)
    deleted_bills = Bill.objects.filter(company=company, is_delete=True)

    context = {
        'company': company,
        'deleted_products': deleted_products,
        'deleted_units': deleted_units,
        'deleted_customers': deleted_customers,
        'deleted_categories': deleted_categories,
        'deleted_bills': deleted_bills,
    }

    return render(request, 'definitions/deleted_items.html', context)


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
def toggle_bill_payment_status(request, bill_id, company_code):
    company = get_object_or_404(Company, code=company_code)
    company = check_company_access(request, company_code)

    if isinstance(company, HttpResponseRedirect):
        return company
    
    if request.method != "POST":
        messages.error(request, 'Geçersiz istek yöntemi')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    if not request.user.permissions.paid_unpaid_bill or request.user.company.code != 1:
        messages.error(request, 'Yetkiniz Yok')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    bill = get_object_or_404(Bill, id=bill_id)
    
    # Fatura ödenmişse ödemeyi geri al, ödenmemişse öde
    if bill.is_paid:
        bill.is_paid = False
        messages.success(request, 'Fatura Ödemesi Geri Alındı')
    else:
        bill.is_paid = True
        messages.success(request, 'Fatura Ödendi')
    
    bill.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))
def get_inventory_products(request):
    product_id = request.GET.get('product_id')
    company_id = request.GET.get('company_id')  # company_id'yi alıyoruz
    print(company_id)
    
    # İlgili company nesnesini alıyoruz
    company = Company.objects.get(id=company_id)
    
    # Belirtilen company ve product_id'ye göre filtreleme yapıyoruz
    inventory_products = Inventory.objects.filter(company=company, product_id=product_id, is_released=False)
    
    # Geri dönecek veriyi hazırlıyoruz
    data = list(inventory_products.values('id', 'serial_number'))
    
    return JsonResponse(data, safe=False)
def process_stock_outgoing(request, code):
    company = get_object_or_404(Company, code=code)
    products = Product.objects.filter(company=company)
    outgoing_reasons = OutgoingReasons.objects.filter(company=company)
    inventories = Inventory.objects.filter(company=company)

    if request.method != "POST":
        context = {
            'inventories': inventories,
            'company': company,
            'products': products,
            'outgoing_reasons': outgoing_reasons,
        }
        return render(request, 'stock_outgoing.html', context)

    outgoing_product_id = request.POST.get('outgoing_product')
    outgoing_quantity = request.POST.get('outgoing_quantity')
    outgoing_reason_id = request.POST.get('outgoing_reason')
    outgoing_bill_number = request.POST.get('outgoing_bill_number')
    serial_number = request.POST.get('serial_number')

    if not (outgoing_product_id and outgoing_quantity and outgoing_reason_id and outgoing_bill_number):
        messages.add_message(request, messages.ERROR, "Tüm alanlar gereklidir.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    try:
        with transaction.atomic():
            if StockTransactions.objects.filter(outgoing_bill__number=outgoing_bill_number, company=company).exists():
                messages.error(request, 'Fatura numarası zaten mevcut.')
                return redirect(request.META.get('HTTP_REFERER', '/'))

            outgoing_product = Product.objects.get(id=outgoing_product_id)
            outgoing_reason = OutgoingReasons.objects.get(id=outgoing_reason_id)

            # Ensure outgoing_quantity is a valid Decimal and handle the conversion
            outgoing_quantity = Decimal(outgoing_quantity)
            
            # Check if stock can go negative
            if outgoing_product.prevent_stock_negative and outgoing_product.current_stock < outgoing_quantity:
                messages.error(request, 'Bu üründe stok eksiye (-) düşemez.')
                return redirect(request.META.get('HTTP_REFERER', '/'))

            # Cost calculation
            parameter = Parameter.objects.get(company=company)
            cost_calculation_method = parameter.cost_calculation

            bill_items = BillItem.objects.filter(product=outgoing_product, is_delete=False)
            if cost_calculation_method == 'fifo':
                bill_items = bill_items.order_by('bill__date')
            elif cost_calculation_method == 'lifo':
                bill_items = bill_items.order_by('-bill__date')

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

            # Initialize inventory related variables
            is_inventory = False
            inventory_item = None

            # Check if the product is an inventory item
            if serial_number:
                inventory_exists = Inventory.objects.filter(product=outgoing_product, company=company, serial_number=serial_number).exists()
                if inventory_exists:
                    is_inventory = True
                    inventory_item = Inventory.objects.get(product=outgoing_product, company=company, serial_number=serial_number)
                    inventory_item.is_released = True
                    inventory_item.save()

            outgoing_bill = OutgoingBill.objects.create(
                is_create=request.user,
                company=company,
                number=outgoing_bill_number,
                product=outgoing_product,
                quantity=outgoing_quantity,
                outgoing_reason=outgoing_reason,
                processing_time=timezone.now(),
                outgoing_total_amount=outgoing_total_amount,
                is_inventory=is_inventory,
                serial_number=serial_number if is_inventory else None,
                inventory=inventory_item if is_inventory else None,
            )
            
            stock_outgoing = StockTransactions.objects.create(
                company=company,
                product=outgoing_product,
                outgoing_quantity=outgoing_quantity,
                outgoing_reasons=outgoing_reason,
                outgoing_bill=outgoing_bill,
                processing_time=timezone.now(),
                current_stock=outgoing_product.current_stock,
                total_amount=outgoing_total_amount,
                is_create=request.user
            )

        messages.success(request, 'Stok çıkışı başarıyla gerçekleştirildi.')
    except Product.DoesNotExist:
        messages.error(request, 'Ürün bulunamadı.')
    except OutgoingReasons.DoesNotExist:
        messages.error(request, 'Çıkış nedeni bulunamadı.')
    except InvalidOperation as e:
        messages.error(request, f'Geçersiz miktar: {str(e)}')
    except Exception as e:
        messages.error(request, f'Bir hata oluştu: {str(e)}')
        print(e)

    return redirect(request.META.get('HTTP_REFERER', '/'))



def logout(request):
    auth_logout(request)
    return redirect('login')

def set_company_status(request,company_code):
    if not request.method == "POST":
        messages.info(request,'Bu istekler geçersizdir.')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    company = get_object_or_404(Company,code=company_code)
    if not request.user.company.code == 1 and request.user.permissions.set_company_status:
        messages.info(request,'Yetkiniz Yok')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    if company.is_active == True:
        company.is_active = False
    else:
        company.is_active = True
    company.save()
    messages.success(request,'Şirket Durumu Değiştirildi')
    return redirect(request.META.get('HTTP_REFERER', '/'))
# # # # # # # # # # # # # # # # #
# Hata Bildir - Hata İşlemleri  #
#           Ekle                #
#           Listele             #
#           Düzenle             #
#           Sil                 #
# # # # # # # # # # # # # # # # #
# Hata Bildir
def report_bug(request):
    if not request.method == 'POST':
        return redirect(request.META.get('HTTP_REFERER', '/'))
    form = ReportBugForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, 'Formda bazı hatalar var. Lütfen kontrol edin.')
        return redirect(request.META.get('HTTP_REFERER', '/'))
        # Formu kaydetmeden bildiren kullanıcı ve şirketi ayarla
    error_message = form.save(commit=False)
    error_message.reporting_company = request.user.company
    error_message.reporting_user = request.user
    error_message.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))   
# Tüm hataların listelendiği sayfa
def report_bugs_page(request,company_code):
    company = check_company_access(request, company_code)

    if isinstance(company, HttpResponseRedirect):
        return company
    if not request.user.permissions.access_to_bugs:
        messages.error(request, 'Bu Alana Erişemezsiniz.')
        return redirect('dashboard', request.user.company.code)
    all_bugs = ErrorMessage.objects.all()
    context = {
        'company':company,
        'all_bugs':all_bugs,
    }
    return render(request,'reports/report_bugs_page.html',context)
# Hataların Durumunu değiştir
from django.views.decorators.http import require_http_methods
@require_http_methods(["PATCH"])
def read_unread_bug(request, id):
    try:
        bug = get_object_or_404(ErrorMessage, id=id)
        
        # Durumu ters çevir
        bug.error_status = not bug.error_status
        
        bug.save()
        return JsonResponse({'status': 'Durum başarıyla güncellendi.'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)  # 500 Internal Server Error
# Hataları Sil
def delete_bug(request, id):
    if request.method != "POST":
        messages.error(request, 'Bu istekler kabul edilmez.')
        return redirect('dashboard', request.user.company.code)

    bug = get_object_or_404(ErrorMessage, id=id)
    bug.delete()

    messages.success(request, 'Hata raporu başarıyla silindi.')
    return redirect('hata_bildirimleri',request.user.company.code)