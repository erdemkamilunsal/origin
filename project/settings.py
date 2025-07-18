import os
from pathlib import Path
from dotenv import load_dotenv



# Proje ana dizini
BASE_DIR = Path(__file__).resolve().parent.parent

# .env dosyasını yükle
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Güvenlik ve genel ayarlar
SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']



# Uygulamalar
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'myapp',  # Kendi uygulamanın adı
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_REDIRECT_URL = '/'

ROOT_URLCONF = 'project.urls'  # Proje ismine göre güncelle

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'myapp.views.base_context',
                'myapp.context_processors.last_scrape_time',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'  # Proje ismine göre güncelle

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Bu kesin olmalı
        'NAME': os.getenv('DB_NAME'),               # DB adı .env'den okunuyor
        'USER': os.getenv('DB_USER'),               # Kullanıcı adı .env'den
        'PASSWORD': os.getenv('DB_PASSWORD'),       # Şifre .env'den
        'HOST': os.getenv('DB_HOST'),               # Host .env'den
        'PORT': os.getenv('DB_PORT'),               # Port .env'den
    }
}



# Şifre doğrulama
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

# Uluslararasılaşma
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Istanbul'

USE_I18N = True

USE_TZ = True

# Statik dosyalar
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # BU SATIRI EKLE

# Varsayılan otomatik alan
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
