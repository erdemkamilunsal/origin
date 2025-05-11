from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
import json
import pytz
from django.db.models import DateField, ExpressionWrapper
from datetime import timedelta, datetime
from .models import LatestData, Latest7Days, MostSharedContent  # Model isimleri güncellendi
from django.db.models import Sum
import matplotlib.pyplot as plt
import io
import base64
from django.utils import timezone
from .forms import YouTubeURLForm
import requests
import re


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
def index(request):
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    today = datetime.now(istanbul_tz)

    base_urls = {
        "finans": ["corporate", "selective", "primary"],
        "mey": ["primary", "selective"],
        "snacks-tr": ["corporate", "primary", "selective", "corprimary", "pladis_categories"],
        "mey-international": ["primary"],
        "fastfood-tr": ["corporate"],
        "transportation-tr": ["corporate"],
        "airtravel-tr": ["corporate"]
    }
    # MostSharedContent modelinden tüm paylaşımları alıyoruz
    posts = MostSharedContent.objects.all()  # SocialMediaPost -> MostSharedContent

    return render(request, "index.html", {
        "posts": posts,  # Bu satır ile MostSharedContent verilerini şablona geçiyoruz
    })

@login_required
def most_engaged_content(request, category, subcategory, source):
    # URL'den gelen parametreleri küçük harfe çevir
    category_lower = category.lower()
    subcategory_lower = subcategory.lower()
    source_lower = source.lower()

    # Eğer URL'deki parametreler küçük harf değilse, küçük harfe yönlendir
    if (category != category_lower or subcategory != subcategory_lower or source != source_lower):
        return redirect('most_engaged_content', category=category_lower, subcategory=subcategory_lower, source=source_lower)

    # Veritabanından ilgili filtrelemeyi yap (küçük harfe çevrilmiş parametrelerle)
    contents = MostSharedContent.objects.filter(
        source_category__iexact=category_lower,  # Büyük-küçük harf duyarsız filtreleme
        selective_part__iexact=subcategory_lower,
        source__iexact=source_lower
    ).order_by('-created_time')

    # Template'e verileri gönder
    return render(request, 'most_engaged_content.html', {
        'contents': contents,
        'category': category,  # Orijinal kategori adını gönder
        'subcategory': subcategory,  # Orijinal alt kategori adını gönder
        'source': source  # Orijinal kaynak adını gönder
    })

@login_required
def channel_dashboard(request, channel_name):
    # İstanbul saat dilimi
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    today = timezone.now().date()

    # Base_urls her endüstri ve kategori için tanımlandı
    base_urls = {
        "finans": ["corporate", "selective", "primary"],
        "mey": ["primary", "selective"],
        "snacks-tr": ["corporate", "primary", "selective", "corprimary", "pladis_categories"],
        "mey-international": ["primary"],
        "fastfood-tr": ["corporate"],
        "transportation-tr": ["corporate"],
        "airtravel-tr": ["corporate"]
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
                daily_records = Latest7Days.objects.filter(  # LatestDataTable -> Latest7Days
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

@login_required
def latest_data(request, category, subcategory):
    # URL'den gelen parametreleri küçük harfe çevir
    category_lower = category.lower()
    subcategory_lower = subcategory.lower()

    # Veritabanından ilgili filtrelemeyi yap
    data = LatestData.objects.filter(
        source_category__iexact=category_lower,  # Büyük-küçük harf duyarsız filtreleme
        selective_part__iexact=subcategory_lower
    ).order_by('-created_time')

    # Template'e verileri gönder
    return render(request, 'latest_data.html', {
        'data': data,
        'category': category,  # Orijinal kategori adını gönder
        'subcategory': subcategory  # Orijinal alt kategori adını gönder
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


def get_channel_id(url):
    try:
        # YouTube kanal sayfasını çek
        response = requests.get(url)
        response.raise_for_status()  # Eğer bağlantı başarısızsa, hata fırlat

        # Sayfa kaynağını al
        page_content = response.text

        # <link rel="alternate" ... > etiketinden kanal ID'sini çek
        match_link = re.search(r'<link rel="alternate"[^>]*href="https://www\.youtube\.com/feeds/videos\.xml\?channel_id=([a-zA-Z0-9_-]+)"', page_content)
        if match_link:
            return match_link.group(1)

        return None  # Kanal ID'si bulunamazsa None döndür
    except requests.exceptions.RequestException as e:
        return None


def youtube_channel_id_view(request):
    channel_id = None
    error = None

    if request.method == 'POST':
        url = request.POST.get('url', '')
        if url:
            try:
                channel_id = get_channel_id(url)
                if not channel_id:
                    error = "Geçersiz YouTube kanal URL'si. Lütfen doğru formatta bir URL giriniz."
            except Exception as e:
                error = str(e)

    return render(request, 'youtube_channel.html', {'channel_id': channel_id, 'error': error})

