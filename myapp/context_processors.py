from myapp.models import ScraperLog
from django.utils.timezone import localtime


def last_scrape_time(request):
    try:
        log = ScraperLog.objects.get(id=1)
        # UTC -> Yerel zaman (Istanbul)
        local_time = localtime(log.last_update)
        return {"last_scrape_time": local_time.strftime("%Y-%m-%d %H:%M:%S")}
    except ScraperLog.DoesNotExist:
        return {"last_scrape_time": "Henüz çalışmadı"}
