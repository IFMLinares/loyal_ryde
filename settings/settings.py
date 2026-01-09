"""
Django settings for settings project.
Optimized for Dokploy Deployment.
"""

import os
from pathlib import Path
import datetime
import settings.db as db
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURACIÓN CRÍTICA PARA DOKPLOY / TRAEFIK ---
# Esto arregla el error "Bad Request (400)" y los problemas de CSRF/SSL
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Permitir todos los hosts (Dokploy maneja la seguridad antes de llegar aquí)
ALLOWED_HOSTS = ["*"]

# Confiar en los dominios de Dokploy para formularios (Login/Admin)
CSRF_TRUSTED_ORIGINS = [
    "https://*.traefik.me", 
    "http://*.traefik.me", 
    "https://*.dokploy.com",
    "http://localhost",
    "http://127.0.0.1"
]
# Desactivamos redirección forzada SSL interna (lo hace Traefik)
SECURE_SSL_REDIRECT = False
# -----------------------------------------------------

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-fallback-key')

# SECURITY WARNING: don't run with debug turned on in production!
# En Dokploy Environment pon DEBUG=False
DEBUG = 'True'


# Application definition
INSTALLED_APPS = [
    'daphne', # Debe ir de primero para Channels
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.gis',
    'leaflet',
    
    # django all auth app
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # Apps 
    'apps.loyalRyde',
    'apps.api_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # 'whitenoise.middleware.WhiteNoiseMiddleware', # Descomentar si instalas whitenoise para servir estáticos
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = 'settings.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

WSGI_APPLICATION = 'settings.wsgi.application'

# Database Configuration
# Dokploy inyecta estas variables automáticamente si usas Database Service
DB_ENGINE = os.environ.get('DB_ENGINE', 'sqlite3').lower()
if DB_ENGINE == 'postgresql':
    DATABASES = db.POSTGRESQL
else:
    DATABASES = db.SQLITE


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


# Internationalization
LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'America/Kralendijk'
USE_I18N = True
USE_L10N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


# User & Auth
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = '/'
AXES_LOGIN_FAILURE_LIMIT = 30
SITE_ID = 1
AUTH_USER_MODEL = 'loyalRyde.CustomUser'
SITE_DOMAIN = os.environ.get('SITE_DOMAIN', 'http://localhost:8000')


# Email Config
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('email') or os.environ.get('DJANGO_EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('passEmail') or os.environ.get('DJANGO_EMAIL_HOST_PASSWORD')


# Rest Framework & JWT
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=36500),
    'JWT_ALLOW_REFRESH': True,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': datetime.timedelta(days=36500),
    'REFRESH_TOKEN_LIFETIME': datetime.timedelta(days=36500),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Google Maps
GOOGLE_MAPS_API_KEY = os.environ.get('DJANGO_GOOGLE_MAPS_API_KEY')

# CORS
CORS_ALLOW_ALL_ORIGINS = True # Útil para desarrollo, ajustar para producción real luego


# --- DAPHNE & CHANNELS (WEBSOCKETS) ---
ASGI_APPLICATION = 'settings.asgi.application'

# NOTA IMPORTANTE PARA DOCKER/DOKPLOY:
# Si usas un servicio de Redis en Dokploy, el host NO es '127.0.0.1'.
# Debe ser el nombre del contenedor de redis o 'redis' si están en la misma red.
# Por defecto lo dejo en localhost, pero si falla, cámbialo en tus variables de entorno.
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(os.environ.get('REDIS_HOST', '127.0.0.1'), 6379)],
        }
    }
}


# Leaflet Config
LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (10.4806, -66.9036),
    'DEFAULT_ZOOM': 7,
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 18,
    'TILES': [('OpenStreetMap', 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        'attribution': '&copy; OpenStreetMap contributors'
    })],
}