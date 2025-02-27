import time
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import pytz
from concurrent.futures import ThreadPoolExecutor, as_completed
from unidecode import unidecode
from django.core.management.base import BaseCommand
from myapp.models import MostSharedContent, ScraperLog, LatestData, Latest7Days

def update_scraper_log():
    """Scraper log'unu günceller. Eğer log kaydı varsa günceller, yoksa yeni bir kayıt oluşturur."""
    log_entry = ScraperLog.objects.first()
    if log_entry:
        log_entry.save()  # `auto_now=True` olduğu için otomatik olarak güncellenir
    else:
        ScraperLog.objects.create()  # İlk defa çalışıyorsa yeni bir kayıt oluştur

def fetch_data(session, url):
    """URL'den veri çeker ve JSON formatında döner."""
    try:
        response = session.get(url, timeout=10)  # 10 saniyelik zaman aşımı ile istek atar
        if response.status_code == 200:  # Başarılı bir yanıt alındıysa
            return json.loads(response.text)  # JSON verisini Python dict'ine dönüştürür
    except Exception as e:
        print(f"{url} için hata oluştu: {e}")  # Hata durumunda log yazdırır
    return None  # Hata durumunda None döner

def fetch_last_7_days(session, base_url, selective, channels_to_find, today):
    """Son 7 günlük verileri çeker ve veritabanına kaydeder."""
    seven_days_ago = today - timedelta(days=7)  # 7 gün öncesini hesapla
    deleted_count, _ = Latest7Days.objects.filter(
        created_time__lte=seven_days_ago.date()  # 7 günden eski verileri sil
    ).delete()
    print(f"🗑 {deleted_count} adet eski kayıt (7 günden eski) temizlendi.")

    for i in range(7):  # Son 7 gün için döngü
        date_start_dt = today - timedelta(days=i)  # İlgili günün başlangıç tarihi
        record_date = date_start_dt.date()  # Sadece tarih kısmını al
        date_end_dt = date_start_dt + timedelta(days=1)  # Bir sonraki günün başlangıcı
        since_str = date_start_dt.strftime("%d.%m.%Y 00:00").replace(" ", "%20")  # URL için tarih formatı
        until_str = date_end_dt.strftime("%d.%m.%Y 00:00").replace(" ", "%20")  # URL için tarih formatı

        for channel in channels_to_find:  # Her kanal için veri çek
            extra_url = (
                f"https://{base_url}.ebrandvalue.com/industries/{selective}/social/posts/"
                f"?path_param=posts&source={channel}&since={since_str}&until={until_str}"
            )
            print(f"{extra_url} verisi çekiliyor...")

            response = session.get(extra_url)
            if response.status_code != 200:  # İstek başarısızsa
                print(f"{since_str} - {base_url} için {channel} verisi bulunamadı veya geçersiz.")
                continue

            parsed_data = json.loads(response.text)  # JSON verisini parse et
            paging_data = parsed_data.get('paging', {})  # Paging verisini al
            author_count = paging_data.get("authors", 0)  # Yazar sayısı
            content_count = paging_data.get("total", 0)  # İçerik sayısı

            # Eski verileri sil
            Latest7Days.objects.filter(
                source_category=base_url,
                selective_part=selective,
                source=channel,
                created_time=record_date
            ).delete()

            # Yeni veriyi ekle
            Latest7Days.objects.create(
                source_category=base_url,
                selective_part=selective,
                source=channel,
                created_time=record_date,
                author=author_count,
                total=content_count
            )
            print(f"✅ {base_url} - {selective} - {channel} için yeni veri eklendi.")

def fetch_yesterday_data(session, base_url, selective, channels_to_find, today):
    """Her kanal için en son veriyi çeker ve veritabanına kaydeder."""
    for channel in channels_to_find:  # Her kanal için veri çek
        current_url = f"https://{base_url}.ebrandvalue.com/industries/{selective}/social/posts/?path_param=posts&source={channel}&start=0"
        print(f"{current_url} verisi çekiliyor...")

        response = session.get(current_url)
        if response.status_code != 200:  # İstek başarısızsa
            print(f"{selective} kategorisinde {channel} kanalı için veri bulunamadı veya geçersiz.")
            continue

        parsed_data = json.loads(response.text)  # JSON verisini parse et
        all_data = parsed_data.get('data', [])  # Tüm verileri al

        if all_data:
            entry = all_data[0]  # İlk içeriği al
            body = entry['content'].get('body', None)
            body = unidecode(body) if body else None  # Unicode karakterleri normalize et

            # Bu kanal ve kategori için eski verileri sil
            LatestData.objects.filter(
                source_category=base_url,
                selective_part=selective,
                source=channel
            ).delete()

            # Yeni veriyi ekle
            LatestData.objects.create(
                source_category=base_url,
                author_name=entry['author'].get('name', None),
                author_nick=entry['author'].get('nick', None),
                author_follower_count=entry['author'].get('follower_count', None),
                body=body,
                source=entry.get('source', None),
                link=entry['content'].get('link', None),
                created_time=entry['content'].get('create_time', None),
                selective_part=selective
            )
            print(f"✅ {selective} - {channel} için yeni veri eklendi.")
        else:
            print(f"{channel} kanalı için {base_url} - {selective} kategorisinde veri bulunamadı.")

def fetch_most_shared(session, base_url, selective, kanallar):
    """Bir önceki günün en çok paylaşılan 10 içeriğini çeker ve veritabanına kaydeder."""
    # İstanbul saat dilimi
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    today = datetime.now(istanbul_tz)

    # Bir önceki günün başlangıç tarihi (00:00)
    start_date = today - timedelta(days=1)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)

    # Bugünün başlangıç tarihi (00:00)
    end_date = today.replace(hour=0, minute=0, second=0, microsecond=0)

    # Tarihleri string formatına dönüştürme
    since_str = start_date.strftime("%d.%m.%Y 00:00").replace(" ", "%20")
    until_str = end_date.strftime("%d.%m.%Y 00:00").replace(" ", "%20")

    for channel in kanallar:  # Her kanal için veri çek
        # URL oluşturma
        current_url = f"https://{base_url}.ebrandvalue.com/industries/{selective}/social/posts/?path_param=posts&source={channel}&most_shared=true&since={since_str}&until={until_str}"
        print(f"{current_url} verisi çekiliyor...")

        response = session.get(current_url)
        if response.status_code != 200:  # İstek başarısızsa
            print(f"{selective} kategorisinde {channel} için veri bulunamadı veya geçersiz.")
            continue

        parsed_data = json.loads(response.text)  # JSON verisini parse et
        all_data = parsed_data.get('data', [])  # Tüm verileri al

        # İlk 10 elemanı al
        all_data = all_data[:10]

        # Bu kanal ve kategori için eski verileri sil
        MostSharedContent.objects.filter(
            source_category=base_url,
            selective_part=selective,
            source=channel,
            created_time=start_date.date()  # Bir önceki günün tarihi
        ).delete()

        # Yeni verileri ekle
        for entry in all_data:
            body = entry['content'].get('body', None)
            body = unidecode(body) if body else None  # Unicode karakterleri normalize et

            # Veriyi oluştur
            post_data = {
                "avatar": entry['author'].get('avatar', None),
                "follower_count": entry['author'].get('follower_count', None),
                "following_count": entry['author'].get('following_count', None),
                "name": entry['author'].get('name', None),
                "nick": entry['author'].get('nick', None),
                "brands": entry.get('brands', None),
                "content": body,
                "comment_count": entry['content'].get('comment_count', None),
                "favourite_count": entry['content'].get('favourite_count', None),
                "create_time": entry['content'].get('create_time', None),
                "link": entry['content'].get('link', None),
                "quote_count": entry['content'].get('quote_count', None),
                "reply_content": entry['content'].get('reply_content', None),
                "retweet_count": entry['content'].get('retweet_count', None),
                "view_count": entry['content'].get('view_count', None),
                "source": entry.get('source', None),
                "selective_part": selective,
                "created_time": start_date.date(),  # Bir önceki günün tarihi
                "source_category": base_url
            }

            # Yeni veriyi ekle
            MostSharedContent.objects.create(**post_data)
            print(f"✅ {selective} - {channel} için yeni veri eklendi: {post_data['name']} - {post_data['create_time']}")

class Command(BaseCommand):
    help = "Sosyal medya verilerini çekip kaydeder."

    def handle(self, *args, **kwargs):
        start_time = time.time()  # Başlangıç zamanı
        base_urls = {
            "finans": ["corporate","selective", "primary"],
            "mey": ["primary", "selective"],
            "snacks-tr": ["corporate", "primary", "selective", "corprimary", "pladis_categories"],
            "mey-international": ["primary"]
        }
        channels_to_find = {
            "twitter", "facebook", "facebook_page_comment", "facebook_page_like",
            "youtube", "youtube_shorts", "instagram", "instagram_comment",
            "tiktok", "pinterest", "rss", "apple_app_store_comment",
            "google_play_store_comment", "linkedin", "donanimhaber", "eksi_sozluk",
            "inci_sozluk", "sikayetvar", "uludag_sozluk"
        }
        kanallar = {"twitter", "facebook", "youtube", "instagram"}  # Sosyal medya kanalları
        istanbul_tz = pytz.timezone('Europe/Istanbul')  # İstanbul zaman dilimi
        today = datetime.now(istanbul_tz)  # Bugünün tarihi

        with requests.Session() as session:  # Oturum başlat
            for base_url, selective_parts in base_urls.items():  # Her bir URL ve kategori için
                # Giriş işlemleri
                login_page_url = f"https://{base_url}.ebrandvalue.com/accounts/login/?next=/"
                login_page = session.get(login_page_url)
                if login_page.status_code != 200:  # Giriş sayfasına ulaşılamazsa
                    print(f"{base_url} için giriş sayfasına ulaşılamadı.")
                    continue

                soup = BeautifulSoup(login_page.text, "html.parser")  # HTML'i parse et
                csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]  # CSRF token'ı al
                payload = {"username": "erdem.unsal", "password": "eu123", "csrfmiddlewaretoken": csrf_token}  # Giriş bilgileri
                headers = {"User-Agent": "Mozilla/5.0", "Referer": login_page_url}  # İstek başlıkları
                response = session.post(login_page_url, data=payload, headers=headers)  # Giriş isteği

                if response.status_code != 200 or "dashboard" not in response.text:  # Giriş başarısızsa
                    print(f"{base_url} için giriş başarısız!")
                    continue

                # Veri çekme işlemleri
                for selective in selective_parts:
                    #fetch_yesterday_data(session, base_url, selective, channels_to_find, today)  # Dünün verilerini çek
                    fetch_last_7_days(session, base_url, selective, channels_to_find, today)  # Son 7 günlük verileri çek
                    #fetch_most_shared(session, base_url, selective, kanallar)  # En popüler içerikleri çek

        end_time = time.time()  # Bitiş zamanı
        print(f"Scraper tamamlandı! Toplam süre: {end_time - start_time:.2f} saniye.")  # Toplam süreyi yazdır