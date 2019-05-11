# coding=utf-8
"""
Pinyto cloud - A secure cloud database for your personal data
Copyright (C) 2105 Johannes Merkert <jonny@pinyto.de>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from project_path import project_path
import os

# Django settings for pinytoCloud project.

DEBUG = os.getenv('PINYTO_DEBUG_MODE', 'True') == 'True'
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('admin', 'pina@pinae.net'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': os.getenv('PINYTO_SQL_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('PINYTO_SQL_DB_NAME', project_path('management.sqlite')),
    }
}
dbuser = os.getenv('PINYTO_SQL_DB_USER')
if dbuser:
    DATABASES['default']['USER'] = dbuser
dbpass = os.getenv('PINYTO_SQL_DB_PASSWORD')
if dbpass:
    DATABASES['default']['PASSWORD'] = dbpass
dbhost = os.getenv('PINYTO_SQL_DB_HOST')
if dbhost:
    DATABASES['default']['HOST'] = dbhost
dbport = os.getenv('PINYTO_SQL_DB_PORT')
if dbport:
    DATABASES['default']['PORT'] = dbport

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = os.getenv('PINYTO_TIME_ZONE', 'Europe/Berlin')

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = os.getenv('PINYTO_LANGUAGE_CODE', 'de-DE')

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
STATIC_URL = '/webapps/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    project_path('webapps/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = os.getenv('PINYTO_SECRET_KEY', 'w_stpdw@im!72s2^%ad5wz5&9mfd8n#95mc3)bqj3qd%f*)ile')

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    #'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEST_RUNNER = 'django.test.runner.DiscoverRunner'

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = 'pinytoCloud.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'pinytoCloud.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.staticfiles',
    'corsheaders',
    'pinytoCloud',
    'keyserver',
    'database',
    'api_prototype',
    'service',
    'api.pinyto_DocumentsAdmin',
    'api.pinyto_Todo',
    'api.bborsalino_Librarian'
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
PINYTO_KEY_NUMBERS = {
    'e': 65537,
    'N': int("7829487815098536540163340882101624716263699124284776727331856400402012605068617607074848020780929263286" +
             "1777371795066320667094273729808501496067021755785325385319270032155555860380403694273039781832166222574" +
             "0982623746713760050717491720444401365859377904761509456912858624197383009910897359227163603168055069076" +
             "2988650388634810877021897370043618319224015852080391715109009180201275625896119513840827703345319162546" +
             "4956424352483465726648149599154639222100356593400640583898292902042777225273667494325059986268195514181" +
             "6261927004696811927915492285857001606967204165474930842200356404798932927527349880460038664735604799615" +
             "6575351492978859740957294904746191106691211687301808176923284964142198110073079545921504748367207486987" +
             "3816642503072179364939244345082744417171570594851345415294043745634023662066627610259775478034263984167" +
             "9047815006824885208959469459587070768606268964437819028000766288835526004124480298771987405845901023717" +
             "0023812712182602254669659406038944136636863318312128196609065625793814435451291091924867897181456040979" +
             "3979413614936337848290374830746444999167778857351617508196024135490271644440537219056271178956203994401" +
             "1689062773834284439722273182150964910834681668991726977737508228377398684622376557220679678700827641"),
    'd': int("2981768869143298800768067276139805778311879799853880133931608158713914775011178828066300437167877893134" +
             "5607846294964070639943939729042989286057292765958861960300039073081931103334520893622851212517341909901" +
             "6878790699821913378791489934702104363801886157818369997636267122409363909613898823396719049872155980119" +
             "2508563483985172416796459045408222372545466097808482182849470682647109851637109525091981913236733768375" +
             "0855965262578922151935718233140068058415899418873103564910165136367024379596342020398540857794343528670" +
             "2047414988635850418982296595247034547023733902468663486129647306214452399990160148716024612556814626733" +
             "1489440719712066780124858202960693626021629524066026661061829400465295571648678728444749604781609873673" +
             "8529007281981007017095712216813819011710931404555953034818233738113059659066244419285043849634481068525" +
             "3548143975603978845786291912874222286240491046109009648741143039959517361628409811549137506938675877055" +
             "8909917938217065976720935041307296168085769614486755994542304843416521502580322224752881715271940433727" +
             "7384485959780857017174141615009919866517007263376908920815476849112200774956701516227265221737241283102" +
             "7020315411534906194196468794693670289897898202328696975402304424196643752903680387357473470467053197"),
    'p': int("2821277970713918256048653007990231177110518360999568297215315451030363360922451608913412334666758452511" +
             "1231767195553918177762972592144688432451139940543706453445125045408142883446363940391681318039249387889" +
             "9221272410238606806443114434181311038598452999086448968431708381699736853293682785830961520024814297720" +
             "9104164160586732250719259907115910514339643158591742876498137338963654036798928174943691577974914582114" +
             "8986000053381002046288857365872191635434067115288149490215955208678017261355061029386428834997399368059" +
             "416941590368967060481355259604484905715581674284845198956697520843763711278109920579556872411927632983"),
    'q': int("2775156470355631661698656696517211110506504123228425869619020522366700242086552972424209878629417181679" +
             "6515984729601332139914064511928228335583511255023628470300794844552418038748153667692692982767178036683" +
             "5385710923639426908174507740243864566730406652900632789559526377061919865408148942186007993525515380029" +
             "1359534324755802993784902963717524213709750802839858501780177752358594148136294468880068656358181616098" +
             "8078780237523696871945421950758160302721429293815062393851347431707188631423196922126628255238016439274" +
             "834026673850207055391955940401743984200700398926835906053936304342481573073644612652761097269016903727")
}
PINYTO_PUBLIC_KEY = rsa.RSAPublicNumbers(
    PINYTO_KEY_NUMBERS['e'],
    PINYTO_KEY_NUMBERS['N']
).public_key(default_backend())
PINYTO_KEY = rsa.RSAPrivateNumbers(
    PINYTO_KEY_NUMBERS['p'],
    PINYTO_KEY_NUMBERS['q'],
    PINYTO_KEY_NUMBERS['d'],
    rsa.rsa_crt_dmp1(PINYTO_KEY_NUMBERS['e'], PINYTO_KEY_NUMBERS['p']),
    rsa.rsa_crt_dmq1(PINYTO_KEY_NUMBERS['e'], PINYTO_KEY_NUMBERS['q']),
    rsa.rsa_crt_iqmp(PINYTO_KEY_NUMBERS['p'], PINYTO_KEY_NUMBERS['q']),
    PINYTO_PUBLIC_KEY.public_numbers()
).private_key(default_backend())

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
