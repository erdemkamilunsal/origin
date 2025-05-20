from myapp.models import ScraperLog
from django.utils.timezone import localtime
from django.core.cache import cache


def last_scrape_time(request):
    try:
        log = ScraperLog.objects.get(id=1)
        # UTC -> Yerel zaman (Istanbul)
        local_time = localtime(log.last_update)
        return {"last_scrape_time": local_time.strftime("%Y-%m-%d %H:%M:%S")}
    except ScraperLog.DoesNotExist:
        return {"last_scrape_time": "Henüz çalışmadı"}


def big_screen_status_context(request):
    return {
        "snacks_status": cache.get("big_screen_status_snacks-tr"),
        "finans_status": cache.get("big_screen_status_finans"),
        "mey_status": cache.get("big_screen_status_mey"),
    }