import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-_(d$u1ksijlg5*p6t)*)&49pr^0-us0u6wsfv94=(y8%mee=au'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

INSTALLED_APPS += [
    # Installed apps
    'django_cleanup.apps.CleanupConfig',
    'ckeditor',
    'ckeditor_uploader',

    # Created apps
    'core',
    'user',
    'blog',
    'support',
    'service',
    'recovery',
    'events',
    'rehab',
    'women',
    'babycare',
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

ROOT_URLCONF = 'Novita.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'Novita.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms Configuration
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Email Configuration (hardcoded, credentials from .env)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
DEFAULT_FROM_EMAIL = 'novita.org.bd@gmail.com'
SERVER_EMAIL = 'novita.org.bd@gmail.com'

SUPPORT_NOTIFY_EMAIL = ''
SERVICE_NOTIFY_EMAIL = ''

# Custom User Model
AUTH_USER_MODEL = 'user.CustomUser'

# Login/Logout URLs
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# Static and Media Files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# CKEditor Configuration
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_JQUERY_URL = 'https://ajax.googleapis.com/ajax/libs/jquery/2.2.4/jquery.min.js'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
        'extraPlugins': ','.join([
            'uploadimage',  # the upload image feature
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    },
    'blog_post': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source'],
            ['Image', 'uploadimage'],
            ['Styles', 'Format', 'Font', 'FontSize'],
            ['TextColor', 'BGColor'],
        ],
        'height': 400,
        'width': '100%',
        'filebrowserWindowHeight': 725,
        'filebrowserWindowWidth': 940,
        'toolbarCanCollapse': True,
        'mathJaxLib': '//cdn.mathjax.org/mathjax/2.2-latest/MathJax.js?config=TeX-AMS_HTML',
        'tabSpaces': 4,
        'extraPlugins': ','.join([
            'uploadimage',
            'div',
            'autolink',
            'autoembed',
            'embedsemantic',
            'autogrow',
            'widget',
            'lineutils',
            'clipboard',
            'dialog',
            'dialogui',
            'elementspath'
        ]),
    }
}

JAZZMIN_SETTINGS = {
    "site_title": "Novita Admin",
    "site_header": "Novita Admin",
    "site_brand": "Novita",
    "welcome_sign": "Welcome to Novita Admin Panel",
    "copyright": "Novita",
    "search_model": "auth.User",
    "icons": {
        # Authentication
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",

        # User app
        "user.CustomUser": "fas fa-user-circle",

        # Blog
        "blog.BlogPost": "fas fa-newspaper",
        "blog.Category": "fas fa-tags",
        "blog.Comment": "fas fa-comments",
        "blog.PostLike": "fas fa-thumbs-up",

        # Core
        "core.Banner": "fas fa-image",
        "core.ContactMessage": "fas fa-envelope",
        "core.Donation": "fas fa-heart",
        "core.ExpertApplication": "fas fa-file-alt",

        # Events
        "events.Event": "fas fa-calendar-alt",

        # Recovery
        "recovery.Appointment": "fas fa-calendar-check",
        "recovery.CounselingSession": "fas fa-user-friends",
        "recovery.DailyCheckIn": "fas fa-clipboard-check",
        "recovery.Milestone": "fas fa-flag",
        "recovery.PatientProfile": "fas fa-user-injured",
        "recovery.RecoveryPlan": "fas fa-clipboard-list",
        "recovery.RelapseRecord": "fas fa-exclamation-triangle",

        # Service
        "service.ExpertProfile": "fas fa-user-tie",
        "service.ServiceType": "fas fa-concierge-bell",
        "service.ServiceInquiry": "fas fa-question-circle",
        "service.ServiceMessage": "fas fa-comments",
        "service.ServiceMessageAttachment": "fas fa-paperclip",

        # Support
        "support.SupportTicket": "fas fa-ticket-alt",
        "support.TicketAttachment": "fas fa-paperclip",
        "support.TicketResponse": "fas fa-reply",

        # Women & Courses
        "women.Course": "fas fa-book",
        "women.CourseModule": "fas fa-layer-group",
        "women.ModuleLesson": "fas fa-book-open",
        "women.Enrollment": "fas fa-graduation-cap",
        "women.LessonProgress": "fas fa-tasks",

        # Baby Care
        "babycare.BabyCareRequest": "fas fa-child",
        "babycare.BabyCareUpdate": "fas fa-info-circle",

        # Rehab
        "rehab.AdmissionRequest": "fas fa-file-signature",
        "rehab.AdmissionUpdate": "fas fa-clipboard-check",
    },

    # Allow searching across commonly used models in the admin search
    "search_model": [
        "user.CustomUser",
        "recovery.PatientProfile",
        "support.SupportTicket",
    ],

    "topmenu_links": [
        {"name": "Home", "url": "admin:index"},
        {"name": "View Site", "url": "home", "new_window": True},
    ],
    
    "show_sidebar": True,
    "navigation_expanded": True,
    "changeform_format": "horizontal_tabs",
}

# Stripe API Keys (from .env file)
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY', '')

