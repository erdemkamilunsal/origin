from django.db import models


class ChannelData(models.Model):
    source_category = models.CharField(max_length=255, null=True, blank=True)
    author_name = models.CharField(max_length=255, null=True, blank=True)
    author_nick = models.CharField(max_length=255, null=True, blank=True)
    author_follower_count = models.IntegerField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    created_time = models.DateTimeField(null=True, blank=True)
    selective_part = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Data for {self.source_category} - {self.selective_part}"

class ScraperLog(models.Model):
    last_update = models.DateTimeField(auto_now=True)  # Otomatik olarak güncellenir

    def __str__(self):
        return f"Last update: {self.last_update}"