# views.py
from django.shortcuts import render
from .models import ChannelData,ScraperLog
from django.db.models import Max
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta



@login_required
def index(request):
    base_url_data = {}

    # Belirtilen base URL'ler
    base_urls = ["finans", "mey", "snacks-tr", "mey-international"]

    # Kategoriler: corporate, selective, primary
    categories = ["corporate", "selective", "primary"]

    for base_url in base_urls:
        category_data = {}
        for category in categories:
            # Bu base_url ve category için en son eklenen veriyi alıyoruz
            channel_data = ChannelData.objects.filter(source_category=base_url, selective_part=category).order_by('-created_time')

            # Veriyi ilgili kategoriye ekliyoruz
            category_data[category] = channel_data

        # Tüm kategorilerle birlikte base_url'i base_url_data'ya ekliyoruz
        base_url_data[base_url] = category_data

    # Verileri index.html'e gönderiyoruz
    return render(request, 'index.html', {'base_url_data': base_url_data})

def filtersbycomment(request):
    return render(request, 'filtersbycomment.html')

class CustomLoginView(LoginView):
    template_name = 'login.html'  # Giriş sayfası şablonu
    redirect_authenticated_user = True  # Giriş yapmış kullanıcıyı doğrudan yönlendir

@login_required
def custom_logout(request):
    logout(request)  # Kullanıcıyı çıkış yapar
    return HttpResponseRedirect('/login/')  # Çıkış yapıldıktan sonra login sayfasına yönlendir

@login_required
def user_status(request):
    # Son 10 dakika içinde aktif olan kullanıcıları bulma
    active_time_threshold = timezone.now() - timedelta(minutes=10)

    # Aktif ve pasif kullanıcıları ayırmak
    active_users = User.objects.filter(last_login__gte=active_time_threshold)
    passive_users = User.objects.filter(last_login__lt=active_time_threshold)

    return render(request, 'user_status.html', {
        'active_users': active_users,
        'passive_users': passive_users,
    })

def finance_corporate(request):
    data = ChannelData.objects.filter(source_category="finans", selective_part="corporate")
    return render(request, 'base.html', {'finance_data': data})

def finance_selective(request):
    data = ChannelData.objects.filter(source_category="finans", selective_part="selective")
    return render(request, 'base.html', {'finance_data': data})

def finance_primary(request):
    data = ChannelData.objects.filter(source_category="finans", selective_part="primary")
    return render(request, 'base.html', {'finance_data': data})

def index(request):
    # Scraper son güncelleme tarihini alıyoruz
    last_update = ScraperLog.objects.first()  # En son güncellenen log kaydını alıyoruz

    if last_update:
        last_update_time = last_update.last_update
    else:
        last_update_time = "Veri bulunamadı"  # Eğer hiç log yoksa

    # finance_data verilerini alıyoruz
    finance_data = ChannelData.objects.filter(source_category='finans')

    return render(request, '', {
        'finance_data': finance_data,
        'last_update': last_update_time
    })