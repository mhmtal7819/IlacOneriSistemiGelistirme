from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.hashers import make_password
import pandas as pd
#from .forms import SearchForm
from .models import User,UserMedication,Medication
from django.db import connection
from django.utils import timezone
from django.utils.timezone import now
import datetime

def login(request): #giris
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password) #kullanıcı kontrol
        
        if user is not None:
            auth_login(request, user) #giris
            if username == 'yonetici':
                return redirect('admin:index')  # Yönlendirme ismini doğru bir şekilde kullanıyoruz.
            return redirect('home')
        
        else:
            error_message = "Kullanıcı adı veya şifre yanlış!"
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')

def sifremiUnuttum(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']

        # Kullanıcı adının varlığını kontrol et
        user = AuthUser.objects.filter(username=username).first()
        if user:
            # Şifrelerin eşleşip eşleşmediğini kontrol et
            if password == password2:
                # Şifreyi güncelle
                user.set_password(password)
                user.save()
                messages.success(request, 'Şifreniz başarıyla güncellendi.')
                return redirect('login')  # Kullanıcıyı giriş sayfasına yönlendir
            else:
                messages.error(request, 'Girilen şifreler eşleşmiyor.')
                return render(request, 'sifremiUnuttum.html', {'error': 'Girilen şifreler eşleşmiyor.'})
        else:
            messages.error(request, 'Bu kullanıcı adı ile bir hesap bulunamadı.')
            return render(request, 'sifremiUnuttum.html', {'error': 'Bu kullanıcı adı ile bir hesap bulunamadı.'})
    else:
        # GET request için formu göster
        return render(request, 'sifremiUnuttum.html')

def yoneticiGiris(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password) #kullanıcı kontrol
        if user is not None:
            auth_login(request, user) #giris
            if username == 'yonetici':
                return redirect('admin:index')  # Yönlendirme ismini doğru bir şekilde kullanıyoruz.
        else:
            error_message = "Kullanıcı adı veya şifre yanlış!"
            return render(request, 'yoneticiGiris.html', {'error_message': error_message})
    return render(request, 'yoneticiGiris.html')

def home(request):
    return render(request,'home.html')

def bilgilerim(request):
    try:
        # request.user.username kullanarak özelleştirilmiş User modelinizden kullanıcıyı çekin
        user_profile = User.objects.get(username=request.user.username)
        user_auth = AuthUser.objects.get(username=request.user.username)
        height_in_meters = user_profile.height / 100  # cm'den metreye çevir
        bmi = user_profile.weight / (height_in_meters * height_in_meters)  # BMI hesaplama

        # User modelinize bağlı UserMedication sorgusu ilaçları gösterme
        user_medications = UserMedication.objects.filter(user=user_profile).select_related('medication')
        medications = [
            (um.medication.name, um.medication.active_ingredient, um.medication.allergens,
             um.medication.kronik_rahatsizlik, um.medication.arac_kullanimi, um.medication.kullanım_suresi, um.medication.kullanım_talimatı)
            for um in user_medications
        ]

        context = {
            'user_profile': {
                'name': user_profile.name,
                'last_name': user_auth.last_name,
                'height': user_profile.height,
                'weight': user_profile.weight,
                'age': user_profile.age,
                'gender': user_profile.gender,
                'bmi': bmi
            },
            'medications': medications,
            'bmi_warning': None  # Varsayılan olarak uyarı yok
        }
        if bmi < 18.5:
            context['bmi_warning'] = 'Dikkat, vücut kitle indeksiniz düşük!'
        elif bmi > 25:
            context['bmi_warning'] = 'Dikkat, vücut kitle indeksiniz yüksek!'
        
        return render(request, 'bilgilerim.html', context)
    except User.DoesNotExist:
        messages.error(request, "Kullanıcı bulunamadı.")
        return render(request, 'bilgilerim.html', {'medications': []})

def ilaclarım(request):
    try:
        # request.user.username kullanarak özelleştirilmiş User modelinizden kullanıcıyı çekin
        user_profile = User.objects.get(username=request.user.username)
        user_auth = request.user  # AuthUser yerine request.user kullanabilirsiniz
        height_in_meters = user_profile.height / 100  # cm'den metreye çevir
        bmi = user_profile.weight / (height_in_meters * height_in_meters)  # BMI hesaplama

        # User modelinize bağlı UserMedication sorgusu ilaçları gösterme
        user_medications = UserMedication.objects.filter(user=user_profile).select_related('medication')
        medications = []
        for um in user_medications:
            medication = um.medication
            total_days = medication.kullanım_suresi.days
            elapsed_days = (timezone.now().date() - um.date_suggested).days
            remaining_days = total_days - elapsed_days
            medications.append((
                medication.name,
                medication.active_ingredient,
                medication.allergens,
                medication.kronik_rahatsizlik,
                medication.arac_kullanimi,
                remaining_days,
                medication.kullanım_talimatı
            ))

        context = {
            'user_profile': {
                'name': user_profile.name,
                'last_name': user_auth.last_name,
                'height': user_profile.height,
                'weight': user_profile.weight,
                'age': user_profile.age,
                'gender': user_profile.gender,
                'bmi': bmi
            },
            'medications': medications,
            'bmi_warning': None  # Varsayılan olarak uyarı yok
        }
        if bmi < 18.5:
            context['bmi_warning'] = 'Dikkat, vücut kitle indeksiniz düşük!'
        elif bmi > 25:
            context['bmi_warning'] = 'Dikkat, vücut kitle indeksiniz yüksek!'
        
        return render(request, 'ilaclarım.html', context)
    except User.DoesNotExist:
        messages.error(request, "Kullanıcı bulunamadı.")
        return render(request, 'ilaclarım.html', {'medications': []})

    

def contact(request):
    return render(request,'contact.html')

def register(request): #kayıt
    if request.method == "POST":
        name = request.POST.get('name')
        surname = request.POST.get('surname')
        age = request.POST.get('age')  
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        username = request.POST.get('username')
        gender = request.POST.get('gender')
        mail = request.POST.get('mail')
        password = request.POST.get('password')
        password2 = request.POST.get('password2') #kyllanııc bilgileri alma

        # Veri doğrulama (validation)
        if User.objects.filter(username=username).exists() or AuthUser.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Kullanıcı adı zaten mevcut'})
        elif password != password2:
            return render(request, 'register.html', {'error': 'Parolalar eşleşmiyor'})
        else:
            # Kullanıcıyı oluştur
            user = User(
                name=name,
                surname=surname,
                height=height,
                weight=weight,
                age=age,
                username=username,
                gender=gender
            )
            #user.set_password(password)  # Şifreyi güvenli bir şekilde kaydedin
            user.save()

            # Django'nun dahili User modelini kullanarak kullanıcı oluştur
            auth_user = AuthUser.objects.create_user(
                username=username,
                email=mail,
                password=password,
                first_name=name,
                last_name=surname
            )
            auth_user.save()
            return redirect('login')  # Başarıyla kayıt olduktan sonra kullanıcıyı giriş sayfasına yönlendir
    else:
        return render(request, 'register.html')

    return render(request, 'register.html')

@login_required
def bilgiGuncelle(request):
    try:
        user_profile = User.objects.get(username=request.user.username)
    except User.DoesNotExist:
        messages.error(request, "Kullanıcı bulunamadı.")
        return redirect('bilgilerim')

    if request.method == 'POST':
        user_profile.name = request.POST['name']
        user_profile.last_name = request.POST['last_name']
        user_profile.age = request.POST['age']
        user_profile.height = request.POST['height']
        user_profile.weight = request.POST['weight']
        user_profile.gender = request.POST['gender']
        user_profile.save()
        messages.success(request, 'Bilgileriniz başarıyla güncellendi.')
        return redirect('bilgilerim')

    context = {
        'user_profile': user_profile
    }
    return render(request, 'bilgiGuncelle.html', context)

def index(request): #anasayfa
    if not request.user.is_authenticated:
        return redirect('login')

    try:
        # request.user.username kullanarak özelleştirilmiş User modelinizden kullanıcıyı çekin
        user_profile = User.objects.get(username=request.user.username)
        user_auth = AuthUser.objects.get(username=request.user.username)
        height_in_meters = user_profile.height / 100  # cm'den metreye çevir
        bmi = user_profile.weight / (height_in_meters * height_in_meters)  # BMI hesaplama


        # User modelinize bağlı UserMedication sorgusu ilaçları gösterme
        user_medications = UserMedication.objects.filter(user=user_profile).select_related('medication')
        medications = [
            (um.medication.name, um.medication.active_ingredient, um.medication.allergens)
            for um in user_medications
        ]

        context = {
            'user_profile': {
                'name': user_profile.name,
                'last_name': user_auth.last_name,
                'height': user_profile.height,
                'weight': user_profile.weight,
                'age': user_profile.age,
                'gender': user_profile.gender,  
                'bmi': bmi
            },
            'medications': medications,
            'bmi_warning': None  # Varsayılan olarak uyarı yok
        }
        if bmi < 18.5:
            context['bmi_warning'] = 'Dikkat, vücut kitle indeksiniz düşük!'
        elif bmi > 25:
            context['bmi_warning'] = 'Dikkat, vücut kitle indeksiniz yüksek!'

        return render(request, 'index.html', context)
    except User.DoesNotExist:
        messages.error(request, "Kullanıcı bulunamadı.")
        return redirect('login')


def signout(request):
    logout(request)
    messages.success(request,"Çıkış Yapıldı")
    return redirect('login')

def returnIndex(request):
    return redirect('index')


def get_dataframe_from_sqlite():
    # Assuming connection setup and pandas are properly imported
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user_medication")
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()

    df = pd.DataFrame(data, columns=columns)
    df.rename(columns={
        'name': 'İlaç Adı',
        'active_ingredient': 'Hastalık',
        'allergens': 'Etken Madde',
        'chronic_condition': 'Kronik Rahatsızlık',
        'driving_usage': 'Araç Kullanımı'
    }, inplace=True)
    return df

def medReq(request):
    # Sorgu parametrelerini başlatma
    hastaliklar = request.POST.getlist('hastalik[]')  # Daha önce 'hastalik' olarak aldığınız yerde listeyi doğru şekilde almak için getlist kullanın.
    alerjenler = request.POST.getlist('alerjen[]')
    secilen_ilac = request.POST.get('secilen_ilac', None)
    
    # Veri çekme işlemleri
    active_ingredients = list(Medication.objects.order_by('active_ingredient').values_list('active_ingredient', flat=True).distinct())
    allergen_set = set()
    medications = Medication.objects.all()
    for medication in medications:
        allergen_set.update([allergen.strip() for allergen in medication.allergens.split(',') if allergen.strip()])
    allergens = sorted(allergen_set)  # Convert set to a sorted list
    allergens.insert(0, 'Alerjim Yok')

    context = {
        'active_ingredients': active_ingredients,
        'allergens': allergens,
        'html_table': 'ilaclar'
    }

    if request.method == "POST":
        if hastaliklar:
            ilaclar_df = get_dataframe_from_sqlite()
            filter = ilaclar_df['Hastalık'].isin(hastaliklar)  # hastaliklar listesini doğru şekilde kullanın
            if alerjenler and 'Alerjim Yok' not in alerjenler:
                filter &= ~ilaclar_df['Etken Madde'].apply(lambda x: any(alerjen in x for alerjen in alerjenler))
            uygun_ilaclar = ilaclar_df[filter]
            context['html_table'] = uygun_ilaclar.to_html(index=False, classes='table table-striped')

        elif secilen_ilac:
            kullanici_id = request.user.id
            userMed = UserMedication(
                user_id=kullanici_id,
                medication_id=secilen_ilac,
                date_suggested=now(),
                accepted=True
            )
            userMed.save()
            messages.success(request, 'İlaç onaylandı.')
            return render(request, 'medReq.html', {'error': 'İlaç onaylandı.'})

    return render(request, 'medReq.html', context)



def data(request): #kullanılmıyor
    # Session'dan DataFrame'i çekelim
    json_ilaclar = request.session.get('uygun_ilaclar', None)
    if json_ilaclar:
        uygun_ilaclar = pd.read_json(json_ilaclar, orient='split')

        # DataFrame'i HTML tablosuna çevirelim
        html_table = uygun_ilaclar.to_html()
    else:
        html_table = "Uygun ilaç bulunamadı."

    return render(request, 'data.html', {'html_table': html_table})