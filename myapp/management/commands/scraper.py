import time
import requests
from bs4 import BeautifulSoup
import json
import datetime
from unidecode import unidecode
import pytz
import django
from myapp.models import ChannelData
from django.core.management.base import BaseCommand
from datetime import datetime
from myapp.models import ScraperLog

def update_scraper_log():
    log_entry = ScraperLog.objects.first()  # Eğer kayıt varsa güncelle, yoksa yeni bir kayıt oluştur
    if log_entry:
        log_entry.save()  # `auto_now=True` olduğu için kaydederken otomatik güncellenir
    else:
        ScraperLog.objects.create()  # İlk defa çalışıyorsa yeni bir kayıt oluştur



class Command(BaseCommand):
    help = "Sosyal medya verilerini çekip kaydeder"



    def handle(self, *args, **kwargs):

        base_urls = {
            "finans": ["corporate","selective","primary"],
            "mey": ["primary", "selective"],
            "snacks-tr": ["corporate", "primary", "selective" ,"corprimary", "pladis_categories"],
            "mey-international": ["primary"]
        }

        channels_to_find = {
            "twitter",
            "facebook", "facebook_page_comment", "facebook_page_like",
            "youtube", "youtube_shorts", "instagram", "instagram_comment",
            "tiktok", "pinterest", "rss", "apple_app_store_comment",
            "google_play_store_comment", "linkedin", "donanimhaber", "eksi_sozluk",
            "inci_sozluk", "sikayetvar", "uludag_sozluk"
        }

        istanbul_tz = pytz.timezone('Europe/Istanbul')

        for base_url, selective_parts in base_urls.items():
            login_page_url = f"https://{base_url}.ebrandvalue.com/accounts/login/?next=/"
            login_url = f"https://{base_url}.ebrandvalue.com/accounts/login/?next=/"

            print(f"{base_url} için giriş yapılıyor...")

            with requests.Session() as session:
                login_page = session.get(login_page_url)
                if login_page.status_code != 200:
                    print(f"{base_url} için giriş sayfasına ulaşılamadı.")
                    continue

                soup = BeautifulSoup(login_page.text, "html.parser")
                csrf_token_input = soup.find("input", {"name": "csrfmiddlewaretoken"})
                if csrf_token_input:
                    csrf_token = csrf_token_input["value"]
                else:
                    print(f"{base_url} için CSRF token bulunamadı.")
                    continue

                payload = {
                    "username": "erdem.unsal",
                    "password": "eu123",
                    "csrfmiddlewaretoken": csrf_token
                }
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                    "Referer": login_page_url
                }
                response = session.post(login_url, data=payload, headers=headers)

                if response.status_code == 200 and "dashboard" in response.text:
                    print(f"{base_url} için giriş başarılı!")
                else:
                    print(f"{base_url} için giriş başarısız!")
                    continue

                print(f"{base_url} için veri çekiliyor...")

                for selective in selective_parts:
                    result = {}

                    for channel in channels_to_find:
                        current_url = f"https://{base_url}.ebrandvalue.com/industries/{selective}/social/posts/?path_param=posts&source={channel}&start=0"
                        print(f"{current_url} verisi çekiliyor...")

                        protected_response = session.get(current_url)
                        if protected_response.status_code != 200:
                            print(f"{selective} kategorisinde veri bulunamadı veya geçersiz.")
                            continue

                        parsed_data = json.loads(protected_response.text)
                        all_data = parsed_data.get('data', [])

                        if all_data:
                            for entry in all_data:
                                body = entry['content'].get('body', None)
                                body = unidecode(body) if body else None

                                result[channel] = {
                                    "source_category": base_url,
                                    "author_name": entry['author'].get('name', None),
                                    "author_nick": entry['author'].get('nick', None),
                                    "author_follower_count": entry['author'].get('follower_count', None),
                                    "body": body,
                                    "source": entry.get('source', None),
                                    "link": entry['content'].get('link', None),
                                    "created_time": entry['content'].get('create_time', None),
                                    "selective_part": selective
                                }
                        else:
                            print(f"{channel} kanalı için {base_url} - {selective} kategorisinde veri bulunamadı.")

                    for channel, data in result.items():
                        if data:  # Yeni veri varsa işlem yap
                            # Önce eski kayıtları sil
                            ChannelData.objects.filter(
                                source_category=data.get("source_category"),
                                selective_part=data.get("selective_part"),
                                source=data.get("source")
                            ).delete()

                            # Yeni veriyi kaydet
                            ChannelData.objects.create(
                                source_category=data.get("source_category"),
                                author_name=data.get("author_name"),
                                author_nick=data.get("author_nick"),
                                author_follower_count=data.get("author_follower_count"),
                                body=data.get("body"),
                                source=data.get("source"),
                                link=data.get("link"),
                                created_time=data.get("created_time"),
                                selective_part=data.get("selective_part"),
                            )
                            print(
                                f"{data.get('selective_part')} - {data.get('created_time')} güncellendi ve kaydedildi.")
                        else:
                            print(f"{channel} için yeni veri bulunamadı, eski kayıtlar silinmedi.")

        self.stdout.write(self.style.SUCCESS("Tüm veriler başarıyla kaydedildi!"))

update_scraper_log()