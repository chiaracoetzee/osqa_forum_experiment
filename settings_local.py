# encoding:utf-8
import os.path

this_dir = os.path.dirname(os.path.realpath(__file__))
subdomain = os.path.basename(this_dir)
if subdomain == 'osqatest':
   subdomain = 'test'

SITE_SRC_ROOT = os.path.dirname(__file__)
LOG_FILENAME = 'django.osqa.log'

#for logging
import logging
logging.basicConfig(
    filename=os.path.join(SITE_SRC_ROOT, 'log', LOG_FILENAME),
    level=logging.INFO,
    format='%(pathname)s TIME: %(asctime)s MSG: %(filename)s:%(funcName)s:%(lineno)d %(message)s',
)

#ADMINS and MANAGERS
ADMINS = ()
MANAGERS = ADMINS

DEBUG = False
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': True
}
TEMPLATE_DEBUG = DEBUG
INTERNAL_IPS = ('127.0.0.1','::1','10.243.45.194','fe80::1031:3bff:fe02:2e38',)


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': subdomain,
        'USER': subdomain,
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5433',
    }
}

if not subdomain.endswith('-a') and not subdomain.endswith('-b') and not subdomain == 'test':
  DATABASES.update({
    'a': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': subdomain + '-a',
        'USER': subdomain + '-a',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
    'b': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': subdomain + '-b',
        'USER': subdomain + '-b',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
  })

CACHE_BACKEND = 'memcached://localhost:11211/'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# This should be equal to your domain name, plus the web application context.
# This shouldn't be followed by a trailing slash.
# I.e., http://www.yoursite.com or http://www.hostedsite.com/yourhostapp
APP_URL = 'http://' + subdomain + '.moocforums.org'

#LOCALIZATIONS
TIME_ZONE = 'Etc/UTC'

#OTHER SETTINGS

USE_I18N = True
LANGUAGE_CODE = 'en'

DJANGO_VERSION = 1.1
OSQA_DEFAULT_SKIN = 'default'

DISABLED_MODULES = ['books', 'recaptcha', 'project_badges']
