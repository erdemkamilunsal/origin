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
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Last update: {self.last_update}"

class LatestDataTable(models.Model):
    source_category = models.CharField(max_length=255)
    selective_part = models.CharField(max_length=255)
    source = models.CharField(max_length=255)
    created_time = models.DateField()
    author = models.CharField(max_length=255, default='Unknown')
    total = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.created_time} - {self.source_category} - {self.selective_part} - {self.source}"

    class Meta:
        verbose_name = "Son 7 Günlük Veri"
        verbose_name_plural = "Son 7 Günlük Veriler"

