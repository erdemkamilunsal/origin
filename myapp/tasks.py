from celery import shared_task
from myapp.management.commands.scraper import runscraper

@shared_task
def run_scraper_task():
    runscraper()  # Scraper fonksiyonunu çağırır
