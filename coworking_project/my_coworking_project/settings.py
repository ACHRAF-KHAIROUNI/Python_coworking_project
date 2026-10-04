"""
Django settings for my_coworking_project project.
"""
import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv
import cloudinary_storage

# ==============================================================================
# 1. CHARGEMENT DES VARIABLES D'ENVIRONNEMENT - TOUT AU DÉBUT
# ==============================================================================
load_dotenv()

# ==============================================================================
# 2. CONFIGURATION CLOUDINARY - IMMÉDIATEMENT APRÈS load_dotenv()
# ==============================================================================
import cloudinary
import cloudinary.uploader
import cloudinary.api


# Configuration du stockage Cloudinary AVANT toute autre configuration
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
    'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
    'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
}

# DÉFINIR DEFAULT_FILE_STORAGE IMMÉDIATEMENT
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# ==============================================================================
# 3. CONFIGURATION DE BASE
# ==============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-tcmmz6zvh_m(1m9)8&aq*+)98=a4+zykx5=^*)!%wf2w%_h9ir')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = ['localhost','127.0.0.1',"coworking.up.railway.app"]
CSRF_TRUSTED_ORIGINS = [
    "http://localhost",
    "https://coworking.up.railway.app"
]


from core.views import page_not_found_view
handler404 = page_not_found_view
DEBUG = False
# ==============================================================================
# 4. APPLICATIONS - ORDRE CRUCIAL
# ==============================================================================
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Cloudinary AVANT staticfiles - CRUCIAL
    'cloudinary_storage',
    'cloudinary',
    

    # Vos applications
    'users.apps.UsersConfig',
    'company.apps.CompanyConfig',
    'finances.apps.FinancesConfig',
    'reservations.apps.ReservationsConfig',
    'chatAI.apps.ChataiConfig',
    'twilio_chatbot.apps.TwilioChatbotConfig',
    'widget_tweaks',
    'core',
    'rest_framework',
    'rest_framework_simplejwt',
    'api.apps.ApiConfig',

]

# Modèle Utilisateur Personnalisé
AUTH_USER_MODEL = 'users.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'my_coworking_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'my_coworking_project.wsgi.application'

# ==============================================================================
# 5. BASE DE DONNÉES
# ==============================================================================
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# ==============================================================================
# 6. VALIDATION MOT DE PASSE, INTERNATIONALISATION
# ==============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==============================================================================
# 7. FICHIERS STATIQUES ET MÉDIA
# ==============================================================================
STATIC_URL = '/static/'
MEDIA_URL = '/media/'
STATIC_ROOT = BASE_DIR / 'staticfiles' 

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# NE PAS redéfinir DEFAULT_FILE_STORAGE ici - déjà fait en haut

# ==============================================================================
# 8. AUTRES CONFIGURATIONS
# ==============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuration Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# Redirections d'authentification
LOGIN_REDIRECT_URL = 'profile'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'

DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

REST_FRAMEWORK = {
    # Par défaut, toutes les requêtes API nécessiteront un token d'authentification valide.
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    # Par défaut, l'accès aux endpoints sera refusé si l'utilisateur n'est pas authentifié.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}