import os
from dotenv import load_dotenv

# .env dosyasını yükle (manage.py ile aynı klasörde)
load_dotenv()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = get_wsgi_application()
