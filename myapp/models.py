from django.db import models

from django.db import models

class ChannelData(models.Model):
    author_name = models.CharField(max_length=255, null=True, blank=True)
    author_nick = models.CharField(max_length=255, null=True, blank=True)
    author_follower_count = models.IntegerField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    link = models.URLField(null=True, blank=True)
    created_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.source} - {self.author_name}"