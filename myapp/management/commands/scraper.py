import time
import requests
from bs4 import BeautifulSoup
import json
import datetime
from unidecode import unidecode
import pytz
import os
import django
from myapp.models import ChannelData
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sosyal medya verilerini çekip kaydeder"
    def handle(self, *args, **kwargs):

        cookies = {
            '_ga': 'GA1.2.980697164.1719825621',
            '_ga_K75CNCCDWX': 'GS1.2.1727762591.2.0.1727762591.0.0.0',
            '_gid': 'GA1.2.1298405708.1736751072',
            'csrftoken': '7JnvwV1I7brfnVPLpCKnX9opKvp3aCYQ',
            '_ga_W6ZMFP1HFC': 'GS1.2.1737153114.268.1.1737156318.0.0.0',
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'tr',
            'cache-control': 'no-cache',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': '_ga=GA1.2.980697164.1719825621; _ga_K75CNCCDWX=GS1.2.1727762591.2.0.1727762591.0.0.0; _gid=GA1.2.1298405708.1736751072; csrftoken=7JnvwV1I7brfnVPLpCKnX9opKvp3aCYQ; _ga_W6ZMFP1HFC=GS1.2.1737153114.268.1.1737156318.0.0.0',
            'origin': 'https://finans.ebrandvalue.com',
            'pragma': 'no-cache',
            'priority': 'u=0, i',
            'referer': 'https://finans.ebrandvalue.com/accounts/login/',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }


        login_page_url = "https://finans.ebrandvalue.com/accounts/login/?next=/"
        login_url = "https://finans.ebrandvalue.com/accounts/login/?next=/"
        optional_channels = {"web"}
        channels_to_find = {
            "twitter", "facebook", "facebook_page_comment", "facebook_page_like",
            "youtube", "youtube_shorts", "instagram", "instagram_comment",
            "tiktok", "pinterest", "rss", "apple_app_store_comment",
            "google_play_store_comment", "linkedin", "donanimhaber", "eksi_sozluk",
            "inci_sozluk", "sikayetvar", "uludag_sozluk"
            }
        istanbul_tz = pytz.timezone('Europe/Istanbul')
        start_time = datetime.datetime.now()

        with requests.Session() as session:
            login_page = session.get(login_page_url, headers=headers)
            soup = BeautifulSoup(login_page.text, "html.parser")
            csrf_token = soup.find(type="hidden")["value"]
            payload = {
                "username": "erdem.unsal",
                "password": "eu123",
                "csrfmiddlewaretoken": csrf_token
            }
            response = session.post(login_url, data=payload, headers=headers)
            if response.status_code == 200:
                print("Başarıyla giriş yapıldı!")
            else:
                print("Giriş başarısız!")
                exit()
            protected_url = "https://finans.ebrandvalue.com/industries/selective/social/posts/?path_param=posts"
            found_channels = set()
            result = {}
            for channel in channels_to_find:
                if channel not in optional_channels:
                    current_url = f"{protected_url}&source={channel}&start=0"
                    print(f"Veri çekiliyor: {current_url}")
                    protected_response = session.get(current_url)
                    if protected_response.status_code != 200:
                        continue
                    parsed_data = json.loads(protected_response.text)
                    all_data = parsed_data.get('data', [])
                    if all_data:
                        entry = all_data[0]
                        body = entry['content'].get('body', None)
                        body = unidecode(body) if body else None
                        result[channel] = {
                            "author_name": entry['author'].get('name', None),
                            "author_nick": entry['author'].get('nick', None),
                            "author_follower_count": entry['author'].get('follower_count', None),
                            "body": entry['content'].get('body', None),
                            "source": entry.get('source', None),
                            "link": entry['content'].get('link', None),
                            "create_time": entry['content'].get('create_time', None),
                            }
                        found_channels.add(channel)
                    else:
                        print(f"{channel} kanalı için veri bulunamadı.")
                else:
                    result[channel] = {
                        "author_name": None,
                        "author_nick": None,
                        "author_follower_count": None,
                        "body": None,
                        "source": None,
                        "link": None,
                        "created_time": None,
                    }
            for channel, data in result.items():
                ChannelData.objects.create(
                    author_name=data.get("author_name"),
                    author_nick=data.get("author_nick"),
                    author_follower_count=data.get("author_follower_count"),
                    body=data.get("body"),
                    source=data.get("source"),
                    link=data.get("link"),
                    created_time=data.get("create_time"))
            self.stdout.write(self.style.SUCCESS("Veriler başarıyla kaydedildi!"))
