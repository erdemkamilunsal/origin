from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
import json
import pytz
from django.db.models import DateField, ExpressionWrapper
from datetime import timedelta, datetime
from .models import ChannelData, LatestDataTable, SocialMediaPost
from django.db.models import Sum
import matplotlib.pyplot as plt
import io
import base64
from django.utils import timezone


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Kullanıcıyı doğrulama işlemi
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)  # Kullanıcıyı giriş yaptı olarak işaretle
                return redirect('index')  # Ana sayfaya yönlendir
            else:
                messages.error(request, "Geçersiz kullanıcı adı veya şifre")
        else:
            messages.error(request, "Geçersiz form")
    else:
        form = AuthenticationForm()

    return render(request, "login.html", {"form": form})

def logout_view(request):
    logout(request)  # Kullanıcıyı oturumdan çıkar
    return redirect('login')  # Login sayfasına yönlendir

@login_required
def finance_primary(request):
    data = ChannelData.objects.filter(source_category="finans", selective_part="primary")
    return render(request, 'finance_primary.html', {'data': data})

@login_required
def finance_selective(request):
    data = ChannelData.objects.filter(source_category="finans", selective_part="selective")
    return render(request, 'finance_selective.html', {'data': data})

@login_required
def finance_corporate(request):
    data = ChannelData.objects.filter(source_category="finans", selective_part="corporate")
    return render(request, 'finance_corporate.html', {'data': data})

@login_required
def mey_primary(request):
    data = ChannelData.objects.filter(source_category="mey", selective_part="primary")
    return render(request, 'mey_primary.html', {'data': data})

@login_required
def mey_selective(request):
    data = ChannelData.objects.filter(source_category="mey", selective_part="selective")
    return render(request, 'mey_selective.html', {'data': data})

@login_required
def snacks_primary(request):
    data = ChannelData.objects.filter(source_category="snacks-tr", selective_part="primary")
    return render(request, 'snacks_primary.html', {'data': data})

@login_required
def snacks_selective(request):
    data = ChannelData.objects.filter(source_category="snacks-tr", selective_part="selective")
    return render(request, 'snacks_selective.html', {'data': data})

@login_required
def snacks_corporate(request):
    data = ChannelData.objects.filter(source_category="snacks-tr", selective_part="corporate")
    return render(request, 'snacks_corporate.html', {'data': data})

@login_required
def mey_int_primary(request):
    data = ChannelData.objects.filter(source_category="mey-international", selective_part="primary")
    return render(request, 'mey_int_primary.html', {'data': data})

@login_required
def index(request):
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    today = datetime.now(istanbul_tz)

    base_urls = {
        "finans": ["corporate", "selective", "primary"],
        "mey": ["primary", "selective"],
        "snacks-tr": ["corporate", "primary", "selective", "corprimary", "pladis_categories"],
        "mey-international": ["primary"]
    }

    industry_data = {}

    for industry, categories in base_urls.items():
        for category in categories:
            last_7_days_data = []
            for i in range(7):
                date_start = today - timedelta(days=i)
                date_end = date_start + timedelta(days=1)  # Bitiş tarihini bir gün sonrasına alıyoruz
                date_str = date_start.strftime("%Y-%m-%d")

                # `total` değerlerini alıyoruz ve toplamları değil, her bir kaydın `total` değerini alıyoruz
                total_content = LatestDataTable.objects.filter(
                    source_category=industry,
                    selective_part=category,
                    source="instagram_comment",
                    created_time__gte=date_start.date(),  # Sadece tarih filtreleme
                    created_time__lt=date_end.date()  # ve bitiş tarihi
                ).aggregate(Sum('total'))['total__sum'] or 0  # Toplam içerik sayısını alıyoruz

                last_7_days_data.append({"date": date_str, "total_content": total_content})

            industry_data[f"{industry}-{category}"] = last_7_days_data[::-1]  # Ters çevirip sıralı hale getiriyoruz

    # SocialMediaPost modelinden tüm paylaşımları alıyoruz
    posts = SocialMediaPost.objects.all()

    return render(request, "index.html", {
        "industry_data": json.dumps(industry_data),
        "posts": posts  # Bu satır ile SocialMediaPost verilerini şablona geçiyoruz
    })

def select_channel(request):
    channels_to_find = {
        "twitter", "facebook", "facebook_page_comment", "facebook_page_like",
        "youtube", "youtube_shorts", "instagram", "instagram_comment",
        "tiktok", "pinterest", "rss", "apple_app_store_comment",
        "google_play_store_comment", "linkedin", "donanimhaber", "eksi_sozluk",
        "inci_sozluk", "sikayetvar", "uludag_sozluk"
    }

    # Eğer bir kanal seçildiyse, channel_dashboard'a yönlendirme yap
    if request.GET.get('channel_name'):
        channel_name = request.GET['channel_name']
        return redirect('channel_dashboard', channel_name=channel_name)

    return render(request, 'select_channel.html', {'channels_to_find': channels_to_find})

def channel_dashboard(request, channel_name):
    # İstanbul saat dilimi
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    today = timezone.now().date()

    # Base_urls her endüstri ve kategori için tanımlandı
    base_urls = {
        "finans": ["corporate", "selective", "primary"],
        "mey": ["primary", "selective"],
        "snacks-tr": ["corporate", "primary", "selective", "corprimary", "pladis_categories"],
        "mey-international": ["primary"]
    }

    social_media_data = {}

    # Seçilen kanal için her endüstri ve kategori için son 7 gün verisini çekiyoruz
    for industry, categories in base_urls.items():
        for category in categories:
            last_7_days_data = []
            for i in range(7):
                # Her gün için tarih hesaplaması
                record_date = today - timedelta(days=i)
                date_str = record_date.strftime("%Y-%m-%d")

                # Veritabanından o gün için verileri çekiyoruz
                daily_records = LatestDataTable.objects.filter(
                    source_category=industry,
                    selective_part=category,
                    source=channel_name,
                    created_time=record_date
                ).values_list("total", flat=True)

                last_7_days_data.append({
                    "date": date_str,
                    "total_content": list(daily_records)
                })

            # İlgili endüstri ve kategori için verileri dictionary'ye ekliyoruz
            social_media_data[f"{industry}-{category}"] = last_7_days_data[::-1]

    # Verileri şablona gönderiyoruz
    return render(request, "channel_dashboard.html", {
        "social_media_data": social_media_data,  # JSON verisini şablona gönderiyoruz, artık direk JSON değil
        "channel_name": channel_name
    })

def base_context(request):
    channels_to_find = [
        "twitter", "facebook", "facebook_page_comment", "facebook_page_like",
        "youtube", "youtube_shorts", "instagram", "instagram_comment",
        "tiktok", "pinterest", "rss", "apple_app_store_comment",
        "google_play_store_comment", "linkedin", "donanimhaber", "eksi_sozluk",
        "inci_sozluk", "sikayetvar", "uludag_sozluk"
    ]
    return {
        'channels_to_find': channels_to_find
    }
