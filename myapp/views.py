# views.py
from django.shortcuts import render
from .models import ChannelData
from django.db.models import Max
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

@login_required
def index(request):
    # Tüm sosyal medya kanalları
    channels = [
        "twitter", "facebook", "facebook_page_comment", "facebook_page_like",
        "youtube", "youtube_shorts", "instagram", "instagram_comment",
        "tiktok", "pinterest", "rss", "apple_app_store_comment",
        "google_play_store_comment", "linkedin", "donanimhaber", "eksi_sozluk",
        "inci_sozluk", "sikayetvar", "uludag_sozluk"
    ]

    # Her kanaldan en güncel veriyi çek
    latest_data = {}
    for channel in channels:
        data = ChannelData.objects.filter(source=channel).order_by('-created_time').first()
        if data:
            latest_data[channel] = data
    return render(request, 'index.html', {'latest_data': latest_data})

def filtersbycomment(request):
    return render(request, 'filtersbycomment.html')

class CustomLoginView(LoginView):
    template_name = 'login.html'  # Giriş sayfası şablonu
    redirect_authenticated_user = True  # Giriş yapmış kullanıcıyı doğrudan yönlendir

def custom_logout(request):
    logout(request)  # Kullanıcıyı çıkış yapar
    return HttpResponseRedirect('/login/')  # Çıkış yapıldıktan sonra login sayfasına yönlendir

