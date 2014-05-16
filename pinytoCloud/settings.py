# coding=utf-8
"""
This File is part of Pinyto
"""

from Crypto.PublicKey import RSA

# Django settings for pinytoCloud project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('admin', 'jonny@pinyto.de'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'management.sqlite',             # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',                              # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',                              # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Berlin'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'de-DE'

SITE_ID = 2

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'w_stpdw@im!72s2^%ad5wz5&9mfd8n#95mc3)bqj3qd%f*)ile'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    #'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'pinytoCloud.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'pinytoCloud.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    #'django.contrib.auth',
    'django.contrib.contenttypes',
    #'django.contrib.sessions',
    'django.contrib.sites',
    #'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'pinytoCloud',
    'database',
    'api_prototype',
    'service',
    'librarian'
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

# Pinyto private key
PINYTO_KEY = RSA.construct((
    long(
        "3523388281094010930039840194958319359717825538249398805551827469668560894302332865345465783916264138897" +
        "1194487075907391212083797216356053906830272143344147059931946183066274310523736662148946074980706469510" +
        "6317511851649828802426144511321407267371613900315155373702173982644362916496126265649482466673875349489" +
        "9070479085121279149754328390162399923662717795499221033389116635575496225355070349703128875820317902210" +
        "6530888409720371972161617274765114279279705884523209156250037402461848192128376514645906747996382277955" +
        "1936787918661317227947726850380461998140456287231079109312171798861513513789080346324162225532044317709" +
        "2662200833191469956074281048646576909583449567985589286591276267789769136879220386308582946743785009694" +
        "0546719385368389141977397930633471243041532075499479657513692320825592500010883343220157357791351211360" +
        "71902337635746637864083449443988262746202666078634728101621385515109353596589585237881665906747589713"
    ),
    65537L,
    long(
        "1639735455900748178375804903279502273088387917002710889563616549809895284743292375193199359284771293107" +
        "1325081340543134900415884387427859745766869102522185716891593429414244876496848622847290161083228517022" +
        "0527093267548404389489866908697421634417721652800894744921438370243573385311073914007495235264861042761" +
        "2213705419781177259677846344812139671814591646897572997213300233227835190401294622365159081320775989401" +
        "7870700466857978625065677813759189244518837137463672951836987875444519717334255451536146510081285215114" +
        "8400446639283331452984755449502216943735706845743755423612274610002604911459743204874388081524614694316" +
        "7158680331173236504954186914631387690423597375352501726053828059156078643119936830919829866563740486336" +
        "6074963562322747508406061207317523742825220613311510788120050207542772490764443182668347329864982339075" +
        "216896694980659745402069075349829891850896836218346516190195982995688569661183509786427919295871473"
    )
))

# if manage.py test was called, use test settings
import sys
if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'test_sqlite.db'
        }
    }

    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
        'django.contrib.auth.hashers.SHA1PasswordHasher',
    )
