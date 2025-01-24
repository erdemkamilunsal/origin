from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django'nun ayarlarını Celery'ye bildirin
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

# Celery uygulamasını oluşturun
app = Celery('project')

# Django'nun settings.py dosyasındaki CELERY_ ile başlayan tüm ayarları yükler
app.config_from_object('django.conf:settings', namespace='CELERY')

# Proje içerisindeki tüm uygulamalardaki task'leri otomatik olarak bulur
app.autodiscover_tasks()


