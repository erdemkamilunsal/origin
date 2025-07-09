import time
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import pytz
import os
import django
from unidecode import unidecode
from django.core.management.base import BaseCommand
from myapp.models import MostSharedContent, ScraperLog, LatestData, Latest7Days
def update_scraper_log():
    log_entry, _ = ScraperLog.objects.get_or_create(id=1)
    log_entry.save()
def fetch_data(session, url):
    try:
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            return json.loads(response.text)
    except Exception as e:
        print(f"{url} için hata oluştu: {e}")
    return None
def fetch_last_7_days(session, base_url, selective, channels_to_find, today):
    seven_days_ago = today - timedelta(days=7)
    deleted_count, _ = Latest7Days.objects.filter(
        created_time__lte=seven_days_ago.date()
    ).delete()
    print(f"🗑 {deleted_count} adet eski kayıt (7 günden eski) temizlendi.")

    for i in range(7):
        date_start_dt = today - timedelta(days=i)
        record_date = date_start_dt.date()
        date_end_dt = date_start_dt + timedelta(days=1)
        since_str = date_start_dt.strftime("%d.%m.%Y 00:00").replace(" ", "%20")
        until_str = date_end_dt.strftime("%d.%m.%Y 00:00").replace(" ", "%20")

        for channel in channels_to_find:
            extra_url = (
                f"https://{base_url}.ebrandvalue.com/industries/{selective}/social/posts/"
                f"?path_param=posts&source={channel}&since={since_str}&until={until_str}&limit=1"
            )
            print(f"{extra_url} verisi çekiliyor...")

            response = session.get(extra_url)
            if response.status_code != 200:
                print(f"{since_str} - {base_url} için {channel} verisi bulunamadı veya geçersiz.")
                continue

            parsed_data = json.loads(response.text)
            paging_data = parsed_data.get('paging', {})
            author_count = paging_data.get("authors", 0)
            content_count = paging_data.get("total", 0)

            Latest7Days.objects.filter(
                source_category=base_url,
                selective_part=selective,
                source=channel,
                created_time=record_date
            ).delete()

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
    for channel in channels_to_find:
        current_url = f"https://{base_url}.ebrandvalue.com/industries/{selective}/social/posts/?path_param=posts&source={channel}&start=0&limit=1"
        print(f"{current_url} verisi çekiliyor...")

        response = session.get(current_url)
        if response.status_code != 200:
            print(f"{selective} kategorisinde {channel} kanalı için veri bulunamadı veya geçersiz.")
            continue

        parsed_data = json.loads(response.text)
        all_data = parsed_data.get('data', [])

        if all_data:
            entry = all_data[0]
            body = entry['content'].get('body', None)
            body = unidecode(body) if body else None
            LatestData.objects.filter(
                source_category=base_url,
                selective_part=selective,
                source=channel
            ).delete()

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
    istanbul_tz = pytz.timezone('Europe/Istanbul')
    today = datetime.now(istanbul_tz)
    start_date = today - timedelta(days=1)
    start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
    since_str = start_date.strftime("%d.%m.%Y 00:00").replace(" ", "%20")
    until_str = end_date.strftime("%d.%m.%Y 00:00").replace(" ", "%20")

    for channel in kanallar:
        current_url = f"https://{base_url}.ebrandvalue.com/industries/{selective}/social/posts/?path_param=posts&source={channel}&most_shared=true&since={since_str}&until={until_str}&limit=10"
        print(f"{current_url} verisi çekiliyor...")

        response = session.get(current_url)
        if response.status_code != 200:
            print(f"{selective} kategorisinde {channel} için veri bulunamadı veya geçersiz.")
            continue

        parsed_data = json.loads(response.text)
        all_data = parsed_data.get('data', [])
        all_data = all_data[:10]
        MostSharedContent.objects.filter(
            source_category=base_url,
            selective_part=selective,
            source=channel,
        ).delete()

        for entry in all_data:
            body = entry['content'].get('body', None)
            body = unidecode(body) if body else None
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
                "created_time": start_date.date(),
                "source_category": base_url
            }

            MostSharedContent.objects.create(**post_data)
            print(f"✅ {selective} - {channel} için yeni veri eklendi: {post_data['name']} - {post_data['create_time']}")

class Command(BaseCommand):
    help = "Sosyal medya verilerini çekip kaydeder."

    def handle(self, *args, **kwargs):
        start_time = time.time()
        base_urls = {
            "finans": ["corporate","selective", "primary"]
            #"mey": ["primary", "selective"]
            #"snacks-tr": ["corporate", "primary", "selective", "corprimary", "pladis_categories"],
            #"mey-international": ["primary"],
            #"fastfood-tr": ["corporate"],
            #"transportation-tr": ["corporate"],
            #"airtravel-tr": ["corporate"]
        }
        channels_to_find = {
            "twitter", "facebook", "facebook_page_comment", "facebook_page_like",
            "youtube", "youtube_shorts", "instagram", "instagram_comment",
            "tiktok", "pinterest", "rss", "apple_app_store_comment",
            "google_play_store_comment", "linkedin", "donanimhaber", "eksi_sozluk",
            "inci_sozluk", "sikayetvar", "uludag_sozluk"
        }
        kanallar = {"twitter", "facebook", "youtube", "instagram"}
        istanbul_tz = pytz.timezone('Europe/Istanbul')
        today = datetime.now(istanbul_tz)

        with requests.Session() as session:
            for base_url, selective_parts in base_urls.items():
                login_page_url = f"https://{base_url}.ebrandvalue.com/accounts/login/?next=/"
                login_page = session.get(login_page_url)
                if login_page.status_code != 200:
                    print(f"{base_url} için giriş sayfasına ulaşılamadı.")
                    continue
                soup = BeautifulSoup(login_page.text, "html.parser")
                csrf_token = soup.find("input", {"name": "csrfmiddlewaretoken"})["value"]
                payload = {"username": "erdem.unsal", "password": "eu123", "csrfmiddlewaretoken": csrf_token}
                headers = {"User-Agent": "Mozilla/5.0", "Referer": login_page_url}
                response = session.post(login_page_url, data=payload, headers=headers)

                if response.status_code != 200 or "dashboard" not in response.text:
                    print(f"{base_url} için giriş başarısız!")
                    continue

                for selective in selective_parts:
                    fetch_yesterday_data(session, base_url, selective, channels_to_find, today)
                    #fetch_last_7_days(session, base_url, selective, channels_to_find, today)
                    #fetch_most_shared(session, base_url, selective, kanallar)


        end_time = time.time()
        print(f"Scraper tamamlandı! Toplam süre: {end_time - start_time:.2f} saniye.")
        update_scraper_log()
